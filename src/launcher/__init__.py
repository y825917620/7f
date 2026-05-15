# -*- coding: utf-8 -*-
"""启动逻辑（无UI依赖）"""

from .game_launcher import launch_game
from .game_settings import update_game_setting, read_helper_from_setting

__all__ = ["launch_game", "update_game_setting", "read_helper_from_setting"]
