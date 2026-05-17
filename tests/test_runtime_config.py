# -*- coding: utf-8 -*-

from pathlib import Path

from src.launcher.game_launcher import write_config_lua_v45


def test_config_wraps_set_cliff_tex_nil_scene_object(tmp_path: Path):
    write_config_lua_v45(tmp_path, 10002, 1, [1, 0, 0, -1, -1, -1, -1, -1, -1, -1])

    lua = (tmp_path / "config.lua").read_text(encoding="ascii")

    assert "local __sl_raw_SetCliffTex = SetCliffTex" in lua
    assert "function SetCliffTex(obj, tex)" in lua
    assert "if obj == nil then" in lua


def test_config_installs_passive_map_chain_diagnostics(tmp_path: Path):
    write_config_lua_v45(tmp_path, 10002, 1, [1, 0, 0, -1, -1, -1, -1, -1, -1, -1])

    lua = (tmp_path / "config.lua").read_text(encoding="ascii")

    assert "passive map-chain diagnostics installed" in lua
    assert "'map_addchar'" in lua
    assert "'map_addsceneobj'" in lua
    assert "'player_station'" in lua
    assert "AddCha.log" in lua


def test_config_blocks_reconnect_failure_exit_chain(tmp_path: Path):
    write_config_lua_v45(tmp_path, 10002, 1, [1, 0, 0, -1, -1, -1, -1, -1, -1, -1])

    lua = (tmp_path / "config.lua").read_text(encoding="ascii")

    assert "__sl_block_exit('appExit')" in lua
    assert "__sl_block_exit('GameEventCloseWindow')" in lua
    assert "__sl_block_exit('NotifyOffline')" in lua
    assert "[BLOCK_EXIT]" in lua
