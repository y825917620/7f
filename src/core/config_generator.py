# -*- coding: utf-8 -*-
"""config.lua / edt2.lua 生成器 — 值来自原启动器字节码反汇编."""

from pathlib import Path


ORIGINAL_HELPER_004 = [25424630, 13886613, 13878151, 9983]  # 来自原版 edt2.o 字节码
ORIGINAL_HELPER_005 = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120]


def _read_helper_from_setting(game_dir):
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


def generate_config_lua(map_id, options, control_id=1, display=0, game_dir=None):
    """生成 config.lua — 与原启动器格式一致."""
    all_negative_one = all(v == -1 for v in options[:10])
    option_parts = []
    for i in range(10):
        val = options[i] if i < len(options) else -1
        if all_negative_one or val != -1:
            option_parts.append(f"{{{i} , {val}}}")
    option_str = ",".join(option_parts)
    return f"tempConfigLuaMapOptionInfo = {{ {option_str},}} SetCurrentControlID({control_id})"


def generate_edt2_lua(map_id, options, control_id=1, display=0, game_dir=None):
    """生成 edt2.o Lua 源码 — 值来自 GameSetting.inf（与原启动器一致）。

    反汇编证实原 edt2.o 包含:
      helper_get004(4个int) helper_get005(10个int)
      tempConfigLuaMapOptionInfo(10个{idx,val})
      SetCurrentControlID GetMapOptionInfo helper_get006 GetMapOptionDisplay
    """
    if game_dir:
        helper004, helper005 = _read_helper_from_setting(game_dir)
    else:
        helper004, helper005 = ORIGINAL_HELPER_004, ORIGINAL_HELPER_005

    option_parts = []
    for i in range(10):
        val = options[i] if i < len(options) else -1
        option_parts.append(f"{{{i},{val}}}")
    option_str = ",".join(option_parts)

    h4 = ",".join(str(v) for v in helper004)
    h5 = ",".join(str(v) for v in helper005)

    return (
        f"function helper_get004() return {{{h4}}} end\n"
        f"function helper_get005() return {{{h5}}} end\n"
        f"tempConfigLuaMapOptionInfo = {{{option_str},}}\n"
        f"SetCurrentControlID({control_id})\n"
        f"function GetMapOptionInfo() return tempConfigLuaMapOptionInfo end\n"
        f"function helper_get006() return '513133695' end\n"
        f"function GetMapOptionDisplay() return {display} end"
    )


def generate_map_opt_lua(g_map_display, g_map_opt):
    """生成 map.o 的 Lua 源码."""
    lines = [f"g_map_display = {g_map_display}", "g_map_opt = {}"]
    for opt_id, values in sorted(g_map_opt.items()):
        vals = ", ".join(str(v) for v in values)
        lines.append(f"g_map_opt[{opt_id}] = {{{vals}}}")
    return "\n".join(lines)
