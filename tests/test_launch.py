# -*- coding: utf-8 -*-
"""自动测试脚本 - 直接调用 launch_game 启动地图并检查日志."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QWidget
from src.launcher.game_launcher import launch_game
from src.data.map_data import DEFAULT_MAP_OPTIONS

def test_launch():
    app = QApplication(sys.argv)
    parent = QWidget()

    game_dir = Path(__file__).parent / "data"
    selected_map = 10002
    map_offset = selected_map - 10000
    options = DEFAULT_MAP_OPTIONS.get(map_offset, [-1] * 10 + [0])

    print(f"[TEST] 启动地图: {selected_map}")
    print(f"[TEST] 选项: {options}")
    print(f"[TEST] 游戏目录: {game_dir}")

    # Launch the game
    result = launch_game(
        parent=parent,
        selected_map=selected_map,
        game_dir=game_dir,
        current_options={map_offset: options},
        resolution_index=1,  # 窗口模式
    )

    print(f"[TEST] launch_game 返回: {result}")

    if result:
        # Wait for game to start and potentially crash
        print("[TEST] 等待 5 秒让游戏启动...")
        time.sleep(5)

        # Check for new log directories
        log_dirs = sorted([d for d in game_dir.glob("log*") if d.is_dir()], key=lambda x: x.stat().st_mtime)
        if log_dirs:
            latest_log = log_dirs[-1]
            print(f"[TEST] 最新日志目录: {latest_log.name}")

            error_log = latest_log / "error.log"
            init_log = latest_log / "init.log"

            if error_log.exists():
                content = error_log.read_text(encoding="gbk", errors="ignore")
                print(f"[TEST] error.log 内容:\n{content}")
                if "tab_interface" in content:
                    print("[TEST] ❌ 检测到 tab_interface 错误!")
                    return False
                elif content.strip():
                    print("[TEST] ⚠️ error.log 有其他错误")
                    return False
                else:
                    print("[TEST] ✅ error.log 为空")
                    return True
            else:
                print("[TEST] ✅ 没有 error.log (游戏可能正常运行)")
                return True
        else:
            print("[TEST] ⚠️ 未找到日志目录")
            return False
    else:
        print("[TEST] ❌ launch_game 返回 False")
        return False

if __name__ == "__main__":
    success = test_launch()
    sys.exit(0 if success else 1)
