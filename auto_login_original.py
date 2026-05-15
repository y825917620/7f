# -*- coding: utf-8 -*-
"""自动点击原启动器的登录按钮并观察."""

import os
import subprocess
import sys
import time
from pathlib import Path

launcher_exe = Path(r"E:\玩家原创\神龙地图启动器\data\神龙地图启动器.exe")
game_dir = launcher_exe.parent

proc = subprocess.Popen([str(launcher_exe)], cwd=str(game_dir))
print(f"[INFO] 启动器 PID={proc.pid}")
print("[INFO] 等待 5 秒让窗口加载...")
time.sleep(5)

try:
    from pywinauto import Application

    app = Application(backend="uia").connect(process=proc.pid)
    windows = app.windows()
    print(f"[INFO] 窗口数: {len(windows)}")
    for w in windows:
        print(f"  - '{w.window_text()}' class={w.class_name()}")

    if not windows:
        print("[ERROR] 未找到窗口")
        sys.exit(1)

    dlg = app.window(handle=windows[0].handle)

    # 尝试填写账号密码（空或 test）
    try:
        account = dlg.child_window(auto_id="1048", control_type="Edit")
        if account.exists():
            account.set_text("test")
            print("[INFO] 已填写账号: test")
    except Exception as e:
        print(f"[WARN] 填写账号失败: {e}")

    try:
        password = dlg.child_window(auto_id="1049", control_type="Edit")
        if password.exists():
            password.set_text("test")
            print("[INFO] 已填写密码: test")
    except Exception as e:
        print(f"[WARN] 填写密码失败: {e}")

    # 点击登录按钮
    try:
        login_btn = dlg.child_window(auto_id="1029", control_type="Button")
        if login_btn.exists():
            print(f"[INFO] 点击登录按钮: '{login_btn.window_text()}'")
            login_btn.click()
        else:
            print("[WARN] 未找到登录按钮")
    except Exception as e:
        print(f"[ERROR] 点击登录失败: {e}")

    print("[INFO] 等待 10 秒观察...")
    time.sleep(10)

    # 检查是否有 game.exe 启动
    import psutil
    game_procs = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) if p.info['name'] == 'game.exe']
    print(f"[INFO] game.exe 进程: {[p.info['pid'] for p in game_procs]}")
    for p in game_procs:
        try:
            print(f"[INFO] game.exe cmdline: {p.info['cmdline']}")
        except:
            pass

    # 检查 sl 目录
    print(f"[INFO] sl exists: {os.path.exists(str(game_dir / 'sl'))}")

    # 列出 data_test 或当前目录的日志
    for d in sorted(game_dir.glob("log*"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
        if d.is_dir():
            init_log = d / "init.log"
            if init_log.exists():
                content = init_log.read_text(encoding="gbk", errors="ignore")
                has_sanguo = "do [map/sanguo/sanguo.o] ok!" in content
                print(f"[INFO] 日志 {d.name}: sanguo.o={has_sanguo}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n[INFO] 等待 5 秒后关闭...")
    time.sleep(5)
    proc.terminate()
    print("[INFO] 已终止")
    sys.exit(0)
