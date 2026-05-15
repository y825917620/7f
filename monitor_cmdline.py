# -*- coding: utf-8 -*-
import psutil
import time

seen = set()
for _ in range(60):
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        if p.info['name'] == 'game.exe' and p.info['pid'] not in seen:
            seen.add(p.info['pid'])
            print(f"[FOUND] PID={p.info['pid']} cmdline={p.info['cmdline']}")
    time.sleep(0.5)
