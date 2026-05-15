# -*- coding: utf-8 -*-
"""GameSetting.inf 读写工具"""

from pathlib import Path


def read_helper_from_setting(game_dir):
    """从 GameSetting.inf 读取 helper_get004/helper_get005 的值.

    GameSetting.inf 是 21 行纯数字文本，前 14 行对应:
      helper_get004 -> 第 1~4 行 (4 个整数)
      helper_get005 -> 第 5~14 行 (10 个整数)
    如果文件不存在或格式错误，回退到全 0.
    """
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
        # 补齐缺失值
        while len(helper004) < 4:
            helper004.append(0)
        while len(helper005) < 10:
            helper005.append(0)
        return helper004, helper005
    except Exception:
        return [0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def update_game_setting(game_dir, resolution_index):
    """根据当前分辨率设置更新 GameSetting.inf

    关键发现：
      - 原启动器 GameSetting.inf 第1行 = 1（不是5），第21行 = 1
      - 原启动器只写入 data/GameSetting.inf，不写 core/GameSetting.inf
      - 若第1行设为5，游戏UI初始化失败导致 tab_interface nil 崩溃
      - 分辨率控制可能通过其他机制（非GameSetting.inf）实现
    """
    from ..data.map_data import RESOLUTION_OPTIONS
    try:
        setting_path = Path(game_dir) / "GameSetting.inf"
        # 默认模板必须与原启动器完全一致（第1行=1，第21行=1）
        default_lines = [
            "1", "0", "1", "1", "42", "0", "43", "10", "3",
            "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "1"
        ]
        lines = default_lines[:]
        if setting_path.exists():
            with open(setting_path, "r", encoding="gbk") as f:
                existing = f.read().strip().splitlines()
            for i, val in enumerate(existing):
                if i < len(lines):
                    lines[i] = val

        # 暂时保留分辨率设置逻辑，但第1行和第21行保持原值
        # TODO: 分辨率控制需要进一步研究原启动器机制
        if 0 <= resolution_index < len(RESOLUTION_OPTIONS):
            _, display_quality, screen_full = RESOLUTION_OPTIONS[resolution_index]
            # 不覆盖第1行（必须是1），第21行保持原值
            pass

        content = "\n".join(lines) + "\n"
        with open(setting_path, "w", encoding="gbk") as f:
            f.write(content)

        # 原启动器不写 core/GameSetting.inf
    except Exception:
        pass
