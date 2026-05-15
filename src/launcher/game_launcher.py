# -*- coding: utf-8 -*-
"""GameBridge — 统一向游戏注入启动参数与资源."""

import os
import ctypes
from ctypes import wintypes
import struct
import time
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox

from ..core.map_catalog import MapCatalog
from ..core.resource_mount_manager import ResourceMountManager
from ..launcher.log_verifier import LogVerifier


def launch_game(parent, selected_map, game_dir, *args):
    """启动游戏主入口.

    Args:
        parent: UI 父窗口（用于显示消息框和保持句柄存活）
        selected_map: 用户选择的地图 ID（int）
        game_dir: 游戏根目录（Path 或 str）
        *args: 兼容旧接口的额外参数（options, resolution_index 等）

    Returns:
        bool: 进程是否成功创建（不保证地图加载成功）
    """
    try:
        abs_game_dir = Path(game_dir).absolute()

        # 0. 地图 ID 校验
        if selected_map is None:
            QMessageBox.warning(parent, "提示", "请先选择一张地图")
            return False

        mid_val = int(selected_map)

        # 1. 地图资源准备（使用 ResourceMountManager）
        catalog = MapCatalog(abs_game_dir)
        info = catalog.get_info(mid_val)
        if info is None:
            QMessageBox.critical(parent, "启动错误", f"未找到地图 {mid_val} 的资源文件")
            return False

        diag = catalog.diagnose(mid_val)
        if diag:
            QMessageBox.critical(parent, "启动错误", diag)
            return False

        mount_mgr = ResourceMountManager(abs_game_dir)
        manifest = mount_mgr.prepare(mid_val, info["sl_path"])
        if not manifest.is_valid():
            err_msg = "\\n".join(manifest.errors) if manifest.errors else "地图资源准备失败"
            QMessageBox.critical(parent, "启动错误", err_msg)
            return False

        # 保存 manifest（用于诊断）
        manifest_dir = abs_game_dir.parent / "launcher_logs"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest.save(manifest_dir / f"manifest_{mid_val}_{int(time.time())}.json")

        # 2. Win32 API 声明
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateMutexA.restype = wintypes.HANDLE
        kernel32.CreateFileMappingA.restype = wintypes.HANDLE
        kernel32.MapViewOfFile.restype = ctypes.c_void_p
        kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        kernel32.CreatePipe.argtypes = [
            ctypes.POINTER(wintypes.HANDLE), ctypes.POINTER(wintypes.HANDLE),
            ctypes.c_void_p, wintypes.DWORD
        ]
        kernel32.CreateFileA.restype = wintypes.HANDLE

        # 3. 互斥体
        parent._game_mutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

        # 4. 共享内存
        parent._shm_handles = []
        for name in [b"7fgame_game_client_start_info", b"7fgame_game_client_login"]:
            size = 512 if b"start_info" in name else 256
            hMap = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, size, name)
            if hMap:
                parent._shm_handles.append(hMap)
                ptr = kernel32.MapViewOfFile(hMap, 0xF001F, 0, 0, size)
                if ptr:
                    ctypes.memset(ptr, 0, size)
                    if b"start_info" in name:
                        ctypes.c_uint32.from_address(ptr).value = mid_val
                    else:
                        buf = (ctypes.c_char * size).from_address(ptr)
                        buf.value = b"localplayer"
                    kernel32.UnmapViewOfFile(ptr)

        # 5. 管道与 NUL 重定向（关键修复）
        class SECURITY_ATTRIBUTES(ctypes.Structure):
            _fields_ = [
                ("nLength", wintypes.DWORD),
                ("lpSecurityDescriptor", wintypes.LPVOID),
                ("bInheritHandle", wintypes.BOOL)
            ]

        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(sa)
        sa.bInheritHandle = True

        hReadPipe = wintypes.HANDLE()
        hWritePipe = wintypes.HANDLE()
        kernel32.CreatePipe(ctypes.byref(hReadPipe), ctypes.byref(hWritePipe), ctypes.byref(sa), 0)

        # NUL 设备句柄 —— 防止 GUI 模式下 C++ 日志系统崩溃
        GENERIC_WRITE = 0x40000000
        OPEN_EXISTING = 3
        hNul = kernel32.CreateFileA(
            b"NUL", GENERIC_WRITE, 3, None, OPEN_EXISTING, 0x80, None
        )

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
        si.dwFlags = 0x101  # STARTF_USESHOWWINDOW | STARTF_USESTDHANDLES
        si.wShowWindow = 1
        si.hStdInput = hReadPipe
        si.hStdOutput = hNul
        si.hStdError = hNul

        game_path = abs_game_dir / "core" / "game.exe"
        work_dir = str(abs_game_dir)
        cmdline = f'"{game_path}" {mid_val}'

        os.environ["PATH"] = str(abs_game_dir / "core") + os.pathsep + os.environ.get("PATH", "")

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
            QMessageBox.critical(parent, "启动错误", f"CreateProcessA 失败，错误码: {err}")
            return False

        # 6. 发送管道数据
        pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, mid_val, 0)
        written = wintypes.DWORD(0)
        kernel32.WriteFile(hWritePipe, pipe_data, len(pipe_data), ctypes.byref(written), None)

        # 7. 关闭句柄
        kernel32.CloseHandle(hReadPipe)
        kernel32.CloseHandle(hWritePipe)
        if hNul:
            kernel32.CloseHandle(hNul)
        kernel32.CloseHandle(pi.hThread)

        parent._game_process_handle = pi.hProcess

        # 8. 后台日志验证（延迟几秒后执行）
        # 注意：不在此处阻塞等待，由 UI 层决定何时验证
        parent._last_launch_manifest = manifest
        parent._last_launch_pid = pi.dwProcessId

        return True

    except Exception as e:
        QMessageBox.critical(parent, "启动错误", str(e))
        return False


def verify_last_launch(parent, game_dir: Path, timeout_seconds: int = 30) -> dict:
    """验证上一次启动的结果（应在游戏运行一段时间后调用）."""
    manifest = getattr(parent, "_last_launch_manifest", None)
    if manifest is None:
        return {"ok": False, "errors": ["没有可验证的启动记录"]}

    expected_map_id = manifest.map_id
    verifier = LogVerifier(game_dir)

    # 等待日志生成
    time.sleep(2)
    log_dir = verifier.find_latest_log_dir()
    if log_dir is None:
        return {"ok": False, "errors": ["未找到日志目录"]}

    # 再次等待，确保日志写入完成
    time.sleep(3)
    return verifier.verify(expected_map_id, log_dir)
