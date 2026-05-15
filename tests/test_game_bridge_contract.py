# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.map_launch_manifest import MapLaunchManifest
from src.launcher.game_launcher import GameBridge


def test_game_bridge_accepts_manifest_without_unpacking(temp_game_dir: Path):
    mounted = temp_game_dir / "sl" / "map.map"
    mounted.parent.mkdir()
    mounted.write_bytes(b"LuaRDGTM mounted")

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=temp_game_dir,
        unpacked_path=mounted,
        mount_points=[mounted],
        options=[-1] * 10 + [0],
    )
    manifest.strategy = "file_dual_mount"

    bridge = GameBridge(manifest)

    assert bridge.map_id == 10002
    assert bridge.game_dir == temp_game_dir
    assert bridge.manifest is manifest


def test_game_bridge_rejects_invalid_manifest(temp_game_dir: Path):
    import pytest

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=temp_game_dir,
    )
    manifest.add_error("no resources")

    with pytest.raises(ValueError, match="Manifest 无效"):
        GameBridge(manifest)


def test_game_bridge_does_not_unpack_resources(temp_game_dir: Path, sample_payload: bytes):
    """验证 GameBridge 不自行解压资源 — 资源已由 MountManager 准备好."""
    # 模拟 MountManager 已经完成的挂载
    mounted = temp_game_dir / "sl" / "map.map"
    mounted.parent.mkdir()
    mounted.write_bytes(sample_payload)

    # 创建 GameSetting.inf（21 行）
    (temp_game_dir / "GameSetting.inf").write_text("\n".join(["1"] * 21))

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=temp_game_dir,
        unpacked_path=mounted,
        mount_points=[mounted],
        options=[-1] * 10 + [0],
    )
    manifest.strategy = "file_dual_mount"

    bridge = GameBridge(manifest)

    # prepare() 只做 config.lua + map.o + GameSetting.inf
    # 不调用 lzma.decompress 或 _ensure_sl_map
    prepare_ok = bridge.prepare()
    assert prepare_ok is True
    # sl/map.map 内容未被修改（GameBridge 不重写挂载点）
    assert mounted.read_bytes() == sample_payload
