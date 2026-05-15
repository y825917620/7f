# -*- coding: utf-8 -*-
"""GameSetting.inf 读写工具"""

from pathlib import Path


def read_helper_from_setting(game_dir):
    """从 GameSetting.inf 读取 helper_get004/helper_get005 的值."""
    try:
        setting_path = Path(game_dir) / "GameSetting.inf"
        with open(setting_path, "r", encoding="gbk") as f:
            lines = [line.strip() for line in f.read().strip().splitlines()]
        nums = []
        for line in lines:
            try:
                nums.append(int(line))
            except ValueError:
                nums.append(0)
        helper004 = nums[0:4] if len(nums) >= 4 else [0, 0, 0, 0]
        helper005 = nums[4:14] if len(nums) >= 14 else [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while len(helper004) < 4:
            helper004.append(0)
        while len(helper005) < 10:
            helper005.append(0)
        return helper004, helper005
    except Exception:
        return [0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def update_game_setting(game_dir, resolution_index):
    """更新 GameSetting.inf — 保留前14行 helper 值，只改分辨率相关行."""
    from ..data.map_data import RESOLUTION_OPTIONS
    try:
        setting_path = Path(game_dir) / "GameSetting.inf"

        # 默认模板（第1行=1，第21行=1）
        default_lines = [
            "1", "0", "1", "1", "42", "0", "43", "10", "3",
            "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "1"
        ]

        if not setting_path.exists():
            content = "\r\n".join(default_lines) + "\r\n"
            with open(setting_path, "w", encoding="gbk") as f:
                f.write(content)
            return

        # 读取现有值，保留前14行不变
        with open(setting_path, "r", encoding="gbk") as f:
            lines = f.read().strip().splitlines()
        while len(lines) < 21:
            lines.append("0")

        # 应用分辨率：RESOLUTION_OPTIONS = [(name, display_quality, screen_full), ...]
        if 0 <= resolution_index < len(RESOLUTION_OPTIONS):
            _, display_quality, screen_full = RESOLUTION_OPTIONS[resolution_index]
            lines[20] = str(screen_full)  # 第21行: 0=窗口, 1=全屏

        content = "\r\n".join(lines) + "\r\n"
        with open(setting_path, "w", encoding="gbk") as f:
            f.write(content)
    except Exception:
        pass
