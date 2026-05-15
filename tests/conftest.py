# -*- coding: utf-8 -*-

import lzma
from pathlib import Path

import pytest


def make_sl_bytes(payload: bytes) -> bytes:
    compressor = lzma.LZMACompressor(
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 67108864}],
    )
    compressed = compressor.compress(payload) + compressor.flush()
    props = bytes([0x5D, 0x00, 0x00, 0x40, 0x00])
    size = len(payload).to_bytes(8, "little")
    return props + size + compressed


@pytest.fixture
def sample_payload() -> bytes:
    return b"LuaRDGTMa2 synthetic package for tests"


@pytest.fixture
def temp_game_dir(tmp_path: Path, sample_payload: bytes) -> Path:
    game_dir = tmp_path / "data"
    (game_dir / "map").mkdir(parents=True)
    (game_dir / "core").mkdir()
    (game_dir / "resource").mkdir()

    (game_dir / "map" / "10002.map").write_bytes(b"MAPMETA10002")
    (game_dir / "map" / "10002.sl").write_bytes(make_sl_bytes(sample_payload))
    return game_dir
