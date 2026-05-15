# -*- coding: utf-8 -*-
"""自动化测试：启动原启动器，检测窗口并尝试启动游戏."""

import os
import subprocess
import sys
import time
from pathlib import Path


def test():
    game_dir = Path(__file__).parent / "data_test"
    launcher_exe = game_dir / "神龙地图启动器.exe"

    if not launcher_exe.exists():
        print(f"[TEST] 原启动器不存在: {launcher_exe}")
        return False

    # 记录启动前的日志目录
    before_logs = set(d.name for d in game_dir.glob("log*") if d.is_dir())
    print(f"[TEST] 启动前日志数: {len(before_logs)}")

    # 启动原启动器
    print(f"[TEST] 启动原启动器...")
    proc = subprocess.Popen(
        [str(launcher_exe)],
        cwd=str(game_dir),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    print(f"[TEST] 原启动器 PID={proc.pid}")

    # 等待窗口加载
    time.sleep(5)

    try:
        from pywinauto import Desktop

        # 列出所有顶层窗口
        print("[TEST] 查找所有窗口...")
        windows = Desktop(backend="uia").windows()
        for w in windows:
            try:
                title = w.window_text()
                class_name = w.class_name()
                pid = w.process_id()
                if pid == proc.pid or "神龙" in title or "地图" in title:
                    print(f"  窗口: title='{title}', class='{class_name}', pid={pid}")
            except:
                pass

        # 尝试通过进程找到窗口
        print("[TEST] 尝试连接进程窗口...")
        from pywinauto import Application
        app = Application(backend="uia").connect(process=proc.pid)
        top_windows = app.windows()
        print(f"[TEST] 进程窗口: {top_windows}")

        if top_windows:
            dlg = top_windows[0]
            print(f"[TEST] 主窗口标题: {dlg.window_text()}")
            print(f"[TEST] 主窗口类名: {dlg.class_name()}")

            # 等待一下
            time.sleep(2)

            # 查找所有按钮
            print("[TEST] 查找按钮...")
            buttons = dlg.descendants(control_type="Button")
            for btn in buttons:
                try:
                    text = btn.window_text()
                    print(f"  按钮: '{text}'")
                except:
                    pass

            # 尝试点击包含"启动"的按钮
            for btn in buttons:
                try:
                    text = btn.window_text()
                    if "启动" in text or "游戏" in text:
                        print(f"[TEST] 点击按钮: '{text}'")
                        btn.click()
                        break
                except:
                    pass

    except Exception as e:
        print(f"[TEST] 自动化失败: {e}")
        import traceback
        traceback.print_exc()

    # 等待游戏启动
    time.sleep(15)

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
        proc.terminate()
        print("[TEST] 已终止原启动器")
    except:
        pass

    return True


if __name__ == "__main__":
    test()
