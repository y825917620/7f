# -*- coding: utf-8 -*-
"""测试重构后的启动链路 — 命令模式直接启动，不依赖 UI."""

import ctypes
import os
import struct
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

# 把 src 加入路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.map_catalog import MapCatalog
from src.core.resource_mount_manager import ResourceMountManager
from src.launcher.log_verifier import LogVerifier

GAME_DIR = Path(r"E:\\玩家原创\\神龙地图启动器5.2\\data")
MAP_ID = 10002


def launch_direct(map_id: int, game_dir: Path) -> int:
    """直接启动游戏，返回 PID."""
    kernel32 = ctypes.windll.kernel32

    # 资源准备
    catalog = MapCatalog(game_dir)
    info = catalog.get_info(map_id)
    if not info:
        print(f"[ERROR] 地图 {map_id} 未找到")
        return 0

    diag = catalog.diagnose(map_id)
    if diag:
        print(f"[ERROR] {diag}")
        return 0

    mount_mgr = ResourceMountManager(game_dir)
    manifest = mount_mgr.prepare(map_id, info["sl_path"])
    if not manifest.is_valid():
        print(f"[ERROR] 资源准备失败: {manifest.errors}")
        return 0

    print(f"[INFO] 地图 {map_id} 资源已挂载到: {manifest.mount_points}")

    # Win32 启动
    kernel32.CreateMutexA.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCSTR]
    kernel32.CreateMutexA.restype = wintypes.HANDLE

    kernel32.CreateFileMappingA.argtypes = [
        wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
        wintypes.DWORD, wintypes.DWORD, wintypes.LPCSTR
    ]
    kernel32.CreateFileMappingA.restype = wintypes.HANDLE

    kernel32.MapViewOfFile.argtypes = [
        wintypes.HANDLE, wintypes.DWORD,
        wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t
    ]
    kernel32.MapViewOfFile.restype = wintypes.LPVOID

    kernel32.UnmapViewOfFile.argtypes = [wintypes.LPVOID]
    kernel32.UnmapViewOfFile.restype = wintypes.BOOL

    hMutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")
    print(f"[INFO] Mutex: {hMutex}")

    hStart = kernel32.CreateFileMappingA(
        wintypes.HANDLE(-1), None, 0x04, 0, 512, b"7fgame_game_client_start_info"
    )
    if hStart:
        ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
        if ptr:
            ctypes.memset(ptr, 0, 512)
            ctypes.c_uint32.from_address(ptr).value = map_id
            kernel32.UnmapViewOfFile(ptr)
        print("[INFO] Shared memory start_info created")

    hLogin = kernel32.CreateFileMappingA(
        wintypes.HANDLE(-1), None, 0x04, 0, 256, b"7fgame_game_client_login"
    )
    if hLogin:
        ptr = kernel32.MapViewOfFile(hLogin, 0xF001F, 0, 0, 256)
        if ptr:
            ctypes.memset(ptr, 0, 256)
            buf = (ctypes.c_char * 256).from_address(ptr)
            buf.value = b"localplayer"
            kernel32.UnmapViewOfFile(ptr)
        print("[INFO] Shared memory login created")

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

    hNul = kernel32.CreateFileA(b"NUL", 0x40000000, 3, None, 3, 0x80, None)

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
    si.hStdInput = hReadPipe
    si.hStdOutput = hNul
    si.hStdError = hNul

    game_exe = game_dir / "core" / "game.exe"
    work_dir = str(game_dir)
    cmdline = f'"{game_exe}" {map_id}'

    core_dir = str(game_dir / "core")
    os.environ["PATH"] = core_dir + os.pathsep + os.environ.get("PATH", "")

    pi = PROCESS_INFORMATION()
    ok = kernel32.CreateProcessA(
        str(game_exe).encode("mbcs"),
        cmdline.encode("mbcs"),
        None, None, True, 0, None,
        work_dir.encode("mbcs"),
        ctypes.byref(si), ctypes.byref(pi)
    )

    if not ok:
        err = kernel32.GetLastError()
        print(f"[ERROR] CreateProcessA failed: {err}")
        return 0

    pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, map_id, 0)
    written = wintypes.DWORD()
    kernel32.WriteFile(hWritePipe, pipe_data, len(pipe_data), ctypes.byref(written), None)

    kernel32.CloseHandle(hReadPipe)
    kernel32.CloseHandle(hWritePipe)
    kernel32.CloseHandle(hNul)
    kernel32.CloseHandle(pi.hThread)

    print(f"[INFO] Game started PID={pi.dwProcessId}")
    return pi.dwProcessId


def main():
    print("=" * 60)
    print(f"测试重构启动链路 — 地图 {MAP_ID}")
    print("=" * 60)

    # 记录启动前日志目录
    before = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    print(f"[INFO] 启动前日志数: {len(before)}")

    pid = launch_direct(MAP_ID, GAME_DIR)
    if pid == 0:
        sys.exit(1)

    # 启动对话框监视线程（自动关闭 LOG 错误对话框）
    dialog_closed = []
    def watch_dialogs():
        user32 = ctypes.windll.user32
        for _ in range(120):
            hwnd = user32.FindWindowA(b"#32770", b"LOG")
            if hwnd:
                print("[DIALOG] 发现 LOG 对话框，正在关闭")
                user32.ShowWindow(hwnd, 0)
                user32.PostMessageA(hwnd, 0x10, 0, 0)
                dialog_closed.append(True)
            time.sleep(0.5)

    t = threading.Thread(target=watch_dialogs, daemon=True)
    t.start()

    print("[INFO] 等待 60 秒让游戏运行...")
    time.sleep(60)

    after = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    new = after - before
    print(f"[INFO] 新日志目录: {new}")
    if dialog_closed:
        print("[INFO] 已自动关闭 LOG 对话框")

    verifier = LogVerifier(GAME_DIR)
    result = verifier.verify(MAP_ID)

    print("\\n--- 验证结果 ---")
    print(f"日志目录: {result['log_dir']}")
    print(f"地图ID匹配: {result['map_id_match']}")
    print(f"sanguo.o 加载: {result['has_sanguo_o']}")
    print(f"begin load map: {result['has_begin_load']}")
    print(f"AfterRunGameLogic: {result['after_run_count']}")
    print(f"Render: {result['render_count']}")
    print(f"错误: {result['errors']}")
    print(f"整体通过: {result['ok']}")
    print("---")

    if result['tail_lines']:
        print("\\n--- 日志尾部 ---")
        for line in result['tail_lines']:
            print(line)
        print("---")

    # 终止游戏
    kernel32 = ctypes.windll.kernel32
    hProc = kernel32.OpenProcess(1, False, pid)
    if hProc:
        kernel32.TerminateProcess(hProc, 0)
        kernel32.CloseHandle(hProc)
        print("[INFO] 已终止游戏进程")

    sys.exit(0 if result['ok'] else 1)


if __name__ == "__main__":
    main()
