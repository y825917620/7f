# -*- coding: utf-8 -*-
"""自动化测试：启动新启动器，自动选择地图并启动游戏."""

import subprocess
import sys
import time
from pathlib import Path


def test():
    game_dir = Path(__file__).parent / "data"
    launcher_exe = game_dir / "神龙地图启动器_new.exe"

    if not launcher_exe.exists():
        print(f"[TEST] 新启动器不存在: {launcher_exe}")
        # 尝试 data_test
        launcher_exe = Path(__file__).parent / "data_test" / "神龙地图启动器_new.exe"
        if not launcher_exe.exists():
            print(f"[TEST] data_test 中也没有")
            return False

    # 记录启动前的日志目录
    before_logs = set(d.name for d in game_dir.glob("log*") if d.is_dir())
    print(f"[TEST] 启动前日志数: {len(before_logs)}")

    # 启动新启动器
    print(f"[TEST] 启动新启动器: {launcher_exe}")
    proc = subprocess.Popen(
        [str(launcher_exe)],
        cwd=str(game_dir),
    )
    print(f"[TEST] 新启动器 PID={proc.pid}")

    # 等待窗口加载
    time.sleep(5)

    try:
        from pywinauto import Application, Desktop

        # 通过窗口标题连接
        print("[TEST] 查找窗口...")
        desktop = Desktop(backend="uia")
        for w in desktop.windows():
            try:
                title = w.window_text()
                if "神龙地图" in title or "7F555" in title:
                    print(f"  找到窗口: '{title}', pid={w.process_id()}")
            except:
                pass

        # 尝试连接
        app = Application(backend="uia").connect(title_re=".*神龙地图.*", found_index=0)
        dlg = app.window(title_re=".*神龙地图.*")
        print(f"[TEST] 已连接窗口: {dlg.window_text()}")

        # 等待窗口完全加载
        time.sleep(2)

        # 查找地图列表并选择第一个地图
        print("[TEST] 查找地图列表...")
        list_widget = dlg.child_window(auto_id="map_list", control_type="List")
        if list_widget.exists():
            items = list_widget.children(control_type="ListItem")
            if items:
                print(f"[TEST] 选择地图: {items[0].window_text()}")
                items[0].click()
                time.sleep(1)

        # 查找启动按钮
        print("[TEST] 查找启动按钮...")
        for btn in dlg.descendants(control_type="Button"):
            try:
                text = btn.window_text()
                print(f"  按钮: '{text}'")
                if "启动" in text:
                    print(f"[TEST] 点击: '{text}'")
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

    # 关闭启动器
    try:
        proc.terminate()
        print("[TEST] 已终止启动器")
    except:
        pass

    return True


if __name__ == "__main__":
    test()
