# -*- coding: utf-8 -*-
"""直接测试 - 在原始 launcher 的 data 目录下启动，使用完全原始的文件"""

import ctypes
import os
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

# 使用原始 launcher 的 data 目录
GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器\data")
MAP_ID = 10002


def launch():
    kernel32 = ctypes.windll.kernel32

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

    hMutex = kernel32.CreateMutexA(None, True, b"7fxx_dgtm")
    print(f"[INFO] Mutex: {hMutex}")

    hStart = kernel32.CreateFileMappingA(
        wintypes.HANDLE(-1), None, 0x04, 0, 512, b"7fgame_game_client_start_info"
    )
    if hStart:
        ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
        if ptr:
            ctypes.memset(ptr, 0, 512)
            ctypes.c_uint32.from_address(ptr).value = MAP_ID
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
    log_dirs = sorted([d for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr"], key=lambda x: x.stat().st_mtime, reverse=True)
    if not log_dirs:
        print("[WARN] 未找到日志目录")
        return False

    latest = log_dirs[0]
    print(f"\n[INFO] 分析日志: {latest.name}")

    init_log = latest / "init.log"
    if init_log.exists():
        content = init_log.read_text(encoding="gbk", errors="ignore")
        print(f"[INFO] init.log: {len(content)} bytes")

        has_sanguo_o = "do [map/sanguo/sanguo.o] ok!" in content
        has_begin_load = "begin load map[sanguo]" in content
        after_count = content.count("enter:AfterRunGameLogic")
        render_count = content.count("enter:Render")

        print(f"[INFO] do [map/sanguo/sanguo.o] ok! = {has_sanguo_o}")
        print(f"[INFO] begin load map[sanguo] = {has_begin_load}")
        print(f"[INFO] AfterRunGameLogic count = {after_count}")
        print(f"[INFO] Render count = {render_count}")

        lines = content.strip().split("\n")
        print("\n--- 日志尾部 ---")
        for line in lines[-20:]:
            print(line)
        print("---")

        if has_sanguo_o and after_count > 2 and render_count > 2:
            print("\n[OK] 地图脚本加载成功，游戏进入主循环!")
            return True
        elif not has_sanguo_o and has_begin_load:
            print("\n[FAIL] 游戏进入地图但未加载 sanguo.o 脚本")
            return False
        else:
            print("\n[FAIL] 游戏未正常进入地图主循环")
            return False
    else:
        print("[WARN] 未找到 init.log")
        return False


def main():
    print("=" * 60)
    print("测试：使用原始 launcher 目录启动地图 10002")
    print("=" * 60)

    before = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    print(f"[INFO] 启动前日志数: {len(before)}")

    # 确认原始目录的关键文件
    for f in ["config.lua", "core/edt2.o", "GameSetting.inf"]:
        p = GAME_DIR / f
        print(f"[INFO] {'存在' if p.exists() else '缺失'}: {f}")

    hProc = launch()
    if not hProc:
        sys.exit(1)

    # Start dialog watcher that captures text before closing
    import threading
    def watch_dialogs():
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        for _ in range(120):
            hwnd = user32.FindWindowA(b"#32770", b"LOG")
            if hwnd:
                # Read dialog text
                def get_text(h):
                    length = user32.GetWindowTextLengthW(h)
                    if length == 0:
                        return ""
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(h, buf, length + 1)
                    return buf.value
                # Enum child windows
                texts = []
                ENUM_CHILD = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
                def cb(child, _):
                    cls = ctypes.create_unicode_buffer(256)
                    user32.GetClassNameW(child, cls, 256)
                    t = get_text(child)
                    if t:
                        texts.append(t)
                    return True
                user32.EnumChildWindows(hwnd, ENUM_CHILD(cb), 0)
                print(f"[DIALOG] LOG dialog texts: {texts}")
                user32.ShowWindow(hwnd, 0)
                user32.PostMessageA(hwnd, 0x10, 0, 0)
                print("[INFO] Closed LOG dialog")
            time.sleep(0.5)

    t = threading.Thread(target=watch_dialogs, daemon=True)
    t.start()

    print("[INFO] 等待 30 秒让游戏运行...")
    time.sleep(30)

    after = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    new = after - before
    print(f"[INFO] 新日志目录: {new}")

    success = analyze_logs()

    kernel32 = ctypes.windll.kernel32
    kernel32.TerminateProcess(hProc, 0)
    kernel32.CloseHandle(hProc)
    print("[INFO] 已终止游戏进程")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
