# -*- coding: utf-8 -*-
"""GameBridge — 统一向游戏注入启动参数与资源.

所有启动参数（命令行、共享内存、管道）必须来自 MapLaunchManifest，
不再硬编码任何地图 ID 或文件路径。
"""

import os
import ctypes
from ctypes import wintypes
import struct
import time
from pathlib import Path
from typing import Optional

from ..core.map_launch_manifest import MapLaunchManifest


class GameBridge:
    """接收 MapLaunchManifest，统一向游戏进程注入全部启动参数."""

    def __init__(self, manifest: MapLaunchManifest):
        if not manifest.is_valid():
            raise ValueError(f"Manifest 无效: {'; '.join(manifest.errors)}")
        self.manifest = manifest
        self.game_dir = manifest.game_dir
        self._handles = {}
        self._process_info = None

    def launch(self) -> bool:
        """执行完整启动流程.

        Returns:
            bool: 进程是否成功创建.
        """
        self._create_mutex()
        self._create_shared_memory()
        self._create_pipes()
        return self._create_process()

    # === 互斥体 ===

    def _create_mutex(self):
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateMutexA.restype = wintypes.HANDLE
        self._handles["mutex"] = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

    # === 共享内存 ===

    def _create_shared_memory(self):
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateFileMappingA.restype = wintypes.HANDLE
        kernel32.MapViewOfFile.restype = ctypes.c_void_p
        kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]

        map_id = self.manifest.map_id

        shm_configs = [
            (b"7fgame_game_client_start_info", 512, "uint32", map_id),
            (b"7fgame_game_client_login", 256, "string", b"localplayer"),
        ]

        self._handles["shm"] = []
        for name, size, kind, value in shm_configs:
            hMap = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, size, name)
            if not hMap:
                continue
            self._handles["shm"].append(hMap)
            ptr = kernel32.MapViewOfFile(hMap, 0xF001F, 0, 0, size)
            if not ptr:
                continue
            ctypes.memset(ptr, 0, size)
            if kind == "uint32":
                ctypes.c_uint32.from_address(ptr).value = value
            elif kind == "string":
                buf = (ctypes.c_char * size).from_address(ptr)
                buf.value = value
            kernel32.UnmapViewOfFile(ptr)

    # === 管道与 NUL ===

    def _create_pipes(self):
        kernel32 = ctypes.windll.kernel32
        kernel32.CreatePipe.argtypes = [
            ctypes.POINTER(wintypes.HANDLE), ctypes.POINTER(wintypes.HANDLE),
            ctypes.c_void_p, wintypes.DWORD
        ]
        kernel32.CreateFileA.restype = wintypes.HANDLE

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

        self._handles["pipe_read"] = hRead
        self._handles["pipe_write"] = hWrite
        self._handles["nul"] = hNul

    # === 创建进程 ===

    def _create_process(self) -> bool:
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateProcessA.restype = wintypes.BOOL

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
        si.hStdInput = self._handles["pipe_read"]
        si.hStdOutput = self._handles["nul"]
        si.hStdError = self._handles["nul"]

        game_path = self.game_dir / "core" / "game.exe"
        work_dir = str(self.game_dir)
        cmdline = f'"{game_path}" {self.manifest.map_id}'

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
            self._cleanup_handles()
            return False

        # 写入管道数据
        pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, self.manifest.map_id, 0)
        written = wintypes.DWORD(0)
        kernel32.WriteFile(self._handles["pipe_write"], pipe_data, len(pipe_data), ctypes.byref(written), None)

        self._process_info = {
            "pid": pi.dwProcessId,
            "tid": pi.dwThreadId,
            "hProcess": pi.hProcess,
            "hThread": pi.hThread,
        }

        # 关闭不需要的句柄
        kernel32.CloseHandle(pi.hThread)
        self._cleanup_handles()
        return True

    def _cleanup_handles(self):
        kernel32 = ctypes.windll.kernel32
        for key in ["pipe_read", "pipe_write", "nul"]:
            h = self._handles.pop(key, None)
            if h:
                kernel32.CloseHandle(h)

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


def launch_game(manifest: MapLaunchManifest) -> Optional[GameBridge]:
    """使用 manifest 启动游戏.

    Args:
        manifest: 已验证的 MapLaunchManifest

    Returns:
        GameBridge 实例（含进程句柄），失败返回 None.
    """
    try:
        bridge = GameBridge(manifest)
        if bridge.launch():
            return bridge
        return None
    except Exception:
        return None
