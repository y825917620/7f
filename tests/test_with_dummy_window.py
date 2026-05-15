# -*- coding: utf-8 -*-
"""直接测试 - 但先创建一个标题为'神龙地图启动器'的虚拟窗口."""

import ctypes
import os
import struct
import subprocess
import sys
import threading
import time
import tkinter as tk
from ctypes import wintypes
from pathlib import Path

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器\data")
MAP_ID = 10002


def create_dummy_window():
    """创建一个最小化的虚拟窗口，标题与原启动器一致."""
    root = tk.Tk()
    root.title("神龙地图启动器")
    root.geometry("1x1+0+0")
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.update()
    print(f"[INFO] Dummy window created, handle={root.winfo_id()}")
    return root


def launch():
    kernel32 = ctypes.windll.kernel32

    kernel32.CreateMutexA.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCSTR]
    kernel32.CreateMutexA.restype = wintypes.HANDLE

    kernel32.CreateFileMappingA.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.LPCSTR]
    kernel32.CreateFileMappingA.restype = wintypes.HANDLE

    kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
    kernel32.MapViewOfFile.restype = wintypes.LPVOID

    kernel32.UnmapViewOfFile.argtypes = [wintypes.LPVOID]
    kernel32.UnmapViewOfFile.restype = wintypes.BOOL

    hMutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")
    print(f"[INFO] Mutex: {hMutex}")

    hStart = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 512, b"7fgame_game_client_start_info")
    if hStart:
        ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
        if ptr:
            ctypes.memset(ptr, 0, 512)
            ctypes.c_uint32.from_address(ptr).value = MAP_ID
            kernel32.UnmapViewOfFile(ptr)
        print("[INFO] Shared memory start_info created")

    hLogin = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 256, b"7fgame_game_client_login")
    if hLogin:
        ptr = kernel32.MapViewOfFile(hLogin, 0xF001F, 0, 0, 256)
        if ptr:
            ctypes.memset(ptr, 0, 256)
            buf = (ctypes.c_char * 256).from_address(ptr)
            buf.value = b"localplayer"
            kernel32.UnmapViewOfFile(ptr)
        print("[INFO] Shared memory login created")

    core_dir = str(GAME_DIR / "core")
    os.environ["PATH"] = core_dir + os.pathsep + os.environ.get("PATH", "")

    game_exe = GAME_DIR / "core" / "game.exe"
    work_dir = str(GAME_DIR)
    cmdline = f'"{game_exe}" {MAP_ID}'

    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", wintypes.LPVOID), ("bInheritHandle", wintypes.BOOL)]

    class STARTUPINFOA(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD), ("lpReserved", wintypes.LPSTR), ("lpDesktop", wintypes.LPSTR),
            ("lpTitle", wintypes.LPSTR), ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
            ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD), ("dwXCountChars", wintypes.DWORD),
            ("dwYCountChars", wintypes.DWORD), ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
            ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD), ("lpReserved2", wintypes.LPBYTE),
            ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE),
        ]

    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE), ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

    sa = SECURITY_ATTRIBUTES()
    sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
    sa.lpSecurityDescriptor = None
    sa.bInheritHandle = True

    hRead = wintypes.HANDLE()
    hWrite = wintypes.HANDLE()
    kernel32.CreatePipe(ctypes.byref(hRead), ctypes.byref(hWrite), ctypes.byref(sa), 0)

    hNul = kernel32.CreateFileA(b"NUL", 0x40000000, 3, None, 3, 0x80, None)

    si = STARTUPINFOA()
    si.cb = ctypes.sizeof(STARTUPINFOA)
    si.dwFlags = 0x101
    si.wShowWindow = 1
    si.hStdInput = hRead
    si.hStdOutput = hNul
    si.hStdError = hNul

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
        return None

    kernel32.CloseHandle(hRead)
    kernel32.CloseHandle(hNul)

    pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, MAP_ID, 0)
    written = wintypes.DWORD()
    kernel32.WriteFile(hWrite, pipe_data, len(pipe_data), ctypes.byref(written), None)
    kernel32.CloseHandle(hWrite)
    kernel32.CloseHandle(pi.hThread)

    print(f"[INFO] Game started PID={pi.dwProcessId}")
    return pi.hProcess


def analyze_logs():
    import glob
    log_dirs = sorted([d for d in glob.glob(str(GAME_DIR / "log*")) if os.path.isdir(d) and "log_mgr" not in d], key=lambda x: os.path.getmtime(x), reverse=True)
    if not log_dirs:
        print("[WARN] No log dirs")
        return False

    latest = log_dirs[0]
    init_log = os.path.join(latest, "init.log")
    if os.path.exists(init_log):
        with open(init_log, "r", encoding="gbk", errors="ignore") as f:
            content = f.read()
        print(f"[INFO] init.log: {len(content)} bytes")
        has_sanguo = "do [map/sanguo/sanguo.o] ok!" in content
        after = content.count("enter:AfterRunGameLogic")
        render = content.count("enter:Render")
        print(f"[INFO] sanguo.o={has_sanguo}, After={after}, Render={render}")
        for line in content.splitlines()[-10:]:
            print(line)
        return has_sanguo and after > 2 and render > 2
    return False


def main():
    root = create_dummy_window()

    hProc = launch()
    if not hProc:
        root.destroy()
        sys.exit(1)

    print("[INFO] Waiting 15s...")
    time.sleep(15)

    success = analyze_logs()

    kernel32 = ctypes.windll.kernel32
    kernel32.TerminateProcess(hProc, 0)
    kernel32.CloseHandle(hProc)
    print("[INFO] Game terminated")

    root.destroy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
