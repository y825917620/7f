# -*- coding: utf-8 -*-
"""测试：监控游戏进程创建的子进程."""

import ctypes
import os
import psutil
import shutil
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

kernel32 = ctypes.windll.kernel32


def get_process_tree(parent_pid):
    """获取进程树."""
    children = []
    for p in psutil.process_iter(['pid', 'ppid', 'name']):
        try:
            if p.info['ppid'] == parent_pid:
                children.append((p.info['pid'], p.info['name']))
        except:
            pass
    return children


def test():
    game_dir = Path(__file__).parent / "data"
    game_exe = game_dir / "core" / "game.exe"
    selected_map = 10002
    data_test = Path(__file__).parent / "data_test"

    # 恢复 data_test 状态
    if (data_test / "sl" / "map.map").exists():
        sl_dir = game_dir / "sl"
        sl_dir.mkdir(exist_ok=True)
        shutil.copy2(data_test / "sl" / "map.map", sl_dir / "map.map")

    if (data_test / "core" / "sl" / "map.map").exists():
        core_sl_dir = game_dir / "core" / "sl"
        core_sl_dir.mkdir(exist_ok=True)
        shutil.copy2(data_test / "core" / "sl" / "map.map", core_sl_dir / "map.map")

    if (data_test / "core" / "config.lua").exists():
        shutil.copy2(data_test / "core" / "config.lua", game_dir / "config.lua")
        shutil.copy2(data_test / "core" / "config.lua", game_dir / "core" / "config.lua")

    edt2_o = game_dir / "core" / "edt2.o"
    if edt2_o.exists():
        edt2_o.unlink()
    if (data_test / "core" / "edt2.lua").exists():
        shutil.copy2(data_test / "core" / "edt2.lua", game_dir / "core" / "edt2.lua")

    if (data_test / "core" / "GameSetting.inf").exists():
        shutil.copy2(data_test / "core" / "GameSetting.inf", game_dir / "GameSetting.inf")
        shutil.copy2(data_test / "core" / "GameSetting.inf", game_dir / "core" / "GameSetting.inf")

    map_o = game_dir / "map.o"
    if map_o.exists():
        map_o.unlink()

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

    # 监控子进程
    print("\n[TEST] 监控子进程...")
    for i in range(10):
        time.sleep(1)
        children = get_process_tree(pi.dwProcessId)
        if children:
            print(f"  t+{i+1}s: 子进程: {children}")
        # 也检查进程是否还在
        try:
            p = psutil.Process(pi.dwProcessId)
            if not p.is_running():
                print(f"  t+{i+1}s: 主进程已退出")
                break
        except:
            print(f"  t+{i+1}s: 主进程已退出")
            break

    kernel32.CloseHandle(pi.hProcess)

    # 分析日志
    log_dirs = sorted([d for d in game_dir.glob("log*") if d.is_dir()], key=lambda x: x.stat().st_mtime)
    if log_dirs:
        latest_log = log_dirs[-1]
        init_log = latest_log / "init.log"
        if init_log.exists():
            content = init_log.read_text(encoding="gbk", errors="ignore")
            print(f"\n[TEST] init.log ({len(content)} bytes):")
            for line in content.strip().split("\n")[-10:]:
                print(f"  {line}")

    return True


if __name__ == "__main__":
    test()
