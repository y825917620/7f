# -*- coding: utf-8 -*-

from pathlib import Path

from src.launcher.log_verifier import LogVerifier


def make_log(game_dir: Path, pid: int, init_text: str, error_text: str = "") -> Path:
    log_dir = game_dir / f"log{pid}-2026.05.15-00.00.00"
    log_dir.mkdir(parents=True)
    (log_dir / "init.log").write_text(init_text, encoding="gbk")
    if error_text:
        (log_dir / "error.log").write_text(error_text, encoding="gbk")
    return log_dir


def test_verify_detects_tab_interface_failure(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "设置读取地图名[10002]\n读取地图表格, 加载地图相关脚本!\n",
        "scripts\\game_init.lua:104: attempt to index global 'tab_interface' (a nil value)\n",
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10002, log_dir=log_dir)

    assert result["ok"] is False
    assert result["failure_kind"] == "ui_init_failed"


def test_verify_detects_map_read_failure(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "设置读取地图名[10005]\n[0] begin load map[10005]\n",
        "读取地图[10005]失败, 游戏退出!\n",
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10005, log_dir=log_dir)

    assert result["ok"] is False
    assert result["failure_kind"] == "map_read_failed"


def test_verify_success_requires_loop_after_map_load(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "\n".join([
            "设置读取地图名[10002]",
            "do [core/gpi.o] ok!",
            "do [map/sanguo/sanguo.o] ok!",
            "[0] begin load map[10002]",
            "enter:AfterRunGameLogic",
            "enter:AfterRunGameLogic",
            "enter:AfterRunGameLogic",
            "enter:Render",
            "enter:Render",
            "enter:Render",
        ]),
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10002, log_dir=log_dir)

    assert result["ok"] is True
    assert result["failure_kind"] is None


def test_verify_accepts_sanguo_as_resource_name_when_cmdline_has_map_id(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "\n".join([
            "10002",
            "设置读取地图名[sanguo]",
            "do [core/gpi.o] ok!",
            "[0] begin load map[sanguo]",
        ]),
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10002, log_dir=log_dir)

    assert result["map_id_match"] is True
    assert result["resource_map_name"] == "sanguo"


def test_verify_collects_multiple_diagnostic_logs(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "设置读取地图名[10002]\nenter:AfterRunGameLogic\n",
        "第一条弹窗\n第二条弹窗\n",
    )
    (log_dir / "net_state.log").write_text("Ping服务通讯失败\n通知脚本发生断线重连\n", encoding="gbk")
    (log_dir / "log_err.log").write_text("set file level \"error\"(1)\n", encoding="gbk")

    result = LogVerifier(game_dir).verify(expected_map_id=10002, log_dir=log_dir)

    assert "init.log" in result["diagnostic_logs"]
    assert "error.log" in result["diagnostic_logs"]
    assert "net_state.log" in result["diagnostic_logs"]
    assert "log_err.log" in result["diagnostic_logs"]
    assert "第二条弹窗" in result["error_log_tail"]
    assert "通知脚本发生断线重连" in result["net_state_log_tail"]


def test_verify_detects_reconnect_popup_loop(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "设置读取地图名[10002]\ndo [map/sanguo/sanguo.o] ok!\nenter:AfterRunGameLogic\n",
        "UI_lua扩展函数[ksui::lua_UIForm_Open]参数个数或者类型错误!\n断线重连中……\n",
    )
    (log_dir / "net_state.log").write_text(
        "Ping服务通讯失败\n当前游戏帧数[0], 通知脚本发生断线重连, bIs = 1, chState = 0\n",
        encoding="gbk",
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10002, log_dir=log_dir)

    assert result["ok"] is False
    assert result["failure_kind"] == "network_reconnect_loop"
    assert any("断线重连循环" in err for err in result["errors"])
