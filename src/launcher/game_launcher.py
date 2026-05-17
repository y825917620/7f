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
        custom_name = f"SL10002_LANV45_10002_{os.getpid()}"
        return f'"{game_path}" /mapfile={self.map_id} MemoryMapName={custom_name}'

    def prepare(self) -> bool:
        """写 config.lua + 编译 map.o/edt2.o."""
        game_dir = self.game_dir

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
        """启动 HostService + 创建 PlatformBlock SHM + 启动游戏."""
        # 0. 启动本地 HostService
        from .host_service import HostService
        self._host = HostService(self.player_slot, self.player_name)
        self._host.start()
        time.sleep(0.2)  # 等端口就绪

        kernel32 = ctypes.windll.kernel32

        # 1. PlatformBlock
        block = build_platform_block(self.map_id, self.host_ip, self.host_port,
                                     self.player_name, self.player_slot, self.mode)
        custom_name = f"SL10002_LANV45_10002_{os.getpid()}"

        kernel32.CreateFileMappingA.restype = wintypes.HANDLE
        kernel32.MapViewOfFile.restype = ctypes.c_void_p
        kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        kernel32.UnmapViewOfFile.restype = wintypes.BOOL

        # 创建两个 SHM: "10002" 和自定义名
        for name in [b"10002", custom_name.encode("ascii")]:
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
                resolution_index: int = 0) -> tuple:
    bridge = GameBridge(game_dir, map_id, options, resolution_index)
    if not bridge.prepare():
        return None, "\n".join(bridge._prepare_errors)
    ok, err = bridge.launch()
    if not ok:
        return None, err
    return bridge, f"PID={bridge.process_id}"
