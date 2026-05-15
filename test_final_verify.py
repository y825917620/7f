# -*- coding: utf-8 -*-
"""最终验证：测试新构建的 launcher 是否能正常启动游戏."""

import shutil
import subprocess
import sys
import time
from pathlib import Path


def test():
    game_dir = Path(__file__).parent / "data"
    launcher_exe = game_dir / "神龙地图启动器.exe"

    if not launcher_exe.exists():
        print(f"[TEST] Launcher 不存在: {launcher_exe}")
        return False

    # 记录启动前的日志目录
    before_logs = set(d.name for d in game_dir.glob("log*") if d.is_dir())
    print(f"[TEST] 启动前日志数: {len(before_logs)}")

    # 启动 launcher
    print(f"[TEST] 启动 launcher: {launcher_exe}")
    proc = subprocess.Popen(
        [str(launcher_exe)],
        cwd=str(game_dir),
    )
    print(f"[TEST] Launcher PID={proc.pid}")

    # 等待窗口加载
    time.sleep(5)

    try:
        from pywinauto import Application, Desktop

        # 通过窗口标题连接
        print("[TEST] 查找窗口...")
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
                if "启动游戏" in text:
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

    success = False
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

            # 检查是否进入主循环
            if "begin load map" in content:
                print("[TEST] ✓ 游戏成功进入地图加载!")
                success = True
            else:
                print("[TEST] ✗ 游戏未进入地图加载")

        error_log = log_dir / "error.log"
        if error_log.exists():
            content = error_log.read_text(encoding="gbk", errors="ignore")
            print(f"[TEST] error.log ({len(content)} bytes):")
            print(content[:500])
        else:
            print("[TEST] 无 error.log")

    # 关闭 launcher
    try:
        proc.terminate()
        print("[TEST] 已终止 launcher")
    except:
        pass

    return success


if __name__ == "__main__":
    success = test()
    print(f"\n[TEST] 最终结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1)
