# -*- coding: utf-8 -*-
"""测试：创建 sanguo 文件（而非共享内存映射），配合 MemoryMapName=sanguo 启动游戏."""

import ctypes
import os
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

kernel32 = ctypes.windll.kernel32


def test(sanguo_file_size=0):
    game_dir = Path(__file__).parent / "data"
    game_exe = game_dir / "core" / "game.exe"
    selected_map = 10002

    # 使用原启动器的所有文件
    for src_name, dst_path in [
        ("orig_config.lua", game_dir / "config.lua"),
        ("orig_edt2.o", game_dir / "core" / "edt2.o"),
        ("orig_map.o", game_dir / "map.o"),
    ]:
        src = Path(__file__).parent / src_name
        if src.exists():
            dst_path.write_bytes(src.read_bytes())

    # 删除空 sl/ 目录
    sl_dir = game_dir / "sl"
    if sl_dir.exists() and not any(sl_dir.iterdir()):
        sl_dir.rmdir()

    # 创建 sanguo 文件（而非共享内存）
    sanguo_file = game_dir / "sanguo"
    if sanguo_file_size > 0:
        # 复制 .sl 文件内容
        sl_file = game_dir / "map" / f"{selected_map}.sl"
        if sl_file.exists():
            sanguo_file.write_bytes(sl_file.read_bytes()[:sanguo_file_size])
            print(f"[TEST] 创建 sanguo 文件，大小={sanguo_file.stat().st_size} bytes（来自 .sl）")
        else:
            sanguo_file.write_bytes(b'\x00' * sanguo_file_size)
            print(f"[TEST] 创建空 sanguo 文件，大小={sanguo_file_size} bytes")
    else:
        sanguo_file.write_bytes(b'')
        print("[TEST] 创建空 sanguo 文件，大小=0 bytes")

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
    cmdline = f'"{game_path}" {selected_map} MemoryMapName=sanguo'

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
    time.sleep(10)

    # 分析日志
    log_dirs = sorted([d for d in game_dir.glob("log*") if d.is_dir()], key=lambda x: x.stat().st_mtime)
    if log_dirs:
        latest_log = log_dirs[-1]
        error_log = latest_log / "error.log"
        if error_log.exists():
            content = error_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] error.log: {content[:300]}")
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
    # 测试1: 空 sanguo 文件
    print("=" * 60)
    print("测试 1: 空 sanguo 文件")
    print("=" * 60)
    success1 = test(sanguo_file_size=0)
    print(f"[TEST] 测试1: {'成功' if success1 else '失败'}")

    time.sleep(2)

    # 测试2: sanguo 文件填充 .sl 数据
    print()
    print("=" * 60)
    print("测试 2: sanguo 文件填充 .sl 数据")
    print("=" * 60)
    success2 = test(sanguo_file_size=1024*1024)
    print(f"[TEST] 测试2: {'成功' if success2 else '失败'}")

    # 清理 sanguo 文件
    sanguo_file = Path(__file__).parent / "data" / "sanguo"
    if sanguo_file.exists():
        sanguo_file.unlink()
        print("[TEST] 已删除 sanguo 文件")

    sys.exit(0 if (success1 or success2) else 1)
