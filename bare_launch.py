# -*- coding: utf-8 -*-
"""最简启动 — 只用 CreateProcess + map_id，无 SHM / 管道 / NUL."""

import sys, os, time, ctypes
from ctypes import wintypes
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from src.launcher.log_verifier import LogVerifier

def main():
    game_dir = project_root / "data"
    map_id = 10002
    kernel32 = ctypes.windll.kernel32

    # 互斥体
    kernel32.CreateMutexA.restype = wintypes.HANDLE
    kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

    # PATH
    os.environ["PATH"] = str(game_dir / "core") + os.pathsep + os.environ.get("PATH", "")

    # STARTUPINFO (最简)
    class SI(ctypes.Structure):
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
    class PI(ctypes.Structure):
        _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
                     ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

    game_exe = game_dir / "core" / "game.exe"
    cmdline = f'"{game_exe}" {map_id}'

    si = SI()
    si.cb = ctypes.sizeof(si)
    # 不设 dwFlags，不设 hStd*，不设 SHM，不设管道

    pi = PI()
    ok = kernel32.CreateProcessA(
        str(game_exe).encode("mbcs"), cmdline.encode("mbcs"),
        None, None, False, 0, None,
        str(game_dir).encode("mbcs"),
        ctypes.byref(si), ctypes.byref(pi)
    )
    if not ok:
        print(f"CreateProcess 失败: {kernel32.GetLastError()}")
        return 1

    pid = pi.dwProcessId
    kernel32.CloseHandle(pi.hThread)
    print(f"[最简启动] PID={pid}")

    time.sleep(3)
    verifier = LogVerifier(game_dir)

    # 等待日志
    diag = None
    for _ in range(15):
        log_dir = verifier.find_latest_log_dir()
        if log_dir and str(pid) in str(log_dir):
            diag = verifier.verify(expected_map_id=map_id, log_dir=log_dir)
            break
        time.sleep(1)

    if diag is None:
        print("未找到日志目录")
        return 1

    print(f"日志: {diag.get('log_dir')}")
    print(f"sanguo.o: {diag.get('has_sanguo_o')}")
    print(f"失败: {diag.get('failure_kind')}")
    print(f"错误: {'; '.join(diag['errors']) if diag['errors'] else '无'}")

    if diag.get("ok"):
        print("\n✅ 成功！")
        return 0
    else:
        # 关键日志行
        log_dir = Path(diag["log_dir"])
        ip = log_dir / "init.log"
        if ip.exists():
            for line in ip.read_text(encoding="gbk", errors="ignore").splitlines():
                if any(k in line for k in ["sanguo.o", "gpi.o", "AfterRun", "Render", "读取地图", "设置读取", "Creat_Reconnect"]):
                    print(f"  {line.strip()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
