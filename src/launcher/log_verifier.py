# -*- coding: utf-8 -*-
"""LogVerifier — 启动后解析日志，分类失败类型."""

from pathlib import Path
from typing import Optional, Dict


class LogVerifier:
    """读取游戏日志目录，判断启动结果和失败类型."""

    DIAGNOSTIC_LOGS = (
        "init.log",
        "error.log",
        "net_state.log",
        "log_err.log",
        "cmd_0.log",
        "!Live.log",
        "!video.log",
        "check_sum.log",
    )

    def __init__(self, game_dir: Path):
        self.game_dir = Path(game_dir)

    @staticmethod
    def _read_text(path: Path) -> str:
        return path.read_text(encoding="gbk", errors="ignore")

    @staticmethod
    def _tail_text(text: str, max_chars: int = 12000) -> str:
        if len(text) <= max_chars:
            return text.strip()
        omitted = len(text) - max_chars
        return f"[...前面省略 {omitted} 字符...]\n{text[-max_chars:].strip()}"

    def _collect_diagnostic_logs(self, log_dir: Path) -> Dict[str, str]:
        logs = {}
        for name in self.DIAGNOSTIC_LOGS:
            path = log_dir / name
            if not path.exists() or not path.is_file():
                continue
            try:
                content = self._tail_text(self._read_text(path))
            except Exception as e:
                content = f"[读取失败] {e}"
            if content:
                logs[name] = content
        return logs

    def find_latest_log_dir(self) -> Optional[Path]:
        """找到最新的日志目录."""
        log_dirs = []
        for entry in self.game_dir.glob("log*"):
            if entry.is_dir() and entry.name.startswith("log") and "log_mgr" not in entry.name:
                try:
                    mtime = entry.stat().st_mtime
                    log_dirs.append((mtime, entry))
                except Exception:
                    pass
        if not log_dirs:
            return None
        log_dirs.sort(key=lambda x: x[0], reverse=True)
        return log_dirs[0][1]

    def verify(self, expected_map_id: int, log_dir: Optional[Path] = None) -> Dict:
        """验证日志，返回结构化报告.

        failure_kind 分类:
          - ui_init_failed: error.log 中有 tab_interface nil
          - map_read_failed: 日志中有 读取地图[...]失败
          - map_id_mismatch: 期望 ID 未出现在日志中
          - map_script_not_loaded: 有 begin load map 但无 sanguo.o ok!
          - not_enough_runtime_frames: map 加载了但帧数太少
          - None: 成功
        """
        result = {
            "ok": False,
            "log_dir": str(log_dir) if log_dir else None,
            "init_log_exists": False,
            "map_id_match": False,
            "resource_map_name": None,
            "has_sanguo_o": False,
            "has_begin_load": False,
            "after_run_count": 0,
            "render_count": 0,
            "errors": [],
            "failure_kind": None,
            "error_log_tail": "",
            "init_log_tail": "",
            "net_state_log_tail": "",
            "log_err_tail": "",
            "diagnostic_logs": {},
            "tail_lines": [],
        }

        if log_dir is None:
            log_dir = self.find_latest_log_dir()
            if log_dir:
                result["log_dir"] = str(log_dir)

        if not log_dir or not log_dir.exists():
            result["errors"].append("未找到日志目录")
            result["failure_kind"] = "no_logs"
            return result

        result["log_dir"] = str(log_dir)
        result["diagnostic_logs"] = self._collect_diagnostic_logs(log_dir)
        result["init_log_tail"] = result["diagnostic_logs"].get("init.log", "")
        result["error_log_tail"] = result["diagnostic_logs"].get("error.log", "")
        result["net_state_log_tail"] = result["diagnostic_logs"].get("net_state.log", "")
        result["log_err_tail"] = result["diagnostic_logs"].get("log_err.log", "")

        # 读 init.log
        init_log = log_dir / "init.log"
        init_content = ""
        if init_log.exists():
            result["init_log_exists"] = True
            try:
                init_content = self._read_text(init_log)
            except Exception as e:
                result["errors"].append(f"读取 init.log 失败: {e}")
                result["failure_kind"] = "log_read_error"
                return result

        # 读 error.log
        error_log = log_dir / "error.log"
        error_content = ""
        if error_log.exists():
            try:
                error_content = self._read_text(error_log)
            except Exception:
                pass

        net_state_content = ""
        net_state_log = log_dir / "net_state.log"
        if net_state_log.exists():
            try:
                net_state_content = self._read_text(net_state_log)
            except Exception:
                pass
        combined_content = "\n".join([init_content, error_content, net_state_content])

        # 检查地图 — 必须看到本次 manifest 的具体地图 ID。
        expected_name_num = f"设置读取地图名[{expected_map_id}]"
        init_lines = [line.strip() for line in init_content.splitlines()]
        if expected_name_num in init_content or str(expected_map_id) in init_lines:
            result["map_id_match"] = True
        if "设置读取地图名[sanguo]" in init_content:
            result["resource_map_name"] = "sanguo"

        # 检查关键阶段
        result["has_sanguo_o"] = "do [map/sanguo/sanguo.o] ok!" in init_content
        result["has_begin_load"] = f"begin load map[{expected_map_id}]" in init_content

        # 只有地图名匹配时，才允许进入后续加载阶段判断。
        if result["map_id_match"] and not result["has_begin_load"]:
            result["has_begin_load"] = True  # 地图名正确即认为开始加载
        result["after_run_count"] = init_content.count("enter:AfterRunGameLogic")
        result["render_count"] = init_content.count("enter:Render")

        lines = init_content.strip().splitlines()
        result["tail_lines"] = lines[-20:] if len(lines) >= 20 else lines

        # === 失败分类 ===

        # 1. UI 初始化失败
        if "tab_interface" in error_content and "nil" in error_content:
            result["failure_kind"] = "ui_init_failed"
            result["errors"].append(
                "UI 初始化失败 (tab_interface nil)"
            )

        # 1b. 网络/重连链路失败：会持续触发 event.lua 的断线重连 UI 弹窗。
        reconnect_markers = [
            "通知脚本发生断线重连",
            "断线重连中",
            "重连成功",
            "Ping服务通讯失败",
            "底层与host server失去联系",
        ]
        if any(marker in combined_content for marker in reconnect_markers):
            if not result["failure_kind"]:
                result["failure_kind"] = "network_reconnect_loop"
            result["errors"].append("游戏进入断线重连循环，重连 UI 控件为 nil，弹窗会持续出现")

        if "打开内存映射失败" in combined_content:
            if not result["failure_kind"]:
                result["failure_kind"] = "memory_map_open_failed"
            result["errors"].append("游戏未能打开 MemoryMapName=sanguo 内存映射")

        if "网络初始化失败" in combined_content:
            if not result["failure_kind"]:
                result["failure_kind"] = "network_init_failed"
            result["errors"].append("网络初始化失败，游戏未进入可用的本地对局链路")

        # 2. 地图读取失败
        read_fail_pattern = f"读取地图[{expected_map_id}]失败"
        sanguo_read_fail = "读取地图[sanguo]失败"
        if read_fail_pattern in init_content or sanguo_read_fail in init_content or read_fail_pattern in error_content or sanguo_read_fail in error_content:
            if not result["failure_kind"]:
                result["failure_kind"] = "map_read_failed"
            result["errors"].append("游戏引擎报告地图读取失败")

        # 3. 地图 ID 不匹配
        if not result["map_id_match"] and not result["failure_kind"]:
            result["failure_kind"] = "map_id_mismatch"
            result["errors"].append(
                f"日志未包含期望的地图 ID {expected_map_id}"
            )

        # 4. 地图脚本未加载
        if result["has_begin_load"] and not result["has_sanguo_o"] and not result["failure_kind"]:
            result["failure_kind"] = "map_script_not_loaded"
            result["errors"].append("游戏开始加载地图但 sanguo.o 未成功执行")

        # 5. 帧数过低
        if result["after_run_count"] < 3 and not result["failure_kind"]:
            result["failure_kind"] = "not_enough_runtime_frames"
            result["errors"].append(
                f"运行时帧数不足 (AfterRun={result['after_run_count']}, Render={result['render_count']})"
            )

        # 综合判定
        result["ok"] = (
            result["map_id_match"]
            and result["has_sanguo_o"]
            and result["after_run_count"] > 2
            and result["render_count"] > 2
            and result["failure_kind"] is None
            and len(result["errors"]) == 0
        )

        return result
