
import ctypes
import os
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器5.2\data")
MAP_ID = 10002

def test_launch(cmdline_extra: str):
    kernel32 = ctypes.windll.kernel32
    
    hNul = kernel32.CreateFileA(b"NUL", 0x40000000, 3, None, 3, 0x80, None)
    
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", wintypes.LPVOID), ("bInheritHandle", wintypes.BOOL)]
    sa = SECURITY_ATTRIBUTES()
    sa.nLength = ctypes.sizeof(sa)
    sa.bInheritHandle = True
    
    hReadPipe = wintypes.HANDLE()
    hWritePipe = wintypes.HANDLE()
    kernel32.CreatePipe(ctypes.byref(hReadPipe), ctypes.byref(hWritePipe), ctypes.byref(sa), 0)
    
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
    
    si = STARTUPINFOA()
    si.cb = ctypes.sizeof(si)
    si.dwFlags = 0x101
    si.wShowWindow = 1
    si.hStdInput = hReadPipe
    si.hStdOutput = hNul
    si.hStdError = hNul
    
    game_exe = GAME_DIR / "core" / "game.exe"
    work_dir = str(GAME_DIR)
    cmdline = f'"{game_exe}" {MAP_ID} {cmdline_extra}'
    
    core_dir = str(GAME_DIR / "core")
    os.environ["PATH"] = core_dir + os.pathsep + os.environ.get("PATH", "")
    
    pi = PROCESS_INFORMATION()
    ok = kernel32.CreateProcessA(
        str(game_exe).encode("mbcs"), cmdline.encode("mbcs"),
        None, None, True, 0, None, work_dir.encode("mbcs"), ctypes.byref(si), ctypes.byref(pi)
    )
    
    if not ok:
        print(f'[FAIL] CreateProcess failed: {kernel32.GetLastError()}')
        return
    
    pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, MAP_ID, 0)
    written = wintypes.DWORD()
    kernel32.WriteFile(hWritePipe, pipe_data, len(pipe_data), ctypes.byref(written), None)
    
    kernel32.CloseHandle(hReadPipe)
    kernel32.CloseHandle(hWritePipe)
    kernel32.CloseHandle(hNul)
    kernel32.CloseHandle(pi.hThread)
    
    print(f'[TEST] PID={pi.dwProcessId}, cmdline={cmdline_extra!r}')
    time.sleep(12)
    
    # 检查错误日志
    log_dirs = [d for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr"]
    if log_dirs:
        latest = max(log_dirs, key=lambda d: d.stat().st_mtime)
        err_log = latest / "error.log"
        if err_log.exists():
            content = err_log.read_text(encoding="gbk", errors="ignore")
            if "tab_interface" in content:
                print(f'[RESULT] tab_interface NIL (FAILED)')
            else:
                print(f'[RESULT] NO tab_interface error (MAYBE OK)')
        else:
            print(f'[RESULT] no error.log')
    
    # 杀掉进程
    hProc = kernel32.OpenProcess(1, False, pi.dwProcessId)
    if hProc:
        kernel32.TerminateProcess(hProc, 0)
        kernel32.CloseHandle(hProc)
    time.sleep(2)

# 测试不同参数
test_launch("")  # 基准
test_launch("/testgamebyeditor=1")
test_launch("/testgamebyeditor=0")
test_launch("/mode=host")
test_launch("/mode=single")
test_launch("MemoryMapName=sanguo")
test_launch("/testgamebyeditor=1 MemoryMapName=sanguo")
