# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.map_package_analyzer import MapPackageAnalyzer
from tests.conftest import make_sl_bytes


def test_analyze_valid_raw_lzma_sl(tmp_path: Path):
    payload = b"LuaRDGTM payload"
    sl_path = tmp_path / "10005.sl"
    sl_path.write_bytes(make_sl_bytes(payload))

    report = MapPackageAnalyzer.analyze(sl_path)

    assert report["ok"] is True
    assert report["map_id"] == 10005
    assert report["decompressed_size"] == len(payload)
    assert report["header_valid"] is True
    assert report["dec_sha256"]


def test_decompress_returns_payload_for_valid_sl(tmp_path: Path):
    payload = b"LuaRDGTM another payload"
    sl_path = tmp_path / "10006.sl"
    sl_path.write_bytes(make_sl_bytes(payload))

    assert MapPackageAnalyzer.decompress(sl_path) == payload


def test_analyze_rejects_non_luardgtm_payload(tmp_path: Path):
    sl_path = tmp_path / "10007.sl"
    sl_path.write_bytes(make_sl_bytes(b"BADHEADER"))

    report = MapPackageAnalyzer.analyze(sl_path)

    assert report["ok"] is False
    assert report["header_valid"] is False
    assert "LuaRDGTM" in report["error"]
