# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:\\玩家原创\\神龙地图启动器5.2\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['src.core.config_generator', 'src.core.map_parser', 'src.core.sl_handler', 'src.launcher.game_launcher', 'src.launcher.game_settings', 'src.ui.main_window', 'src.ui.sponsor_widgets', 'PyQt6.sip', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='神龙地图启动器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['E:\\玩家原创\\神龙地图启动器5.2\\icon.ico'],
)
