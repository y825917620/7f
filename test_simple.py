# -*- coding: utf-8 -*-
"""最简测试 - 直接运行 game.exe 10002，不做任何特殊处理"""

import os
import subprocess
import sys
import time
from pathlib import Path

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器5.2\data")
MAP_ID = 10002


def main():
    print("=" * 60)
    print("最简测试: 直接 subprocess.Popen game.exe 10002")
    print("=" * 60)

    before = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    print(f"[INFO] 启动前日志数: {len(before)}")

    game_exe = GAME_DIR / "core" / "game.exe"
    core_dir = str(GAME_DIR / "core")
    os.environ["PATH"] = core_dir + os.pathsep + os.environ.get("PATH", "")

    # 直接启动，不设置互斥锁、共享内存、管道
    proc = subprocess.Popen(
        [str(game_exe), str(MAP_ID)],
        cwd=str(GAME_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[INFO] Game started PID={proc.pid}")

    print("[INFO] 等待 15 秒...")
    time.sleep(15)

    after = set(d.name for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr")
    new = after - before
    print(f"[INFO] 新日志目录: {new}")

    # 分析日志
    log_dirs = sorted([d for d in GAME_DIR.glob("log*") if d.is_dir() and d.name != "log_mgr"], key=lambda x: x.stat().st_mtime, reverse=True)
    if log_dirs:
        latest = log_dirs[0]
        init_log = latest / "init.log"
        if init_log.exists():
            content = init_log.read_text(encoding="gbk", errors="ignore")
            print(f"[INFO] init.log: {len(content)} bytes")
            has_sanguo_o = "do [map/sanguo/sanguo.o] ok!" in content
            has_begin_load = "begin load map[sanguo]" in content
            after_count = content.count("enter:AfterRunGameLogic")
            render_count = content.count("enter:Render")
            print(f"[INFO] sanguo.o = {has_sanguo_o}, begin_load = {has_begin_load}, After={after_count}, Render={render_count}")
            for line in content.strip().split("\n")[-15:]:
                print(line)

    proc.terminate()
    print("[INFO] 已终止")


if __name__ == "__main__":
    main()
