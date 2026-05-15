# -*- coding: utf-8 -*-
"""Monitor game.exe command line when launched by original launcher."""

import psutil
import subprocess
import sys
import time
from pathlib import Path

launcher_exe = Path(r"E:\玩家原创\神龙地图启动器\data\神龙地图启动器.exe")
game_dir = launcher_exe.parent

# Start launcher
proc = subprocess.Popen([str(launcher_exe)], cwd=str(game_dir))
print(f"[INFO] Launcher PID={proc.pid}")

# Wait for game.exe to appear
found = False
timeout = 30
start = time.time()
while time.time() - start < timeout:
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        if p.info['name'] == 'game.exe':
            print(f"[FOUND] game.exe PID={p.info['pid']}")
            print(f"[FOUND] cmdline={p.info['cmdline']}")
            found = True
            break
    if found:
        break
    time.sleep(0.5)

if not found:
    print("[WARN] game.exe not found within timeout")

print("[INFO] Waiting 5s then terminating...")
time.sleep(5)
proc.terminate()
print("[INFO] Done")
