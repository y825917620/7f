# -*- coding: utf-8 -*-
"""直接命令行测试 - 绕过GUI，直接启动地图10002（窗口模式）"""

import ctypes
import os
import struct
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

# 将 src 加入路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config_generator import generate_config_lua, generate_edt2_lua, generate_map_opt_lua
from src.data.map_data import DEFAULT_MAP_OPTIONS

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器5.2\data")
MAP_ID = 10002


def _find_luac():
    candidates = [
        GAME_DIR.parent / "lua51_bin" / "luac5.1.exe",
        GAME_DIR / ".." / "lua51_bin" / "luac5.1.exe",
        GAME_DIR / "lua51_bin" / "luac5.1.exe",
    ]
    for c in candidates:
        resolved = c.resolve()
        if resolved.exists():
            return resolved
    return None


def _compile_lua(src, output_path, luac_path):
    tmp = output_path.with_suffix(".lua.tmp")
    try:
        tmp.write_text(src, encoding="gbk")
        r = subprocess.run(
            [str(luac_path), "-s", "-o", str(output_path), str(tmp)],
            capture_output=True, text=True,
        )
        return r.returncode == 0
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def prepare_files():
    """准备 config.lua, edt2.o, map.o, GameSetting.inf"""
    luac = _find_luac()
    if not luac:
        print("[ERROR] 找不到 luac5.1.exe")
        return False

    map_offset = MAP_ID - 10000
    options = DEFAULT_MAP_OPTIONS.get(map_offset, [-1] * 10 + [0])

    # 1. config.lua
    config_lua = generate_config_lua(MAP_ID, options, game_dir=GAME_DIR)
    (GAME_DIR / "config.lua").write_text(config_lua, encoding="gbk")
    print(f"[INFO] config.lua: {config_lua}")

    # 2. edt2.o
    edt2_lua = generate_edt2_lua(MAP_ID, options, game_dir=GAME_DIR)
    edt2_path = GAME_DIR / "core" / "edt2.o"
    if edt2_path.exists():
        edt2_path.unlink()
    ok = _compile_lua(edt2_lua, edt2_path, luac)
    print(f"[INFO] edt2.o compiled: {ok}, size={edt2_path.stat().st_size if edt2_path.exists() else 0}")

    # 3. map.o
    g_map_opt = dict(DEFAULT_MAP_OPTIONS)
    lua_src = generate_map_opt_lua(1, g_map_opt)
    map_o_path = GAME_DIR / "map.o"
    if map_o_path.exists():
        map_o_path.unlink()
    ok = _compile_lua(lua_src, map_o_path, luac)
    print(f"[INFO] map.o compiled: {ok}, size={map_o_path.stat().st_size if map_o_path.exists() else 0}")

    # 4. GameSetting.inf (窗口模式: 第21行=1)
    setting_path = GAME_DIR / "GameSetting.inf"
    lines = [
        "1", "0", "1", "1", "42", "0", "43", "10", "3",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "1"
    ]
    setting_path.write_text("\n".join(lines) + "\n", encoding="gbk")
    print("[INFO] GameSetting.inf written")

    # 5. 清理可能干扰的 sl/ 目录
    sl_dir = GAME_DIR / "sl"
    if sl_dir.exists():
        import shutil
        shutil.rmtree(sl_dir)
        print("[INFO] 已清理 sl/ 目录")

    return True


def launch():
    kernel32 = ctypes.windll.kernel32

    # 必须正确设置 64 位 ctypes 类型，否则指针被截断导致访问冲突
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

    # 互斥锁
    hMutex = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")
    print(f"[INFO] Mutex: {hMutex}")

    # 共享内存 start_info
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

    # 共享内存 login
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

    # 设置 PATH
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
    """查找并分析最新日志"""
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

        # 打印关键尾部
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
    print("直接命令行测试 - 地图 10002 (窗口模式)")
    print("=" * 60)

    # 记录启动前已有的日志目录
    before = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    print(f"[INFO] 启动前日志数: {len(before)}")

    if not prepare_files():
        sys.exit(1)

    hProc = launch()
    if not hProc:
        sys.exit(1)

    print("[INFO] 等待 15 秒让游戏运行...")
    time.sleep(15)

    # 检查新日志
    after = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    new = after - before
    print(f"[INFO] 新日志目录: {new}")

    success = analyze_logs()

    # 尝试关闭游戏进程
    kernel32 = ctypes.windll.kernel32
    kernel32.TerminateProcess(hProc, 0)
    kernel32.CloseHandle(hProc)
    print("[INFO] 已终止游戏进程")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
