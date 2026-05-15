# -*- coding: utf-8 -*-
"""Build script for PyInstaller - avoids bash encoding issues with Chinese filenames."""

import sys
import os
from pathlib import Path

# Project root
project_root = Path(__file__).parent.resolve()
os.chdir(project_root)

# Add PyInstaller to path if needed
try:
    import PyInstaller.__main__
except ImportError:
    print("PyInstaller not installed!")
    sys.exit(1)

icon_path = project_root / "icon.ico"
main_script = project_root / "main.py"

# Build arguments
args = [
    str(main_script),
    "--name", "神龙地图启动器",
    "--icon", str(icon_path),
    "--noconsole",
    "--onefile",
    "--clean",
    "--noconfirm",
    # Hidden imports
    "--hidden-import", "src.core.config_generator",
    "--hidden-import", "src.core.map_parser",
    "--hidden-import", "src.core.map_catalog",
    "--hidden-import", "src.core.map_launch_manifest",
    "--hidden-import", "src.core.map_package_analyzer",
    "--hidden-import", "src.core.resource_mount_manager",
    "--hidden-import", "src.core.resource_workspace",
    "--hidden-import", "src.core.resource_control_service",
    "--hidden-import", "src.launcher.game_launcher",
    "--hidden-import", "src.launcher.game_settings",
    "--hidden-import", "src.launcher.log_verifier",
    "--hidden-import", "src.ui.main_window",
    "--hidden-import", "src.ui.sponsor_widgets",
    # PyQt6 hidden imports
    "--hidden-import", "PyQt6.sip",
    "--hidden-import", "PyQt6.QtCore",
    "--hidden-import", "PyQt6.QtGui",
    "--hidden-import", "PyQt6.QtWidgets",
]

print("Building with args:", args)
PyInstaller.__main__.run(args)
