# -*- coding: utf-8 -*-

from pathlib import Path
from src.core.resource_mount_manager import ResourceMountManager


def test_prepare_rejects_missing_sl(temp_game_dir: Path):
    manager = ResourceMountManager(temp_game_dir)
    manifest = manager.prepare(10099, temp_game_dir / "map" / "10099.sl")
    assert manifest.is_valid() is False
    assert manifest.strategy == "missing_sl"


def test_prepare_rejects_non_luardgtm(temp_game_dir: Path):
    # 写入非 LuaRDGTM 头部的数据
    sl_path = temp_game_dir / "map" / "10002.sl"
    sl_path.write_bytes(b"NOT_LUARDGTM_DATA")

    manager = ResourceMountManager(temp_game_dir)
    manifest = manager.prepare(10002, sl_path)
    assert manifest.is_valid() is False
