# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.map_launch_manifest import MapLaunchManifest
from src.core.config_generator import generate_edt2_lua
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


def test_game_bridge_prepare_writes_editor_bootstrap_files(temp_game_dir: Path, sample_payload: bytes):
    mounted = temp_game_dir / "sl" / "map.map"
    mounted.parent.mkdir()
    mounted.write_bytes(sample_payload)
    core_mounted = temp_game_dir / "core" / "sl" / "map.map"
    core_mounted.parent.mkdir()
    core_mounted.write_bytes(sample_payload)
    (temp_game_dir / "GameSetting.inf").write_text("\n".join(["1"] * 21))

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=temp_game_dir,
        unpacked_path=mounted,
        mount_points=[mounted, core_mounted],
        options=[1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0],
    )
    manifest.strategy = "file_dual_mount"

    bridge = GameBridge(manifest)

    assert bridge.prepare() is True
    assert (temp_game_dir / "config.lua").exists()
    assert (temp_game_dir / "core" / "config.lua").exists()
    assert (temp_game_dir / "core" / "edt2.o").exists()


def test_generate_edt2_uses_original_launcher_helper_constants(temp_game_dir: Path):
    lua_src = generate_edt2_lua(10002, [1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0], game_dir=temp_game_dir)

    assert "function helper_get004() return {4938529,13879638,13889092,26660} end" in lua_src
    assert "function helper_get005() return {10,20,40,80,160,320,640,1280,2560,5120} end" in lua_src
    assert "function GetMapOptionDisplay() return 0 end" in lua_src


def test_game_bridge_uses_file_mount_default_cmdline(temp_game_dir: Path, sample_payload: bytes):
    mounted = temp_game_dir / "sl" / "map.map"
    mounted.parent.mkdir()
    mounted.write_bytes(sample_payload)
    core_mounted = temp_game_dir / "core" / "sl" / "map.map"
    core_mounted.parent.mkdir()
    core_mounted.write_bytes(sample_payload)

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=temp_game_dir,
        unpacked_path=mounted,
        mount_points=[mounted, core_mounted],
        options=[-1] * 10 + [0],
    )
    manifest.strategy = "file_dual_mount"

    bridge = GameBridge(manifest)
    cmdline = bridge._build_cmdline(temp_game_dir / "core" / "game.exe")

    assert cmdline == f'"{temp_game_dir / "core" / "game.exe"}" 10002'
    assert "/testgamebyeditor=1" not in cmdline
    assert "MemoryMapName=sanguo" not in cmdline
    assert "/mapfile=" not in cmdline
