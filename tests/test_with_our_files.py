# -*- coding: utf-8 -*-
"""测试：使用我们的 config.lua 和 edt2.o + 原 GameSetting.inf."""

import ctypes
import os
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

from src.core.config_generator import generate_config_lua, generate_edt2_lua
from src.data.map_data import DEFAULT_MAP_OPTIONS

kernel32 = ctypes.windll.kernel32

def test():
    game_dir = Path(__file__).parent / "data"
    game_exe = game_dir / "core" / "game.exe"
    selected_map = 10002
    map_offset = selected_map - 10000
    options = DEFAULT_MAP_OPTIONS.get(map_offset, [-1] * 10 + [0])

    # 生成我们的 config.lua 和 edt2.o
    config_lua = generate_config_lua(selected_map, options, game_dir=game_dir)
    edt2_lua = generate_edt2_lua(selected_map, options, game_dir=game_dir)

    print(f"[TEST] 我们的 config.lua: {config_lua}")

    # 写入 config.lua
    with open(game_dir / "config.lua", "w", encoding="gbk") as f:
        f.write(config_lua)
    with open(game_dir / "core" / "config.lua", "w", encoding="gbk") as f:
        f.write(config_lua)

    # 编译 edt2.o
    import subprocess
    tmp_lua = game_dir / "core" / "edt2_test.lua"
    tmp_lua.write_text(edt2_lua, encoding="gbk")
    luac = Path(__file__).parent / "lua51_bin" / "luac5.1.exe"
    subprocess.run([str(luac), "-s", "-o", str(game_dir / "core" / "edt2.o"), str(tmp_lua)], capture_output=True)
    subprocess.run([str(luac), "-s", "-o", str(game_dir / "edt2.o"), str(tmp_lua)], capture_output=True)
    tmp_lua.unlink(missing_ok=True)

    # 使用原 GameSetting.inf（已复制到 data/）
    print("[TEST] 使用原 GameSetting.inf")

    # 创建互斥锁
    kernel32.CreateMutexA.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCSTR]
    kernel32.CreateMutexA.restype = wintypes.HANDLE
    hMutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

    # 共享内存
    kernel32.CreateFileMappingA.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.LPCSTR]
    kernel32.CreateFileMappingA.restype = wintypes.HANDLE
    kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
    kernel32.MapViewOfFile.restype = wintypes.LPVOID
    kernel32.UnmapViewOfFile.argtypes = [wintypes.LPVOID]
    kernel32.UnmapViewOfFile.restype = wintypes.BOOL

    hStart = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 512, b"7fgame_game_client_start_info")
    if hStart:
        ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
        if ptr:
            ctypes.memset(ptr, 0, 512)
            ctypes.c_uint32.from_address(ptr).value = int(selected_map)
            kernel32.UnmapViewOfFile(ptr)

    hLogin = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 256, b"7fgame_game_client_login")
    if hLogin:
        ptr = kernel32.MapViewOfFile(hLogin, 0xF001F, 0, 0, 256)
        if ptr:
            ctypes.memset(ptr, 0, 256)
            buf = (ctypes.c_char * 256).from_address(ptr)
            buf.value = b"localplayer"
            kernel32.UnmapViewOfFile(ptr)

    # 创建进程
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", wintypes.LPVOID), ("bInheritHandle", wintypes.BOOL)]
    class STARTUPINFOA(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("lpReserved", wintypes.LPSTR), ("lpDesktop", wintypes.LPSTR), ("lpTitle", wintypes.LPSTR), ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD), ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD), ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD), ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD), ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD), ("lpReserved2", wintypes.LPBYTE), ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE)]
    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE), ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

    sa = SECURITY_ATTRIBUTES()
    sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
    sa.bInheritHandle = True
    hReadPipe = wintypes.HANDLE()
    hWritePipe = wintypes.HANDLE()
    kernel32.CreatePipe(ctypes.byref(hReadPipe), ctypes.byref(hWritePipe), ctypes.byref(sa), 0)

    hNul = kernel32.CreateFileA(b"NUL", 0x40000000, 3, None, 3, 0x80, None)
    si = STARTUPINFOA()
    si.cb = ctypes.sizeof(STARTUPINFOA)
    si.dwFlags = 0x101
    si.wShowWindow = 1
    si.hStdInput = hReadPipe
    si.hStdOutput = hNul
    si.hStdError = hNul

    pi = PROCESS_INFORMATION()
    core_dir = str(game_dir / "core")
    os.environ["PATH"] = core_dir + os.pathsep + os.environ.get("PATH", "")
    game_path = str(game_exe)
    work_dir = str(game_dir)
    cmdline = f'"{game_path}" {selected_map}'

    ok = kernel32.CreateProcessA(game_path.encode("mbcs"), cmdline.encode("mbcs"), None, None, True, 0, None, work_dir.encode("mbcs"), ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        print(f"[TEST] CreateProcessA failed")
        return False

    kernel32.CloseHandle(hReadPipe)
    kernel32.CloseHandle(hNul)
    pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, int(selected_map), 0)
    written = wintypes.DWORD()
    kernel32.WriteFile(hWritePipe, pipe_data, len(pipe_data), ctypes.byref(written), None)
    kernel32.CloseHandle(hWritePipe)
    kernel32.CloseHandle(pi.hThread)

    print(f"[TEST] 游戏 PID={pi.dwProcessId}")
    time.sleep(8)

    log_dirs = sorted([d for d in game_dir.glob("log*") if d.is_dir()], key=lambda x: x.stat().st_mtime)
    if log_dirs:
        latest_log = log_dirs[-1]
        error_log = latest_log / "error.log"
        if error_log.exists():
            content = error_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] error.log: {content[:300]}")
            if "tab_interface" in content:
                print("[TEST] 结果: 我们的文件 + 原 GameSetting.inf 仍然报错!")
                return False
            elif content.strip():
                print("[TEST] 结果: 有其他错误")
                return False
            else:
                print("[TEST] 结果: 无错误!")
                return True
        else:
            print("[TEST] 结果: 无 error.log!")
            return True
    return False

if __name__ == "__main__":
    success = test()
    print(f"[TEST] 最终: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1)
