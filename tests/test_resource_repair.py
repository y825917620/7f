# -*- coding: utf-8 -*-

from pathlib import Path

from src.launcher.game_launcher import (
    _ensure_effect_aliases,
    _ensure_model_aliases,
    _ensure_terrain_aliases,
    _looks_like_usable_dds,
    _repair_ui_dds_from_tga,
)


def _write_tga_2x2_rgb(path: Path):
    # Uncompressed true-color TGA, bottom-left origin.
    header = bytearray(18)
    header[2] = 2         # image type: true-color
    header[12] = 2        # width
    header[14] = 2        # height
    header[16] = 24       # bpp
    pixels = bytes([
        0, 0, 255,        # red
        0, 255, 0,        # green
        255, 0, 0,        # blue
        255, 255, 255,    # white
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(header) + pixels)


def test_ensure_terrain_aliases_creates_missing_nor_file(tmp_path: Path):
    game_dir = tmp_path / "data"
    terrain = game_dir / "resource" / "sanguo" / "terrain"
    terrain.mkdir(parents=True, exist_ok=True)
    src = terrain / "Terrain_grassland_006.tga"
    src.write_bytes(b"abc")

    created = _ensure_terrain_aliases(game_dir)

    dst = terrain / "Terrain_grassland_006_nor.tga"
    assert dst.exists()
    assert dst.read_bytes() == b"abc"
    assert "Terrain_grassland_006_nor.tga" in created


def test_repair_ui_dds_from_tga_rewrites_invalid_dds(tmp_path: Path):
    game_dir = tmp_path / "data"
    ui = game_dir / "resource" / "sanguo" / "ui"
    ui.mkdir(parents=True, exist_ok=True)

    for stem in ("loading_misc", "mission_misc", "main_misc", "ui_guide"):
        _write_tga_2x2_rgb(ui / f"{stem}.tga")
    # Small broken files that should be replaced.
    (ui / "loading_misc.dds").write_bytes(b"bad")
    (ui / "mission_misc.dds").write_bytes(b"bad")
    (ui / "main_misc.dds").write_bytes(b"bad")
    (ui / "ui_guide.dds").write_bytes(b"bad")

    repaired = _repair_ui_dds_from_tga(game_dir)

    assert set(repaired) == {"loading_misc.dds", "mission_misc.dds", "main_misc.dds", "ui_guide.dds"}
    assert _looks_like_usable_dds(ui / "loading_misc.dds") is False
    # 2x2 texture is tiny and won't pass the "usable" size gate, but DDS header must exist.
    assert (ui / "loading_misc.dds").read_bytes()[:4] == b"DDS "


def test_ensure_effect_aliases_creates_missing_runtime_names(tmp_path: Path):
    game_dir = tmp_path / "data"
    effect = game_dir / "resource" / "sanguo" / "effect"
    effect.mkdir(parents=True, exist_ok=True)
    (effect / "yfire.tga").write_bytes(b"fire")
    (effect / "bomb3002.TGA").write_bytes(b"bomb")
    (effect / "tengman1.tga").write_bytes(b"vine")

    created = _ensure_effect_aliases(game_dir)

    assert (effect / "zzfire11.tga").read_bytes() == b"fire"
    assert (effect / "bomb05.tga").read_bytes() == b"bomb"
    assert (effect / "tengman.tga").read_bytes() == b"vine"
    assert set(created) == {"zzfire11.tga", "bomb05.tga", "tengman.tga"}


def test_ensure_model_aliases_clones_missing_cliff_transitions(tmp_path: Path):
    game_dir = tmp_path / "data"
    model = game_dir / "resource" / "sanguo" / "model"
    model.mkdir(parents=True, exist_ok=True)
    (model / "CliffTransABHL0.lmo").write_bytes(b"cliff-transition")

    created = _ensure_model_aliases(game_dir)

    expected = {
        "CliffTransAAHL0.lmo",
        "CliffTransAALH0.lmo",
        "CliffTransAHLA0.lmo",
        "CliffTransALHA0.lmo",
        "CliffTransHAAL0.lmo",
        "CliffTransHLAA0.lmo",
        "CliffTransLAAH0.lmo",
        "CliffTransLHAA0.lmo",
    }
    assert set(created) == expected
    for name in expected:
        assert (model / name).read_bytes() == b"cliff-transition"
