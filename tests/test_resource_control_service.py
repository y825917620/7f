# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.resource_control_service import ResourceControlService


def test_prepare_launch_manifest_for_existing_map(temp_game_dir: Path, sample_payload: bytes):
    service = ResourceControlService(temp_game_dir)

    manifest = service.prepare_launch_manifest(
        map_id=10002,
        options=[-1] * 10 + [0],
        resolution_index=0,
    )

    assert manifest.is_valid()
    assert manifest.map_id == 10002
    assert manifest.options == [-1] * 10 + [0]
    assert manifest.unpacked_path.read_bytes() == sample_payload
    assert manifest.strategy == "file_dual_mount"


def test_prepare_launch_manifest_reports_missing_map(temp_game_dir: Path):
    service = ResourceControlService(temp_game_dir)

    manifest = service.prepare_launch_manifest(
        map_id=10199,
        options=[-1] * 10 + [0],
        resolution_index=0,
    )

    assert manifest.is_valid() is False
    assert manifest.errors
