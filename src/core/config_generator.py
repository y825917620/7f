# -*- coding: utf-8 -*-
"""config.lua 生成器 - 复用原启动器的 Lua 模板."""

from pathlib import Path

from ..data.map_data import DEFAULT_MAP_OPTIONS


def _read_helper_from_setting(game_dir):
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


def generate_config_lua(map_id, options, control_id=1, display=0, game_dir=None):
    """生成 config.lua — 格式必须与原启动器完全一致。

    原启动器 config.lua 是单行纯文本，只包含：
        tempConfigLuaMapOptionInfo = { {0,val},{1,val},... } SetCurrentControlID(1)
    关键发现：原启动器只写入值不为 -1 的选项（-1 表示"默认"，由游戏自动选择）
    helper_get004/005 放在 edt2.o 字节码中，不在 config.lua 里。
    """
    # 构建 tempConfigLuaMapOptionInfo — 格式必须与原启动器完全一致
    # 关键逻辑：
    #   - 如果所有选项都是 -1（默认状态），生成全部 10 个 -1
    #   - 如果有非 -1 选项，只生成非 -1 的选项
    all_negative_one = all(v == -1 for v in options[:10])
    option_parts = []
    for i in range(10):
        val = options[i] if i < len(options) else -1
        if all_negative_one or val != -1:
            option_parts.append(f"{{{i} , {val}}}")
    option_str = ",".join(option_parts)

    # 单行格式，与原启动器完全一致（注意末尾逗号和空格）
    lua = f"tempConfigLuaMapOptionInfo = {{ {option_str},}} SetCurrentControlID({control_id})"
    return lua


def generate_edt2_lua(map_id, options, control_id=1, display=0, game_dir=None):
    """生成 edt2.o 的字节码源码 — 必须与原启动器的 edt2.o 完全一致。

    通过反汇编原启动器 edt2.o 确认，它包含以下函数：
      - helper_get004 -> {25420060, 13891455, 13881453, 7581}
      - helper_get005 -> {10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120}
      - tempConfigLuaMapOptionInfo
      - SetCurrentControlID(1)
      - GetMapOptionInfo
      - helper_get006 -> "513133695"
      - GetMapOptionDisplay -> 1
    """
    # 所有值必须与原启动器 edt2.o 反汇编结果完全一致
    # 关键：edt2.o 必须保留 -1 值（原启动器 edt2.o 中未设置的选项就是 -1）
    edt2_option_parts = []
    for i in range(10):
        val = options[i] if i < len(options) else 0
        edt2_option_parts.append(f"{{{i},{val}}}")
    edt2_option_str = ",".join(edt2_option_parts)

    lua = f"""function helper_get004() return {{25420765,13891006,13882028,9846}} end
function helper_get005() return {{10,20,40,80,160,320,640,1280,2560,5120}} end
tempConfigLuaMapOptionInfo = {{{edt2_option_str},}}
SetCurrentControlID({control_id})
function GetMapOptionInfo() return tempConfigLuaMapOptionInfo end
function helper_get006() return '513133695' end
function GetMapOptionDisplay() return 1 end
"""
    return lua


def generate_map_opt_lua(g_map_display, g_map_opt):
    """生成 map.o 格式的 Lua 脚本 (用于保存用户自定义选项).

    Args:
        g_map_display: 显示模式
        g_map_opt: dict {option_id: [11 values]}

    Returns:
        Lua 字符串
    """
    lines = [f"g_map_display = {g_map_display}", "g_map_opt = {}"]
    for opt_id, values in sorted(g_map_opt.items()):
        vals = ", ".join(str(v) for v in values)
        lines.append(f"g_map_opt[{opt_id}] = {{{vals}}}")
    return "\n".join(lines)
