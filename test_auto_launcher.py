# -*- coding: utf-8 -*-
"""自动化测试：启动原启动器并自动点击"启动游戏"按钮."""

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
    time.sleep(3)

    try:
        from pywinauto import Application

        # 连接到原启动器窗口
        print("[TEST] 尝试连接窗口...")
        app = Application(backend="uia").connect(process=proc.pid)
        print(f"[TEST] 已连接，窗口列表: {app.windows()}")

        # 获取主窗口
        dlg = app.window(class_name="LauncherWindow")  # 猜测的类名
        print(f"[TEST] 主窗口: {dlg}")

        # 等待窗口完全加载
        time.sleep(2)

        # 查找"启动游戏"按钮并点击
        # 注意：实际的按钮文本可能不同
        btn = dlg.child_window(title="启动游戏", control_type="Button")
        if btn.exists():
            print("[TEST] 找到启动游戏按钮，点击...")
            btn.click()
        else:
            print("[TEST] 未找到启动游戏按钮，尝试查找其他按钮...")
            # 打印所有控件
            dlg.print_control_identifiers()

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
