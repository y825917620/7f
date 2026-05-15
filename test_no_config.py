# -*- coding: utf-8 -*-
"""测试：删除 config.lua，看游戏是否能正常加载."""

import ctypes
import os
import shutil
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

kernel32 = ctypes.windll.kernel32


def test():
    game_dir = Path(__file__).parent / "data"
    game_exe = game_dir / "core" / "game.exe"
    selected_map = 10002
    data_test = Path(__file__).parent / "data_test"

    # 删除 config.lua
    for p in [game_dir / "config.lua", game_dir / "core" / "config.lua"]:
        if p.exists():
            p.unlink()
            print(f"[TEST] 已删除 {p}")

    # 删除 edt2.o（如果有）
    edt2_o = game_dir / "core" / "edt2.o"
    if edt2_o.exists():
        edt2_o.unlink()
        print("[TEST] 已删除 edt2.o")

    # 确保 edt2.lua 不存在
    edt2_lua = game_dir / "core" / "edt2.lua"
    if edt2_lua.exists():
        edt2_lua.unlink()
        print("[TEST] 已删除 edt2.lua")

    # 确保 sl/map.map 存在
    if (data_test / "sl" / "map.map").exists():
        sl_dir = game_dir / "sl"
        sl_dir.mkdir(exist_ok=True)
        shutil.copy2(data_test / "sl" / "map.map", sl_dir / "map.map")
        core_sl_dir = game_dir / "core" / "sl"
        core_sl_dir.mkdir(exist_ok=True)
        shutil.copy2(data_test / "sl" / "map.map", core_sl_dir / "map.map")
        print("[TEST] 已复制 sl/map.map")

    # 删除 map.o（如果有）
    map_o = game_dir / "map.o"
    if map_o.exists():
        map_o.unlink()
        print("[TEST] 已删除 map.o")

    # 创建互斥锁
    kernel32.CreateMutexA.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCSTR]
    kernel32.CreateMutexA.restype = wintypes.HANDLE
    kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

    # 共享内存
    kernel32.CreateFileMappingA.argtypes = [
        wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
        wintypes.DWORD, wintypes.DWORD, wintypes.LPCSTR
    ]
    kernel32.CreateFileMappingA.restype = wintypes.HANDLE
    kernel32.MapViewOfFile.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
        wintypes.DWORD, ctypes.c_size_t
    ]
    kernel32.MapViewOfFile.restype = wintypes.LPVOID
    kernel32.UnmapViewOfFile.argtypes = [wintypes.LPVOID]
    kernel32.UnmapViewOfFile.restype = wintypes.BOOL

    hStart = kernel32.CreateFileMappingA(
        wintypes.HANDLE(-1), None, 0x04, 0, 512,
        b"7fgame_game_client_start_info"
    )
    if hStart:
        ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
        if ptr:
            ctypes.memset(ptr, 0, 512)
            ctypes.c_uint32.from_address(ptr).value = int(selected_map)
            kernel32.UnmapViewOfFile(ptr)

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

    # 创建进程
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [
            ("nLength", wintypes.DWORD),
            ("lpSecurityDescriptor", wintypes.LPVOID),
            ("bInheritHandle", wintypes.BOOL),
        ]

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
            ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD),
        ]

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

    print(f"[TEST] 命令行: {cmdline}")

    ok = kernel32.CreateProcessA(
        game_path.encode("mbcs"), cmdline.encode("mbcs"),
        None, None, True, 0, None, work_dir.encode("mbcs"),
        ctypes.byref(si), ctypes.byref(pi)
    )
    if not ok:
        print("[TEST] CreateProcessA failed")
        return False

    kernel32.CloseHandle(hReadPipe)
    kernel32.CloseHandle(hNul)
    pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, int(selected_map), 0)
    written = wintypes.DWORD()
    kernel32.WriteFile(hWritePipe, pipe_data, len(pipe_data), ctypes.byref(written), None)
    kernel32.CloseHandle(hWritePipe)
    kernel32.CloseHandle(pi.hThread)

    print(f"[TEST] 游戏 PID={pi.dwProcessId}")
    time.sleep(12)

    # 检查进程状态
    exit_code = wintypes.DWORD()
    if kernel32.GetExitCodeProcess(pi.hProcess, ctypes.byref(exit_code)):
        if exit_code.value == 259:
            print(f"[TEST] 游戏进程仍在运行!")
        else:
            print(f"[TEST] 游戏进程已退出，退出码={exit_code.value}")
    kernel32.CloseHandle(pi.hProcess)

    # 分析日志
    log_dirs = sorted([d for d in game_dir.glob("log*") if d.is_dir()], key=lambda x: x.stat().st_mtime)
    if log_dirs:
        latest_log = log_dirs[-1]
        print(f"[TEST] 最新日志: {latest_log.name}")

        init_log = latest_log / "init.log"
        if init_log.exists():
            content = init_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] init.log: {len(content)} bytes")
            lines = content.strip().split("\n")
            for line in lines[-15:]:
                print(f"  {line}")

        error_log = latest_log / "error.log"
        if error_log.exists():
            content = error_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] error.log ({len(content)} bytes):")
            print(content[:600])
            if "tab_interface" in content:
                print("[TEST] 结果: 仍然有 tab_interface 错误!")
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
