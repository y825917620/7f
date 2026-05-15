# -*- coding: utf-8 -*-
"""直接测试 - 使用原始的 core/edt2.o 替换我们编译的，看能否正常启动"""

import ctypes
import os
import shutil
import struct
import sys
import time
from ctypes import wintypes
from pathlib import Path

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器5.2\data")
ORIG_GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器\data")
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

    hMutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")
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
    print("测试：使用原始 edt2.o 启动地图 10002")
    print("=" * 60)

    before = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    print(f"[INFO] 启动前日志数: {len(before)}")

    # 1. 直接复制原始目录的所有关键文件（排除日志和启动器自身）
    # 我们只替换 core/edt2.o，但保留我们的 config.lua 和 map.o
    orig_edt2 = ORIG_GAME_DIR / "core" / "edt2.o"
    our_edt2 = GAME_DIR / "core" / "edt2.o"

    # 备份我们的 edt2.o
    backup = our_edt2.with_suffix(".o.bak")
    if our_edt2.exists():
        shutil.copy2(our_edt2, backup)

    # 复制原始 edt2.o
    shutil.copy2(orig_edt2, our_edt2)
    print(f"[INFO] 已复制原始 edt2.o ({orig_edt2.stat().st_size} bytes) -> {our_edt2}")

    # 同时复制原始 config.lua（如果有）
    orig_config = ORIG_GAME_DIR / "config.lua"
    if orig_config.exists():
        shutil.copy2(orig_config, GAME_DIR / "config.lua")
        print(f"[INFO] 已复制原始 config.lua")

    # 同时复制原始 GameSetting.inf
    orig_setting = ORIG_GAME_DIR / "GameSetting.inf"
    if orig_setting.exists():
        shutil.copy2(orig_setting, GAME_DIR / "GameSetting.inf")
        print(f"[INFO] 已复制原始 GameSetting.inf")

    # 清理 sl/
    sl_dir = GAME_DIR / "sl"
    if sl_dir.exists():
        shutil.rmtree(sl_dir)
        print("[INFO] 已清理 sl/ 目录")

    # 不生成我们的 map.o，让游戏自己处理（或复制原始map.o如果存在）
    # 原始目录应该没有 map.o，因为它是动态生成的
    our_map_o = GAME_DIR / "map.o"
    if our_map_o.exists():
        our_map_o.unlink()
        print("[INFO] 已删除我们的 map.o")

    hProc = launch()
    if not hProc:
        sys.exit(1)

    print("[INFO] 等待 15 秒让游戏运行...")
    time.sleep(15)

    after = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    new = after - before
    print(f"[INFO] 新日志目录: {new}")

    success = analyze_logs()

    # 恢复我们的 edt2.o
    if backup.exists():
        shutil.copy2(backup, our_edt2)
        print("[INFO] 已恢复我们的 edt2.o")

    kernel32 = ctypes.windll.kernel32
    kernel32.TerminateProcess(hProc, 0)
    kernel32.CloseHandle(hProc)
    print("[INFO] 已终止游戏进程")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
