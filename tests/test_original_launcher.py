# -*- coding: utf-8 -*-
"""测试：直接运行原启动器，观察其行为."""

import ctypes
import os
import shutil
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

import psutil

kernel32 = ctypes.windll.kernel32


def get_latest_log_dir(game_dir):
    log_dirs = sorted([d for d in game_dir.glob("log*") if d.is_dir()],
                      key=lambda x: x.stat().st_mtime)
    return log_dirs[-1] if log_dirs else None


def test():
    game_dir = Path(__file__).parent / "data_test"
    launcher_exe = game_dir / "神龙地图启动器.exe"

    if not launcher_exe.exists():
        print(f"[TEST] 原启动器不存在: {launcher_exe}")
        return False

    # 记录启动前的日志目录
    before_logs = set(d.name for d in game_dir.glob("log*") if d.is_dir())
    print(f"[TEST] 启动前日志数: {len(before_logs)}")

    # 创建进程启动原启动器
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

    si = STARTUPINFOA()
    si.cb = ctypes.sizeof(STARTUPINFOA)
    si.dwFlags = 0x1  # STARTF_USESHOWWINDOW
    si.wShowWindow = 0  # SW_HIDE - 隐藏窗口

    pi = PROCESS_INFORMATION()
    work_dir = str(game_dir)
    cmdline = f'"{launcher_exe}"'

    print(f"[TEST] 启动原启动器: {cmdline}")
    print(f"[TEST] 工作目录: {work_dir}")

    ok = kernel32.CreateProcessA(
        str(launcher_exe).encode("mbcs"), cmdline.encode("mbcs"),
        None, None, False, 0, None, work_dir.encode("mbcs"),
        ctypes.byref(si), ctypes.byref(pi)
    )
    if not ok:
        err = kernel32.GetLastError()
        print(f"[TEST] CreateProcessA 失败 (错误码: {err})")
        return False

    print(f"[TEST] 原启动器 PID={pi.dwProcessId}")
    kernel32.CloseHandle(pi.hThread)

    # 等待一段时间，看是否创建子进程
    time.sleep(5)

    # 查找 game.exe 子进程
    game_pids = []
    for p in psutil.process_iter(['pid', 'ppid', 'name']):
        try:
            if p.info['name'] == 'game.exe':
                game_pids.append((p.info['pid'], p.info['ppid']))
        except:
            pass

    print(f"[TEST] 找到的 game.exe 进程: {game_pids}")

    # 检查新日志
    after_logs = set(d.name for d in game_dir.glob("log*") if d.is_dir())
    new_logs = after_logs - before_logs
    print(f"[TEST] 新日志目录: {new_logs}")

    for log_name in new_logs:
        log_dir = game_dir / log_name
        print(f"\n[TEST] 分析日志: {log_name}")

        init_log = log_dir / "init.log"
        if init_log.exists():
            content = init_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] init.log: {len(content)} bytes")
            lines = content.strip().split("\n")
            for line in lines[-15:]:
                print(f"  {line}")

        error_log = log_dir / "error.log"
        if error_log.exists():
            content = error_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] error.log ({len(content)} bytes):")
            print(content[:500])
        else:
            print("[TEST] 无 error.log")

    # 关闭原启动器
    try:
        p = psutil.Process(pi.dwProcessId)
        p.terminate()
        print(f"[TEST] 已终止原启动器")
    except:
        pass

    kernel32.CloseHandle(pi.hProcess)
    return True


if __name__ == "__main__":
    test()
