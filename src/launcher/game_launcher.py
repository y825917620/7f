# -*- coding: utf-8 -*-
"""GameBridge — 基于 SL10002 FinalLauncher C# 参考实现."""

import ctypes
from ctypes import wintypes
import os
import struct
import socket
import threading
import subprocess
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.config_generator import generate_config_lua, generate_edt2_lua, generate_map_opt_lua
from ..core.map_launch_manifest import MapLaunchManifest
from ..data.map_data import DEFAULT_MAP_OPTIONS


def _find_luac(game_dir: Path) -> Optional[Path]:
    candidates = [
        game_dir.parent / "lua51_bin" / "luac5.1.exe",
        Path(__file__).parent.parent.parent / "lua51_bin" / "luac5.1.exe",
    ]
    for c in candidates:
        if c and c.exists():
            return c.resolve()
    return None


def _mirror_sanguo_resources(game_dir: Path) -> Optional[str]:
    src_root = game_dir / "resource" / "sanguo"
    dst_root = game_dir / "core" / "resource" / "sanguo"
    if not src_root.exists():
        return None

    copied = 0
    for src in src_root.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            if (not dst.exists()) or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)
                copied += 1
        except Exception:
            continue
    return f"resource_mirror copied={copied}"


def _looks_like_usable_dds(path: Path) -> bool:
    try:
        if not path.exists() or not path.is_file():
            return False
        if path.stat().st_size < 16384:
            return False
        with open(path, "rb") as f:
            return f.read(4) == b"DDS "
    except Exception:
        return False


def _read_tga_bgra(path: Path):
    try:
        if not path.exists():
            return None
        data = path.read_bytes()
        if len(data) < 18:
            return None

        id_len = data[0]
        color_map_type = data[1]
        image_type = data[2]
        if color_map_type != 0 or image_type != 2:
            return None

        width = data[12] | (data[13] << 8)
        height = data[14] | (data[15] << 8)
        bpp = data[16]
        desc = data[17]
        if width <= 0 or height <= 0:
            return None
        if bpp not in (24, 32):
            return None

        bytes_per_pixel = bpp // 8
        off = 18 + id_len
        need = width * height * bytes_per_pixel
        if off < 0 or off + need > len(data):
            return None

        bgra = bytearray(width * height * 4)
        top_origin = (desc & 0x20) != 0
        for y in range(height):
            src_y = y if top_origin else (height - 1 - y)
            src_base = off + src_y * width * bytes_per_pixel
            dst_base = y * width * 4
            for x in range(width):
                si = src_base + x * bytes_per_pixel
                di = dst_base + x * 4
                bgra[di + 0] = data[si + 0]
                bgra[di + 1] = data[si + 1]
                bgra[di + 2] = data[si + 2]
                bgra[di + 3] = data[si + 3] if bytes_per_pixel == 4 else 255
        return width, height, bytes(bgra)
    except Exception:
        return None


def _write_dds_a8r8g8b8(path: Path, width: int, height: int, bgra: bytes) -> bool:
    try:
        if width <= 0 or height <= 0 or not bgra or len(bgra) < width * height * 4:
            return False
        header = bytearray(128)
        header[0:4] = b"DDS "
        struct.pack_into("<I", header, 4, 124)
        struct.pack_into("<I", header, 8, 0x0002100F)    # CAPS|HEIGHT|WIDTH|PITCH|PIXELFORMAT
        struct.pack_into("<I", header, 12, height)
        struct.pack_into("<I", header, 16, width)
        struct.pack_into("<I", header, 20, width * 4)
        struct.pack_into("<I", header, 76, 32)
        struct.pack_into("<I", header, 80, 0x00000041)   # RGB | ALPHAPIXELS
        struct.pack_into("<I", header, 88, 32)
        struct.pack_into("<I", header, 92, 0x00FF0000)   # R
        struct.pack_into("<I", header, 96, 0x0000FF00)   # G
        struct.pack_into("<I", header, 100, 0x000000FF)  # B
        struct.pack_into("<I", header, 104, 0xFF000000)  # A
        struct.pack_into("<I", header, 108, 0x00001000)  # DDSCAPS_TEXTURE

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(header)
            f.write(bgra[:width * height * 4])
        return True
    except Exception:
        return False


def _repair_ui_dds_from_tga(game_dir: Path) -> list[str]:
    ui_dir = game_dir / "resource" / "sanguo" / "ui"
    repaired = []
    if not ui_dir.exists():
        return repaired
    for dds in sorted(ui_dir.glob("*.dds")):
        if _looks_like_usable_dds(dds):
            continue
        tga = dds.with_suffix(".tga")
        if not tga.exists():
            tga = dds.with_suffix(".TGA")
        parsed = _read_tga_bgra(tga)
        if not parsed:
            continue
        width, height, bgra = parsed
        if _write_dds_a8r8g8b8(dds, width, height, bgra):
            repaired.append(dds.name)
    return repaired


def _ensure_effect_aliases(game_dir: Path) -> list[str]:
    effect_dir = game_dir / "resource" / "sanguo" / "effect"
    aliases = []
    if not effect_dir.exists():
        return aliases

    alias_map = {
        "zzfire11.tga": "yfire.tga",
        "bomb05.tga": "bomb3002.TGA",
        "tengman.tga": "tengman1.tga",
    }
    for dst_name, src_name in alias_map.items():
        dst = effect_dir / dst_name
        if dst.exists():
            continue
        src = effect_dir / src_name
        if not src.exists():
            continue
        shutil.copy2(src, dst)
        aliases.append(dst.name)
    return aliases


def _ensure_model_aliases(game_dir: Path) -> list[str]:
    model_dir = game_dir / "resource" / "sanguo" / "model"
    aliases = []
    if not model_dir.exists():
        return aliases

    required = (
        "CliffTransAAHL0.lmo",
        "CliffTransAALH0.lmo",
        "CliffTransAHLA0.lmo",
        "CliffTransALHA0.lmo",
        "CliffTransHAAL0.lmo",
        "CliffTransHLAA0.lmo",
        "CliffTransLAAH0.lmo",
        "CliffTransLHAA0.lmo",
    )
    required_lower = {name.lower() for name in required}

    src = None
    for candidate in sorted(model_dir.glob("CliffTrans*.lmo")):
        if candidate.name.lower() not in required_lower:
            src = candidate
            break
    if src is None:
        for candidate in sorted(model_dir.glob("*.lmo")):
            src = candidate
            break
    if src is None:
        return aliases

    for name in required:
        dst = model_dir / name
        if dst.exists():
            continue
        shutil.copy2(src, dst)
        aliases.append(dst.name)
    return aliases


def _ensure_terrain_aliases(game_dir: Path) -> list[str]:
    terrain_dir = game_dir / "resource" / "sanguo" / "terrain"
    aliases = []
    if not terrain_dir.exists():
        return aliases
    for src in terrain_dir.glob("*.tga"):
        stem = src.stem
        if stem.endswith("_nor"):
            continue
        dst = terrain_dir / f"{stem}_nor.tga"
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        aliases.append(dst.name)
    return aliases


# === PlatformBlock SHM (匹配 C# BuildPlatformBlock) ===

def _write_ascii(buf: bytearray, offset: int, text: str, maxlen: int):
    b = text.encode("ascii", errors="replace")[:maxlen]
    buf[offset:offset+len(b)] = b


def _write_wide(buf: bytearray, offset: int, text: str, maxlen: int):
    """UTF-16LE 宽字符串写入."""
    b = text.encode("utf-16-le", errors="replace")[:maxlen]
    buf[offset:offset+len(b)] = b


def build_platform_block(map_id: int, host_ip: str, host_port: int,
                         player_name: str, player_slot: int, mode: str) -> bytes:
    """构建 0x435 字节平台数据块 (匹配 C# BuildPlatformBlock)."""
    size = 0x435
    buf = bytearray(size)

    struct.pack_into("<H", buf, 0x00, 1)  # version
    _write_wide(buf, 0x02, str(map_id), 0x40)  # MapNameWide

    # Host IP
    parts = host_ip.split(".")
    for i, p in enumerate(parts[:4]):
        buf[0x42 + i] = int(p) & 0xFF

    struct.pack_into("<H", buf, 0x46, host_port)
    zero_pos = max(0, min(23, player_slot - 1))
    buf[0x48] = zero_pos
    buf[0x49] = 0
    struct.pack_into("<I", buf, 0x4A, 1)  # HostSrvSessionId
    struct.pack_into("<I", buf, 0x4E, 100000 + player_slot)
    _write_wide(buf, 0x52, player_name, 0x20)
    struct.pack_into("<I", buf, 0x72, zero_pos)
    _write_wide(buf, 0x284, "SL10002", 0x60)
    buf[0x2E4] = 0
    _write_ascii(buf, 0x2E5, mode.lower(), 0x10)
    for off in [0x2F5, 0x2F9, 0x2FD, 0x305, 0x349]:
        struct.pack_into("<I", buf, off, 0)
    _write_wide(buf, 0x309, "", 0x20)
    _write_wide(buf, 0x329, "", 0x20)
    _write_wide(buf, 0x34D, "", 0x44)
    struct.pack_into("<I", buf, 0x391, map_id)
    struct.pack_into("<I", buf, 0x427, 1)

    return bytes(buf)


# === config.lua 生成 (匹配 PowerShell Write-SL10002ConfigLuaV45) ===

def write_config_lua_v45(game_dir: Path, map_id: int, control_id: int = 1, options: list = None):
    """生成带本地会话钩子的 config.lua."""
    if options is None:
        options = [1, 0, 0, -1, -1, -1, -1, -1, -1, -1]

    pairs = [f"{{{i} , {options[i]}}}" for i in range(10)]
    values = [str(options[i]) for i in range(10)]

    lua_lines = [
        "-- SL10002 V45 config.lua",
        "local function __sl_log(m) pcall(function()",
        "  local f=io.open('SL10002_map_protocol_v45.log','a')",
        "  if f then f:write(os.date('%Y-%m-%d %H:%M:%S')..' '..tostring(m)..'\\n');f:close() end",
        "end) end",
        f"function helper_get004() return {{{map_id},1,1,{control_id}}} end",
        f"function helper_get005() return {{{','.join(values)}}} end",
        f"tempConfigLuaMapOptionInfo = {{ {','.join(pairs)},}}",
        f"if type(SetCurrentControlID)=='function' then SetCurrentControlID({control_id}) end",
        "function GetMapOptionInfo() return tempConfigLuaMapOptionInfo end",
        f"function helper_get006() return '{map_id}' end",
        "function GetMapOptionDisplay() return 1 end",
        "function SrvScriptInfo(a,b) return 1 end",
        "function load_rolesdk(mapid,data) return 1 end",
        "local __sl_targets = {'map_init','GameEvent_MapInit','GameEventJoinGame','GameEvent_GameStart','GameEvent_StartGame','GameEvent_RunGameLogic','GameEvent_GameLogic','TgrMainTimer','CustomEventTimer','TriggerAddChaFromCoordinate','tgr_GetSideBirthPoint','GetSessionPlayerInfo','GetSessionPlayerInfoEx','AddCha','lua_sceAddCha','sceAddCha','lua_AddCha_New','lua_AddCha_NewEx','lua_AddCha_NewEx_Use_ContrlID','AddSceneObj','AddSceneObject','sceAddSceneObject','map_addchar','map_addsceneobj','player_station','player_mode_station','player_bar_station','tgr_map_init','tgr_maptab_init','map_init_0000','map_init_0004','map_init_allregion','lua_AddTimer','AddTimer','lua_EnableTimer','lua_EnableAllTimer'}",
        "local __sl_wrapped = {}",
        "local function __sl_args(...) local n=select('#',...); local t={}; for i=1,n do t[#t+1]=tostring(select(i,...)) end; return table.concat(t,',') end",
        "local function __sl_addcha_log(m) pcall(function() local f=io.open('AddCha.log','a'); if f then f:write(os.date('%Y-%m-%d %H:%M:%S')..' '..tostring(m)..'\\n'); f:close() end end) end",
        "local function __sl_wrap(name, fn)",
        "  if type(fn)~='function' or __sl_wrapped[name] then return fn end",
        "  __sl_wrapped[name]=true",
        "  return function(...)",
        "    local a=__sl_args(...)",
        "    __sl_log('[CHAIN_BEGIN] '..name..' args='..a)",
        "    if name=='AddCha' or name=='lua_sceAddCha' or name=='lua_AddCha_New' or name=='lua_AddCha_NewEx' or name=='lua_AddCha_NewEx_Use_ContrlID' then __sl_addcha_log('[CALL] '..name..'('..a..')') end",
        "    local r={pcall(fn,...)}",
        "    __sl_log('[CHAIN_END] '..name..' ok='..tostring(r[1])..' r1='..tostring(r[2]))",
        "    if not r[1] then error(r[2]) end",
        "    return unpack(r,2)",
        "  end",
        "end",
        "local function __sl_install_now() for _,n in ipairs(__sl_targets) do local f=rawget(_G,n); if type(f)=='function' then rawset(_G,n,__sl_wrap(n,f)); __sl_log('[CHAIN_WRAP_NOW] '..n) else __sl_log('[CHAIN_WAIT] '..n) end end end",
        "pcall(__sl_install_now)",
        "pcall(function() local mt=getmetatable(_G) or {}; local old=mt.__newindex; mt.__newindex=function(t,k,v) if type(k)=='string' and type(v)=='function' then for _,n in ipairs(__sl_targets) do if k==n then __sl_log('[CHAIN_WRAP_FUTURE] '..k); v=__sl_wrap(k,v); break end end end; if old then return old(t,k,v) end; return rawset(t,k,v) end; setmetatable(_G,mt) end)",
        "__sl_log('[CHAIN_BOOT] passive map-chain diagnostics installed')",
        "local function __sl_block_exit(name)",
        "  rawset(_G,'__SL_REAL_EXIT_'..name,rawget(_G,name))",
        "  rawset(_G,name,function(...) __sl_log('[BLOCK_EXIT] '..name..' args='..__sl_args(...)); return nil end)",
        "end",
        "__sl_block_exit('appExit')",
        "__sl_block_exit('close_net')",
        "__sl_block_exit('CloseNet')",
        "__sl_block_exit('CloseNetwork')",
        "__sl_block_exit('GameEventCloseWindow')",
        "__sl_block_exit('GameEventCloseNet')",
        "__sl_block_exit('NotifyOffline')",
        "local __sl_raw_SetCliffTex = SetCliffTex",
        "function SetCliffTex(obj, tex)",
        "  if obj == nil then __sl_log('skip SetCliffTex nil obj '..tostring(tex)); return 0 end",
        "  if type(__sl_raw_SetCliffTex)=='function' then return __sl_raw_SetCliffTex(obj, tex) end",
        "  return 0",
        "end",
        f"function SL10002_RuntimeProtocolInfo() return {{mapid={map_id},control_id={control_id},mode='lan',vip=0,sponsor=0}} end",
    ]

    config_path = game_dir / "config.lua"
    config_path.write_text("\n".join(lua_lines), encoding="ascii")
    return config_path


# === GameBridge ===

class GameBridge:
    def __init__(self, game_dir: Path, map_id: int, options: list,
                 resolution_index: int = 0, player_slot: int = 1,
                 mode: str = "single", host_ip: str = "127.0.0.1",
                 host_port: int = 29002, player_name: str = "Player1"):
        self.game_dir = Path(game_dir)
        self.map_id = int(map_id)
        self.options = list(options) if options else [1, 0, 0, -1, -1, -1, -1, -1, -1, -1]
        self.resolution_index = resolution_index
        self.player_slot = player_slot
        self.mode = mode
        self.host_ip = host_ip
        self.host_port = host_port
        self.player_name = player_name
        self._handles = {}
        self._process_info = None
        self._prepare_errors = []

    def _build_cmdline(self, game_path: Path) -> str:
        # Avoid editor-path side effects from /mapfile= which can trigger
        # lua_SetCliffTex parameter errors during object loading.
        return f'"{game_path}" {self.map_id} MemoryMapName=sanguo'

    def prepare(self) -> bool:
        """写 config.lua + 编译 map.o/edt2.o."""
        game_dir = self.game_dir

        _repair_ui_dds_from_tga(game_dir)
        _ensure_effect_aliases(game_dir)
        _ensure_model_aliases(game_dir)
        _ensure_terrain_aliases(game_dir)
        _mirror_sanguo_resources(game_dir)

        # 1. V45 config.lua
        write_config_lua_v45(game_dir, self.map_id, self.player_slot, self.options)

        # 2. 编译 map.o
        luac_path = _find_luac(game_dir)
        if luac_path:
            try:
                g_map_display = 1
                g_map_opt = {}
                for opt_id, values in DEFAULT_MAP_OPTIONS.items():
                    if len(values) == 11:
                        g_map_opt[opt_id] = list(values)
                map_offset = self.map_id - 10000
                vals = self.options
                if len(vals) == 11:
                    g_map_opt[map_offset] = list(vals)
                lua_src = generate_map_opt_lua(g_map_display, g_map_opt)
                tmp = game_dir / "map_tmp.lua"
                tmp.write_text(lua_src, encoding="gbk")
                subprocess.run([str(luac_path), "-s", "-o", str(game_dir / "map.o"), str(tmp)],
                             capture_output=True, timeout=10)
                tmp.unlink(missing_ok=True)
            except Exception as e:
                self._prepare_errors.append(f"map.o 编译: {e}")

            # edt2.o
            try:
                edt2_lua = generate_edt2_lua(self.map_id, self.options, display=1, game_dir=game_dir)
                tmp = game_dir / "edt2_tmp.lua"
                tmp.write_text(edt2_lua, encoding="gbk")
                subprocess.run([str(luac_path), "-s", "-o", str(game_dir / "core" / "edt2.o"), str(tmp)],
                             capture_output=True, timeout=10)
                tmp.unlink(missing_ok=True)
            except Exception as e:
                self._prepare_errors.append(f"edt2.o 编译: {e}")

        return len(self._prepare_errors) == 0

    def launch(self) -> tuple:
        """V49: 清端口 → HostService → 弹窗监控 → 确认监听 → SHM → CreateProcess."""
        # 0a. 清理旧进程和端口 (V49)
        try:
            import subprocess
            subprocess.run(["taskkill", "/F", "/IM", "game.exe"], capture_output=True, timeout=5)
            for line in subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True, timeout=5
            ).stdout.splitlines():
                if ":29002" in line and "LISTENING" in line:
                    subprocess.run(["taskkill", "/F", "/PID", line.strip().split()[-1]], capture_output=True, timeout=3)
        except Exception:
            pass
        time.sleep(0.5)

        # 0b. 启动弹窗监控线程 (模仿原版 _dialog_watcher_thread)
        import threading
        def _close_dialogs():
            import ctypes as ct
            u32 = ct.windll.user32
            start = time.time()
            titles = [b"LOG", b"Error", b"Fatal", b"Warning", b"Assertion"]
            while time.time() - start < 120:
                for t in titles:
                    h = u32.FindWindowA(b"#32770", t)
                    if h:
                        u32.ShowWindow(h, 0)
                        u32.PostMessageA(h, 0x0010, 0, 0)
                time.sleep(0.15)

        threading.Thread(target=_close_dialogs, daemon=True).start()

        # 0c. 启动本地 HostService
        from .host_service import HostService
        self._host = HostService(
            player_slot=self.player_slot,
            player_name=self.player_name,
            host_ip="127.0.0.1",
            host_port=self.host_port,
        )
        self._host.start()
        if not self._host.wait_until_ready(timeout=3.0):
            return False, f"HostService TCP {self.host_port} 监听失败，中止启动"

        kernel32 = ctypes.windll.kernel32

        # 1. PlatformBlock (V49: 记录端口字段)
        block = build_platform_block(self.map_id, self.host_ip, self.host_port,
                                     self.player_name, self.player_slot, self.mode)
        custom_name = f"SL10002_LANV45_10002_{os.getpid()}"
        # V49 日志: 确认 MemoryMap 端口字段
        port_in_block = struct.unpack_from("<H", block, 0x46)[0]
        try:
            with open(self.game_dir / "SL10002_ONE_LOG.txt", "a", encoding="utf-8") as f:
                f.write(f"[V49] PlatformBlock HostSrvPort=0x{port_in_block:04X} ({port_in_block}) MemoryMapName={custom_name}\n")
        except Exception:
            pass

        kernel32.CreateFileMappingA.restype = wintypes.HANDLE
        kernel32.MapViewOfFile.restype = ctypes.c_void_p
        kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        kernel32.UnmapViewOfFile.restype = wintypes.BOOL

        # 创建多个 SHM 别名，兼容不同启动链路:
        # - custom_name: 当前桥接链路
        # - sanguo: 旧链路与外部脚本常用名称
        # - "10002": 历史实验工具读取
        shm_names = [b"10002", b"sanguo", custom_name.encode("ascii")]
        for name in shm_names:
            h = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0,
                                            len(block), name)
            if h:
                p = kernel32.MapViewOfFile(h, 0xF001F, 0, 0, len(block))
                if p:
                    ctypes.memmove(p, block, len(block))
                    kernel32.UnmapViewOfFile(p)
                self._handles["shm_" + name.decode("ascii", errors="replace")] = h

        # 2. 互斥体
        kernel32.CreateMutexA.restype = wintypes.HANDLE
        self._handles["mutex"] = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

        # 3. CreateProcess — 匹配 C# Process.Start
        game_path = self.game_dir / "core" / "game.exe"
        if not game_path.exists():
            game_path = self.game_dir / "game.exe"

        class SI(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("a", wintypes.LPSTR), ("b", wintypes.LPSTR),
                ("c", wintypes.LPSTR), ("d", wintypes.DWORD), ("e", wintypes.DWORD),
                ("f", wintypes.DWORD), ("g", wintypes.DWORD), ("h", wintypes.DWORD),
                ("i", wintypes.DWORD), ("j", wintypes.DWORD), ("k", wintypes.DWORD),
                ("l", wintypes.WORD), ("m", wintypes.WORD), ("n", wintypes.LPBYTE),
                ("o", wintypes.HANDLE), ("p", wintypes.HANDLE), ("q", wintypes.HANDLE),
            ]
        class PI(ctypes.Structure):
            _fields_ = [("hp", wintypes.HANDLE), ("ht", wintypes.HANDLE),
                        ("pid", wintypes.DWORD), ("tid", wintypes.DWORD)]

        si = SI()
        si.cb = ctypes.sizeof(si)
        cmdline = self._build_cmdline(game_path)
        os.environ["PATH"] = str(self.game_dir / "core") + os.pathsep + os.environ.get("PATH", "")

        pi = PI()
        ok = kernel32.CreateProcessA(
            str(game_path).encode("mbcs"), cmdline.encode("mbcs"),
            None, None, False, 0, None,
            str(self.game_dir).encode("mbcs"),
            ctypes.byref(si), ctypes.byref(pi)
        )

        if not ok:
            return False, f"CreateProcessA 失败 (err={kernel32.GetLastError()})"

        self._process_info = {"pid": pi.pid, "tid": pi.tid, "hProcess": pi.hp}
        kernel32.CloseHandle(pi.ht)
        return True, ""

    @property
    def process_id(self):
        return self._process_info["pid"] if self._process_info else None

    @property
    def process_handle(self):
        return self._process_info["hProcess"] if self._process_info else None


def launch_game(game_dir: Path, map_id: int, options: list,
                resolution_index: int = 0, mode: str = "single",
                host_ip: str = "127.0.0.1", host_port: int = 29002,
                player_name: str = "Player1", player_slot: int = 1) -> tuple:
    bridge = GameBridge(game_dir, map_id, options, resolution_index,
                       player_slot, mode, host_ip, host_port, player_name)
    if not bridge.prepare():
        return None, "\n".join(bridge._prepare_errors)
    ok, err = bridge.launch()
    if not ok:
        return None, err
    return bridge, f"PID={bridge.process_id}"
