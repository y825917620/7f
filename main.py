# -*- coding: utf-8 -*-
"""
神龙地图启动器 - 新版 (入口文件)
基于原启动器功能完整重写，保留所有赞助/推广功能。
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中，以便 PyInstaller 和直接运行都能找到 src 包
_project_root = Path(__file__).parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.ui.main_window import main

if __name__ == "__main__":
    main()
