# -*- coding: utf-8 -*-
"""SL10002 ONE LOG 生成器 — 参考 SL10002_MakeOneLog.ps1."""

import json
from pathlib import Path
from datetime import datetime


def _read_log(path: Path) -> str:
    try:
        return path.read_text(encoding="gbk", errors="ignore")
    except Exception:
        return ""


def generate_one_log(game_dir: Path, map_id: int = 10002, version_tag: str = "V45"):
    """生成 SL10002_ONE_LOG.txt."""
    output_path = game_dir / "SL10002_ONE_LOG.txt"
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"SL10002 ONE LOG {version_tag} {now}")
    lines.append(f"MapID={map_id}")

    # 收集所有日志目录
    log_dirs = sorted(
        [d for d in game_dir.glob("log*") if d.is_dir() and d.name.startswith("log")],
        key=lambda x: x.stat().st_mtime, reverse=True
    )

    if not log_dirs:
        lines.append("STATUS: NO LOGS FOUND")
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    latest = log_dirs[0]
    lines.append(f"LogDir={latest.name}")

    # init.log 分析
    init_log = latest / "init.log"
    if init_log.exists():
        init = _read_log(init_log)
        lines.append(f"InitLogSize={len(init)}")
        for kw in ["设置读取地图名", "do [core/gpi.o]", "do [map/sanguo",
                    "begin load map", "成功执行map_init", "GameEvent_MapInit",
                    "AfterRunGameLogic", "enter:Render",
                    "读取地图", "失败", "map is not ok"]:
            count = init.count(kw)
            if count > 0:
                lines.append(f"  {kw}: {count}")

        # 尾部
        init_lines = init.strip().splitlines()
        if len(init_lines) > 10:
            lines.append("InitLogTail:")
            for l in init_lines[-20:]:
                lines.append(f"  {l.strip()}")

    # error.log 分析
    error_log = latest / "error.log"
    if error_log.exists():
        err = _read_log(error_log)
        lines.append(f"ErrorLogSize={len(err)}")
        for kw in ["tab_interface", "nil", "Lua", "错误", "失败", "map is not ok",
                    "断线重连", "reconnect", "UI_lua"]:
            count = err.count(kw)
            if count > 0:
                lines.append(f"  {kw}: {count}")
        err_lines = err.strip().splitlines()
        if len(err_lines) > 5:
            lines.append("ErrorLogTail:")
            for l in err_lines[-15:]:
                lines.append(f"  {l.strip()[:200]}")

    # net_state.log
    net_log = latest / "net_state.log"
    if net_log.exists():
        net = _read_log(net_log)
        lines.append(f"NetStateSize={len(net)}")
        for kw in ["连接", "失败", "成功", "Ping", "session", "PlatLev", "RoomID",
                    "recv control", "start", "fps", "turn"]:
            if kw in net:
                idx = net.find(kw)
                ctx = net[max(0, idx-10):idx+100].replace("\n", " | ")
                lines.append(f"  {kw}: {ctx}")

    # HostService log
    hs_log = game_dir / "SL10002_host_service.log"
    if hs_log.exists():
        hs = _read_log(hs_log)
        hs_lines = hs.strip().splitlines()
        lines.append(f"HostServiceLogLines={len(hs_lines)}")
        for l in hs_lines[-10:]:
            lines.append(f"  {l}")

    # map_protocol log
    mp_log = game_dir / "SL10002_map_protocol_v45.log"
    if mp_log.exists():
        mp = _read_log(mp_log)
        mp_lines = mp.strip().splitlines()
        lines.append(f"MapProtocolLogLines={len(mp_lines)}")
        for l in mp_lines[-20:]:
            lines.append(f"  {l}")

    # 诊断结论
    lines.append("")
    lines.append("=== DIAGNOSIS ===")
    errors = []
    if init_log.exists():
        init = _read_log(init_log)
        after_run = init.count("enter:AfterRunGameLogic")
        render = init.count("enter:Render")
        sanguo_o = "do [map/sanguo/sanguo.o] ok!" in init
        map_init = "成功执行map_init" in init
        begin_load = "begin load map" in init
        map_name = any(kw in init for kw in ["设置读取地图名[10002]", "设置读取地图名[sanguo]"])

        lines.append(f"AfterRun={after_run} Render={render} sanguo_o={sanguo_o} map_init={map_init} begin_load={begin_load} map_name={map_name}")

        if not map_name:
            errors.append("MAP_NAME_NOT_FOUND: 游戏未识别地图名")
        if after_run == 0:
            errors.append("NO_RUNTIME: 游戏未能进入运行循环")
        elif after_run < 3:
            errors.append(f"LOW_RUNTIME: 游戏只运行了 {after_run} 帧")
        if not sanguo_o:
            errors.append("NO_SANGUO_O: 地图脚本未加载")
        if after_run > 5 and sanguo_o:
            errors.append("MAP_LOADED_OK: 地图加载成功")
            lines.append("STATUS: SUCCESS")
        else:
            lines.append("STATUS: FAILED")

    if error_log.exists():
        err = _read_log(error_log)
        if "tab_interface" in err and "nil" in err:
            errors.append("UI_INIT_FAILED: tab_interface nil")

    if net_log.exists():
        net = _read_log(net_log)
        if "连接游戏网络" in net and "失败" in net:
            errors.append("NETWORK_CONNECT_FAILED: 无法连接 HostService 29002")

    for e in errors:
        lines.append(f"  [{e}]")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def analyze_and_report(game_dir: Path, map_id: int = 10002, pid: int = 0):
    """生成诊断报告并打印关键发现."""
    log_path = generate_one_log(game_dir, map_id)
    print(f"\n{'='*60}")
    print(f"SL10002 诊断报告: {log_path}")
    print(f"{'='*60}")
    content = log_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        if any(kw in line for kw in ["DIAGNOSIS", "STATUS", "AfterRun", "MAP_",
                                      "UI_", "NETWORK_", "NO_", "LOW_"]):
            print(f"  {line}")
    return log_path
