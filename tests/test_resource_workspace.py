# -*- coding: utf-8 -*-

import json
from pathlib import Path

from src.core.resource_workspace import ResourceWorkspace


def test_import_map_preserves_source_and_manifest(temp_game_dir: Path):
    workspace = ResourceWorkspace(temp_game_dir.parent)

    manifest_path = workspace.import_map(
        10002,
        temp_game_dir / "map" / "10002.map",
        temp_game_dir / "map" / "10002.sl",
    )

    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["map_id"] == 10002
    assert data["files"][".map"]["sha256"]
    assert data["files"][".sl"]["analysis"]["ok"] is True


def test_unpack_to_workspace_writes_unpacked_info(temp_game_dir: Path, sample_payload: bytes):
    workspace = ResourceWorkspace(temp_game_dir.parent)
    workspace.import_map(10002, temp_game_dir / "map" / "10002.map", temp_game_dir / "map" / "10002.sl")

    unpacked = workspace.unpack_to_workspace(10002)

    assert unpacked.exists()
    assert unpacked.read_bytes() == sample_payload
    info_path = temp_game_dir.parent / "maps" / "workspace" / "10002" / "unpack_info.json"
    assert info_path.exists()
    info = json.loads(info_path.read_text(encoding="utf-8"))
    assert info["unpacked_sha256"]
