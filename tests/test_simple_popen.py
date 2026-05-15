# -*- coding: utf-8 -*-
"""最简单的 subprocess.Popen 测试 - 不使用 CreateProcessA、管道、共享内存."""

import os
import subprocess
import sys
import time
from pathlib import Path

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器\data")
MAP_ID = 10002

def main():
    game_exe = GAME_DIR / "core" / "game.exe"
    env = os.environ.copy()
    env["PATH"] = str(GAME_DIR / "core") + os.pathsep + env.get("PATH", "")

    print(f"[INFO] Launching {game_exe} {MAP_ID}")
    print(f"[INFO] cwd={GAME_DIR}")

    # Test with map name instead of ID
    proc = subprocess.Popen(
        [str(game_exe), "sanguo"],
        cwd=GAME_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[INFO] PID={proc.pid}")

    print("[INFO] Waiting 15s...")
    time.sleep(15)

    # Analyze logs
    log_dirs = sorted([d for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr"], key=lambda x: x.stat().st_mtime, reverse=True)
    if log_dirs:
        latest = log_dirs[0]
        init_log = latest / "init.log"
        if init_log.exists():
            content = init_log.read_text(encoding="gbk", errors="ignore")
            has_sanguo = "do [map/sanguo/sanguo.o] ok!" in content
            after = content.count("enter:AfterRunGameLogic")
            render = content.count("enter:Render")
            print(f"[INFO] sanguo.o={has_sanguo}, After={after}, Render={render}")
            for line in content.splitlines()[-10:]:
                print(line)

    proc.terminate()
    print("[INFO] Done")

if __name__ == "__main__":
    main()
