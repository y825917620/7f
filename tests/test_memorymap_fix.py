# -*- coding: utf-8 -*-
"""测试：创建 sanguo 共享内存映射，配合 MemoryMapName=sanguo 启动游戏."""

import ctypes
import os
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

kernel32 = ctypes.windll.kernel32


def test(mapping_size=1024*1024, fill_with_sl=False):
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
        print("[TEST] 已删除空 sl/ 目录")

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

    # 1. start_info 共享内存
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

    # 2. login 共享内存
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

    # 3. sanguo 共享内存（关键修复尝试）
    print(f"[TEST] 创建 sanguo 共享内存，大小={mapping_size} bytes")
    hSanguo = kernel32.CreateFileMappingA(
        wintypes.HANDLE(-1), None, 0x04, 0, mapping_size,
        b"sanguo"
    )
    if hSanguo:
        ptr = kernel32.MapViewOfFile(hSanguo, 0xF001F, 0, 0, mapping_size)
        if ptr:
            ctypes.memset(ptr, 0, mapping_size)
            if fill_with_sl:
                # 尝试填充 .sl 文件数据
                sl_file = game_dir / "map" / f"{selected_map}.sl"
                if sl_file.exists():
                    sl_data = sl_file.read_bytes()
                    to_write = min(len(sl_data), mapping_size)
                    ctypes.memmove(ptr, sl_data, to_write)
                    print(f"[TEST] 已填充 {to_write} bytes 的 .sl 数据到 sanguo 映射")
                else:
                    print(f"[TEST] 未找到 {sl_file}")
            else:
                print("[TEST] sanguo 映射已清零（空映射）")
            kernel32.UnmapViewOfFile(ptr)
    else:
        err = kernel32.GetLastError()
        print(f"[TEST] 创建 sanguo 映射失败，错误码={err}")

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
    print(f"[TEST] 工作目录: {work_dir}")

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
        print(f"[TEST] 最新日志目录: {latest_log.name}")

        # init.log
        init_log = latest_log / "init.log"
        if init_log.exists():
            content = init_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] init.log 大小: {len(content)} bytes")
            last_lines = content.strip().split("\n")[-5:]
            for line in last_lines:
                print(f"  {line}")

        # error.log
        error_log = latest_log / "error.log"
        if error_log.exists():
            content = error_log.read_text(encoding="gbk", errors="ignore")
            if content.strip():
                print(f"[TEST] error.log: {content[:300]}")
                if "tab_interface" in content:
                    print("[TEST] 结果: 仍然有 tab_interface 错误!")
                    return False
                else:
                    print("[TEST] 结果: 无 tab_interface 错误")
            else:
                print("[TEST] 结果: error.log 为空!")
        else:
            print("[TEST] 结果: 无 error.log!")

        # net_state.log
        net_log = latest_log / "net_state.log"
        if net_log.exists():
            content = net_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] net_state.log:")
            for line in content.strip().split("\n")[-5:]:
                print(f"  {line}")
            if "内存映射失败" in content:
                print("[TEST] 结果: 内存映射仍然失败")
                return False
    else:
        print("[TEST] 无日志目录!")

    return True


if __name__ == "__main__":
    # 先测试空映射
    print("=" * 60)
    print("测试 1: 空 sanguo 映射")
    print("=" * 60)
    success1 = test(mapping_size=1024*1024, fill_with_sl=False)
    print(f"[TEST] 测试1: {'成功' if success1 else '失败'}")

    # 等待进程退出
    time.sleep(2)

    # 再测试填充 .sl 数据的映射
    print()
    print("=" * 60)
    print("测试 2: 填充 .sl 数据的 sanguo 映射")
    print("=" * 60)
    success2 = test(mapping_size=6*1024*1024, fill_with_sl=True)
    print(f"[TEST] 测试2: {'成功' if success2 else '失败'}")

    sys.exit(0 if (success1 or success2) else 1)
