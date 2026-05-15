# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.resource_mount_manager import ResourceMountManager


def test_prepare_writes_launch_cache_and_mount_point(temp_game_dir: Path, sample_payload: bytes):
    manager = ResourceMountManager(temp_game_dir, cache_dir=temp_game_dir.parent / "cache" / "launch")

    manifest = manager.prepare(10002, temp_game_dir / "map" / "10002.sl")

    assert manifest.is_valid()
    assert manifest.strategy == "file_dual_mount"
    assert manifest.unpacked_path.exists()
    assert manifest.unpacked_path.read_bytes() == sample_payload
    assert (temp_game_dir / "sl" / "map.map").read_bytes() == sample_payload
    assert (temp_game_dir / "core" / "sl" / "map.map").read_bytes() == sample_payload
    assert len(manifest.mount_points) == 2
    assert manifest.sl_sha256
    assert manifest.unpacked_sha256


def test_prepare_rejects_missing_sl(temp_game_dir: Path):
    manager = ResourceMountManager(temp_game_dir)

    manifest = manager.prepare(10099, temp_game_dir / "map" / "10099.sl")

    assert manifest.is_valid() is False
    assert manifest.strategy == "missing_sl"
    assert manifest.errors
