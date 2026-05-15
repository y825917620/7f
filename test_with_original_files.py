# -*- coding: utf-8 -*-
"""测试：使用原启动器的 config.lua 和 edt2.o，验证是文件问题还是启动环境问题."""

import ctypes
import os
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

kernel32 = ctypes.windll.kernel32

def launch_with_original_files():
    game_dir = Path(__file__).parent / "data"
    game_exe = game_dir / "core" / "game.exe"
    selected_map = 10002

    # 1. 用原启动器的文件覆盖
    orig_config = Path(__file__).parent / "orig_config.lua"
    orig_edt2 = Path(__file__).parent / "orig_edt2.o"

    # 写入 config.lua
    if orig_config.exists():
        config_lua = orig_config.read_text(encoding="gbk")
        print(f"[TEST] 原 config.lua ({len(config_lua)} bytes): {config_lua[:80]}...")
        with open(game_dir / "config.lua", "w", encoding="gbk") as f:
            f.write(config_lua)
        with open(game_dir / "core" / "config.lua", "w", encoding="gbk") as f:
            f.write(config_lua)
    else:
        print("[TEST] ⚠️ 找不到 orig_config.lua")
        return False

    # 写入 edt2.o
    if orig_edt2.exists():
        edt2_data = orig_edt2.read_bytes()
        print(f"[TEST] 原 edt2.o ({len(edt2_data)} bytes)")
        (game_dir / "core" / "edt2.o").write_bytes(edt2_data)
        (game_dir / "edt2.o").write_bytes(edt2_data)
    else:
        print("[TEST] ⚠️ 找不到 orig_edt2.o")
        return False

    # 2. 创建互斥锁
    kernel32.CreateMutexA.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCSTR]
    kernel32.CreateMutexA.restype = wintypes.HANDLE
    hMutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")
    print(f"[TEST] 互斥锁: {hMutex}")

    # 3. 创建共享内存
    kernel32.CreateFileMappingA.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.LPCSTR]
    kernel32.CreateFileMappingA.restype = wintypes.HANDLE
    kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
    kernel32.MapViewOfFile.restype = wintypes.LPVOID
    kernel32.UnmapViewOfFile.argtypes = [wintypes.LPVOID]
    kernel32.UnmapViewOfFile.restype = wintypes.BOOL

    SHM_START_SIZE = 512
    hStart = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, SHM_START_SIZE, b"7fgame_game_client_start_info")
    if hStart:
        ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, SHM_START_SIZE)
        if ptr:
            ctypes.memset(ptr, 0, SHM_START_SIZE)
            ctypes.c_uint32.from_address(ptr).value = int(selected_map)
            kernel32.UnmapViewOfFile(ptr)
        print("[TEST] 共享内存 start_info OK")

    SHM_LOGIN_SIZE = 256
    hLogin = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, SHM_LOGIN_SIZE, b"7fgame_game_client_login")
    if hLogin:
        ptr = kernel32.MapViewOfFile(hLogin, 0xF001F, 0, 0, SHM_LOGIN_SIZE)
        if ptr:
            ctypes.memset(ptr, 0, SHM_LOGIN_SIZE)
            buf = (ctypes.c_char * SHM_LOGIN_SIZE).from_address(ptr)
            buf.value = b"localplayer"
            kernel32.UnmapViewOfFile(ptr)
        print("[TEST] 共享内存 login OK")

    # 4. 创建管道 + CreateProcessA
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", wintypes.LPVOID), ("bInheritHandle", wintypes.BOOL)]

    class STARTUPINFOA(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("lpReserved", wintypes.LPSTR), ("lpDesktop", wintypes.LPSTR), ("lpTitle", wintypes.LPSTR), ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD), ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD), ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD), ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD), ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD), ("lpReserved2", wintypes.LPBYTE), ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE)]

    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE), ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

    sa = SECURITY_ATTRIBUTES()
    sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
    sa.lpSecurityDescriptor = None
    sa.bInheritHandle = True

    hReadPipe = wintypes.HANDLE()
    hWritePipe = wintypes.HANDLE()
    kernel32.CreatePipe(ctypes.byref(hReadPipe), ctypes.byref(hWritePipe), ctypes.byref(sa), 0)

    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 3
    hNul = kernel32.CreateFileA(b"NUL", GENERIC_WRITE, 3, None, OPEN_EXISTING, 0x80, None)

    si = STARTUPINFOA()
    si.cb = ctypes.sizeof(STARTUPINFOA)
    si.dwFlags = 0x101
    si.wShowWindow = 1
    si.hStdInput = hReadPipe
    si.hStdOutput = hNul
    si.hStdError = hNul

    pi = PROCESS_INFORMATION()
    game_path = str(game_exe)
    work_dir = str(game_dir)
    cmdline = f'"{game_path}" {selected_map}'

    core_dir = str(game_dir / "core")
    os.environ["PATH"] = core_dir + os.pathsep + os.environ.get("PATH", "")

    print(f"[TEST] 命令行: {cmdline}")
    print(f"[TEST] 工作目录: {work_dir}")

    ok = kernel32.CreateProcessA(
        game_path.encode("mbcs"), cmdline.encode("mbcs"),
        None, None, True, 0, None, work_dir.encode("mbcs"),
        ctypes.byref(si), ctypes.byref(pi)
    )

    if not ok:
        err = kernel32.GetLastError()
        print(f"[TEST] CreateProcessA 失败: {err}")
        return False

    kernel32.CloseHandle(hReadPipe)
    kernel32.CloseHandle(hNul)

    pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, int(selected_map), 0)
    written = wintypes.DWORD()
    kernel32.WriteFile(hWritePipe, pipe_data, len(pipe_data), ctypes.byref(written), None)
    kernel32.CloseHandle(hWritePipe)
    kernel32.CloseHandle(pi.hThread)

    print(f"[TEST] 游戏已启动 PID={pi.dwProcessId}")
    print("[TEST] 等待 8 秒...")
    time.sleep(8)

    # 检查日志
    log_dirs = sorted([d for d in game_dir.glob("log*") if d.is_dir()], key=lambda x: x.stat().st_mtime)
    if log_dirs:
        latest_log = log_dirs[-1]
        print(f"[TEST] 最新日志: {latest_log.name}")
        error_log = latest_log / "error.log"
        if error_log.exists():
            content = error_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] error.log:\n{content[:500]}")
            if "tab_interface" in content:
                print("[TEST] 结果: 使用原启动器文件仍然报错 tab_interface!")
                return False
            elif content.strip():
                print("[TEST] 结果: 使用原启动器文件有其他错误")
                return False
            else:
                print("[TEST] 结果: 使用原启动器文件无错误!")
                return True
        else:
            print("[TEST] 结果: 无 error.log，可能正常!")
            return True
    return False

if __name__ == "__main__":
    success = launch_with_original_files()
    print(f"[TEST] 最终: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1)
