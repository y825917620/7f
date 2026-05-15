# -*- coding: utf-8 -*-
"""GameBridge — 移植自原启动器的完整启动逻辑.

原启动器 launch_game 流程:
  1. 生成 config.lua
  2. 找到 luac5.1 编译器
  3. 编译 edt2.o (Lua 源码 -> 字节码)
  4. 编译 map.o (从当前选项动态生成)
  5. 更新 GameSetting.inf
  6. 解压 .sl -> sl/map.map (虚拟文件系统)
  7. 创建互斥体 + 共享内存
  8. CreateProcessA + 管道数据
"""

import ctypes
from ctypes import wintypes
import lzma
import os
import struct
import subprocess
import time
from pathlib import Path
from typing import Optional

from ..core.config_generator import generate_config_lua, generate_edt2_lua, generate_map_opt_lua
from ..data.map_data import DEFAULT_MAP_OPTIONS


# === Lua 编译器 ===

def _find_luac(game_dir: Path) -> Optional[Path]:
    """找到 luac5.1.exe 编译器."""
    candidates = [
        game_dir.parent / "lua51_bin" / "luac5.1.exe",
        game_dir.parent.parent / "lua51_bin" / "luac5.1.exe" if game_dir.parent.parent else None,
        Path(__file__).parent.parent.parent / "lua51_bin" / "luac5.1.exe",
    ]
    for c in candidates:
        if c and c.exists():
            return c.resolve()
    return None


def _compile_edt2(config_lua: str, output_path: Path, luac_path: Path) -> bool:
    """将生成的 Lua 源码编译为 edt2.o 字节码."""
    try:
        tmp_path = output_path.with_suffix(".lua")
        tmp_path.write_text(config_lua, encoding="utf-8")
        result = subprocess.run(
            [str(luac_path), "-o", str(output_path), str(tmp_path)],
            capture_output=True, text=True, timeout=10
        )
        tmp_path.unlink(missing_ok=True)
        return result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0
    except Exception:
        return False


def _compile_map_o(game_dir: Path, luac_path: Path,
                   current_options: dict, selected_map: int) -> bool:
    """从当前选项动态编译 map.o.

    原启动器逻辑: 遍历 DEFAULT_MAP_OPTIONS，用 current_options 覆盖，
    然后编译为 map.o 字节码。
    """
    try:
        g_map_display = 0
        g_map_opt = {}
        for offset, values in DEFAULT_MAP_OPTIONS.items():
            if current_options and offset in current_options:
                g_map_opt[offset] = list(current_options[offset])
            else:
                g_map_opt[offset] = list(values)

        lua_src = generate_map_opt_lua(g_map_display, g_map_opt)
        tmp_path = game_dir / "map_tmp.lua"
        tmp_path.write_text(lua_src, encoding="utf-8")

        map_o_path = game_dir / "map.o"
        result = subprocess.run(
            [str(luac_path), "-o", str(map_o_path), str(tmp_path)],
            capture_output=True, text=True, timeout=10
        )
        tmp_path.unlink(missing_ok=True)
        return result.returncode == 0 and map_o_path.exists() and map_o_path.stat().st_size > 0
    except Exception:
        return False


def _ensure_sl_map(game_dir: Path, map_id: int) -> bool:
    """从 map/{map_id}.sl 解压生成 sl/map.map (虚拟文件系统).

    原启动器会在启动游戏前检查 sl/map.map 是否存在，
    若不存在则从对应的 .sl 文件解压生成。
    游戏将 sl/map.map 作为虚拟文件系统，从中读取 map/sanguo/sanguo.o 等资源。
    """
    try:
        sl_dir = game_dir / "sl"
        sl_dir.mkdir(exist_ok=True)
        map_map = sl_dir / "map.map"

        sl_file = game_dir / "map" / f"{map_id}.sl"
        if not sl_file.exists():
            return False

        data = sl_file.read_bytes()
        decompressed = lzma.decompress(data)
        map_map.write_bytes(decompressed)
        return True
    except Exception:
        return False


# === GameBridge ===

class GameBridge:
    """接收地图参数，执行完整启动流程."""

    def __init__(self, game_dir: Path, map_id: int,
                 options: list, resolution_index: int = 0):
        self.game_dir = Path(game_dir)
        self.map_id = int(map_id)
        self.options = list(options)
        self.resolution_index = resolution_index
        self._handles = {}
        self._process_info = None

    def prepare(self) -> bool:
        """准备所有资源（config.lua, map.o, GameSetting.inf, sl/map.map）.

        注意: edt2.o 不重新编译 — 原启动器使用预编译的 edt2.o。
        """
        game_dir = self.game_dir

        # 1. 生成并写入 config.lua
        config_lua = generate_config_lua(self.map_id, self.options, game_dir=game_dir)
        (game_dir / "config.lua").write_text(config_lua, encoding="gbk")

        # 2. 找到 lua 编译器
        luac_path = _find_luac(game_dir)

        # 3. 编译 map.o (从当前选项动态生成)
        if luac_path:
            map_offset = self.map_id - 10000
            current_options = {map_offset: self.options} if self.options else {}
            _compile_map_o(game_dir, luac_path, current_options, self.map_id)

        # 4. 更新 GameSetting.inf
        from .game_settings import update_game_setting
        update_game_setting(game_dir, self.resolution_index)

        # 5. 解压 sl/map.map (虚拟文件系统)
        _ensure_sl_map(game_dir, self.map_id)

        return True

    def launch(self) -> bool:
        """创建游戏进程."""
        kernel32 = ctypes.windll.kernel32

        # 互斥体
        kernel32.CreateMutexA.restype = wintypes.HANDLE
        self._handles["mutex"] = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

        # 共享内存: start_info
        kernel32.CreateFileMappingA.restype = wintypes.HANDLE
        kernel32.MapViewOfFile.restype = ctypes.c_void_p
        kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        kernel32.UnmapViewOfFile.restype = wintypes.BOOL

        hStart = kernel32.CreateFileMappingA(
            wintypes.HANDLE(-1), None, 0x04, 0, 512,
            b"7fgame_game_client_start_info"
        )
        if hStart:
            ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
            if ptr:
                ctypes.memset(ptr, 0, 512)
                ctypes.c_uint32.from_address(ptr).value = self.map_id
                kernel32.UnmapViewOfFile(ptr)
        self._handles["shm_start"] = hStart

        # 共享内存: login
        hLogin = kernel32.CreateFileMappingA(
            wintypes.HANDLE(-1), None, 0x04, 0, 256,
            b"7fgame_game_client_login"
        )
        if hLogin:
            ptr = kernel32.MapViewOfFile(hLogin, 0xF001F, 0, 0, 256)
            if ptr:
                ctypes.memset(ptr, 0, 256)
                buf = (ctypes.c_char * 256).from_address(ptr)
                buf.value = b"localplayer"
                kernel32.UnmapViewOfFile(ptr)
        self._handles["shm_login"] = hLogin

        # 管道
        class SECURITY_ATTRIBUTES(ctypes.Structure):
            _fields_ = [
                ("nLength", wintypes.DWORD),
                ("lpSecurityDescriptor", wintypes.LPVOID),
                ("bInheritHandle", wintypes.BOOL)
            ]

        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(sa)
        sa.bInheritHandle = True

        hRead = wintypes.HANDLE()
        hWrite = wintypes.HANDLE()
        kernel32.CreatePipe(ctypes.byref(hRead), ctypes.byref(hWrite), ctypes.byref(sa), 0)

        GENERIC_WRITE = 0x40000000
        OPEN_EXISTING = 3
        hNul = kernel32.CreateFileA(b"NUL", GENERIC_WRITE, 3, None, OPEN_EXISTING, 0x80, None)

        # STARTUPINFO
        class STARTUPINFOA(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("lpReserved", wintypes.LPSTR),
                ("lpDesktop", wintypes.LPSTR), ("lpTitle", wintypes.LPSTR),
                ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
                ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
                ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
                ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
                ("lpReserved2", wintypes.LPBYTE), ("hStdInput", wintypes.HANDLE),
                ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE),
            ]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
                ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)
            ]

        si = STARTUPINFOA()
        si.cb = ctypes.sizeof(si)
        si.dwFlags = 0x101
        si.wShowWindow = 1
        si.hStdInput = hRead
        si.hStdOutput = hNul
        si.hStdError = hNul

        game_path = self.game_dir / "core" / "game.exe"
        if not game_path.exists():
            game_path = self.game_dir / "game.exe"
        work_dir = str(self.game_dir)
        cmdline = f'"{game_path}" {self.map_id}'

        os.environ["PATH"] = str(self.game_dir / "core") + os.pathsep + os.environ.get("PATH", "")

        pi = PROCESS_INFORMATION()
        ok = kernel32.CreateProcessA(
            str(game_path).encode("mbcs"),
            cmdline.encode("mbcs"),
            None, None, True, 0, None,
            work_dir.encode("mbcs"),
            ctypes.byref(si), ctypes.byref(pi)
        )

        if not ok:
            err = kernel32.GetLastError()
            kernel32.CloseHandle(hRead)
            kernel32.CloseHandle(hWrite)
            if hNul:
                kernel32.CloseHandle(hNul)
            raise RuntimeError(f"CreateProcessA 失败 (错误码: {err})")

        kernel32.CloseHandle(hRead)

        # 管道数据
        pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, self.map_id, 0)
        written = wintypes.DWORD(0)
        kernel32.WriteFile(hWrite, pipe_data, len(pipe_data), ctypes.byref(written), None)
        kernel32.CloseHandle(hWrite)
        if hNul:
            kernel32.CloseHandle(hNul)

        self._process_info = {
            "pid": pi.dwProcessId,
            "tid": pi.dwThreadId,
            "hProcess": pi.hProcess,
        }
        kernel32.CloseHandle(pi.hThread)
        return True

    @property
    def process_id(self) -> Optional[int]:
        if self._process_info:
            return self._process_info["pid"]
        return None

    @property
    def process_handle(self):
        if self._process_info:
            return self._process_info["hProcess"]
        return None


def launch_game(game_dir: Path, map_id: int, options: list,
                resolution_index: int = 0) -> Optional[GameBridge]:
    """启动游戏的便捷入口."""
    bridge = GameBridge(game_dir, map_id, options, resolution_index)
    bridge.prepare()
    bridge.launch()
    return bridge
