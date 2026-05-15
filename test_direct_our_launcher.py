# -*- coding: utf-8 -*-
"""直接测试 - 使用我们的 launcher 逻辑启动地图 10002（窗口模式，命令行直接运行）."""

import ctypes
import os
import struct
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.config_generator import generate_config_lua, generate_edt2_lua, generate_map_opt_lua
from src.data.map_data import DEFAULT_MAP_OPTIONS
from src.launcher.game_settings import update_game_setting

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器5.2\data")
MAP_ID = 10002


def find_luac():
    candidates = [
        GAME_DIR.parent / "lua51_bin" / "luac5.1.exe",
        GAME_DIR / "lua51_bin" / "luac5.1.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def compile_lua(src, output_path, luac_path):
    tmp = output_path.with_suffix(".lua.tmp")
    try:
        tmp.write_text(src, encoding="gbk")
        r = subprocess.run([str(luac_path), "-s", "-o", str(output_path), str(tmp)], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[WARN] luac failed: {r.stderr}")
            return False
        print(f"[INFO] Compiled {output_path.name}: {output_path.stat().st_size} bytes")
        return True
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def launch():
    kernel32 = ctypes.windll.kernel32

    kernel32.CreateMutexA.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCSTR]
    kernel32.CreateMutexA.restype = wintypes.HANDLE

    kernel32.CreateFileMappingA.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.LPCSTR]
    kernel32.CreateFileMappingA.restype = wintypes.HANDLE

    kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
    kernel32.MapViewOfFile.restype = wintypes.LPVOID

    kernel32.UnmapViewOfFile.argtypes = [wintypes.LPVOID]
    kernel32.UnmapViewOfFile.restype = wintypes.BOOL

    hMutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")
    print(f"[INFO] Mutex: {hMutex}")

    hStart = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 512, b"7fgame_game_client_start_info")
    if hStart:
        ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
        if ptr:
            ctypes.memset(ptr, 0, 512)
            ctypes.c_uint32.from_address(ptr).value = MAP_ID
            kernel32.UnmapViewOfFile(ptr)
        print("[INFO] Shared memory start_info created")

    hLogin = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 256, b"7fgame_game_client_login")
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

    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 3
    hNul = kernel32.CreateFileA(b"NUL", GENERIC_WRITE, 3, None, OPEN_EXISTING, 0x80, None)

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
    if hNul:
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
        print("[WARN] No log dirs found")
        return False

    latest = log_dirs[0]
    print(f"\n[INFO] Analyzing log: {latest.name}")

    init_log = latest / "init.log"
    if init_log.exists():
        content = init_log.read_text(encoding="gbk", errors="ignore")
        print(f"[INFO] init.log size: {len(content)} bytes")

        has_sanguo_o = "do [map/sanguo/sanguo.o] ok!" in content
        has_begin_load = "begin load map[sanguo]" in content
        after_count = content.count("enter:AfterRunGameLogic")
        render_count = content.count("enter:Render")

        print(f"[INFO] do [map/sanguo/sanguo.o] ok! = {has_sanguo_o}")
        print(f"[INFO] begin load map[sanguo] = {has_begin_load}")
        print(f"[INFO] AfterRunGameLogic count = {after_count}")
        print(f"[INFO] Render count = {render_count}")

        lines = content.strip().split("\n")
        print("\n--- tail ---")
        for line in lines[-20:]:
            print(line)
        print("---")

        if has_sanguo_o and after_count > 2 and render_count > 2:
            print("\n[OK] Map script loaded, game entered main loop!")
            return True
        elif not has_sanguo_o and has_begin_load:
            print("\n[FAIL] Game entered map but sanguo.o not loaded")
            return False
        else:
            print("\n[FAIL] Game did not enter map main loop normally")
            return False
    else:
        print("[WARN] init.log not found")
        return False


def main():
    print("=" * 60)
    print("Test: our launcher logic -> map 10002 (window mode)")
    print("=" * 60)

    luac = find_luac()
    if not luac:
        print("[ERROR] luac5.1.exe not found")
        sys.exit(1)
    print(f"[INFO] luac: {luac}")

    before = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    print(f"[INFO] Log dirs before: {len(before)}")

    # Generate config.lua
    map_offset = MAP_ID - 10000
    options = DEFAULT_MAP_OPTIONS.get(map_offset, [-1] * 10 + [0])
    config_lua = generate_config_lua(MAP_ID, options, game_dir=GAME_DIR)
    (GAME_DIR / "config.lua").write_text(config_lua, encoding="gbk")
    print(f"[INFO] config.lua written")

    # Generate and compile edt2.o
    edt2_lua = generate_edt2_lua(MAP_ID, options, game_dir=GAME_DIR)
    edt2_path = GAME_DIR / "core" / "edt2.o"
    if edt2_path.exists():
        edt2_path.unlink()
    compile_lua(edt2_lua, edt2_path, luac)

    # Generate and compile map.o
    g_map_opt = dict(DEFAULT_MAP_OPTIONS)
    map_lua = generate_map_opt_lua(1, g_map_opt)
    map_o_path = GAME_DIR / "map.o"
    if map_o_path.exists():
        map_o_path.unlink()
    compile_lua(map_lua, map_o_path, luac)

    # GameSetting.inf (resolution index 0 = default/window)
    update_game_setting(GAME_DIR, 0)
    print("[INFO] GameSetting.inf updated")

    hProc = launch()
    if not hProc:
        sys.exit(1)

    print("[INFO] Waiting 15 seconds for game to run...")
    time.sleep(15)

    after = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    new = after - before
    print(f"[INFO] New log dirs: {new}")

    success = analyze_logs()

    kernel32 = ctypes.windll.kernel32
    kernel32.TerminateProcess(hProc, 0)
    kernel32.CloseHandle(hProc)
    print("[INFO] Game process terminated")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
