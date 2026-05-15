# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.map_launch_manifest import MapLaunchManifest


def test_manifest_records_hashes_and_mount_points(tmp_path: Path):
    unpacked = tmp_path / "cache" / "map_package.bin"
    unpacked.parent.mkdir()
    unpacked.write_bytes(b"LuaRDGTM data")

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=tmp_path / "data",
        sl_path=tmp_path / "data" / "map" / "10002.sl",
        unpacked_path=unpacked,
        mount_points=[tmp_path / "data" / "sl" / "map.map"],
        options=[-1] * 10 + [0],
    )
    manifest.set_hashes(sl_sha256="abc", unpacked_sha256="def")
    manifest.strategy = "file_dual_mount"

    data = manifest.to_dict()

    assert data["sl_sha256"] == "abc"
    assert data["unpacked_sha256"] == "def"
    assert data["strategy"] == "file_dual_mount"
    assert data["valid"] is True


def test_manifest_round_trip(tmp_path: Path):
    unpacked = tmp_path / "map_package.bin"
    unpacked.write_bytes(b"LuaRDGTM data")
    path = tmp_path / "launch_manifest.json"

    manifest = MapLaunchManifest(10005, tmp_path / "data", unpacked_path=unpacked)
    manifest.strategy = "cache_only"
    manifest.save(path)

    loaded = MapLaunchManifest.load(path)

    assert loaded.map_id == 10005
    assert loaded.strategy == "cache_only"
    assert loaded.unpacked_path == unpacked
