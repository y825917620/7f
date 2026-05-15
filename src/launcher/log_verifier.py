# -*- coding: utf-8 -*-
"""LogVerifier — 启动后解析日志，分类失败类型."""

from pathlib import Path
from typing import Optional, Dict


class LogVerifier:
    """读取游戏日志目录，判断启动结果和失败类型."""

    def __init__(self, game_dir: Path):
        self.game_dir = Path(game_dir)

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
            "has_sanguo_o": False,
            "has_begin_load": False,
            "after_run_count": 0,
            "render_count": 0,
            "errors": [],
            "failure_kind": None,
            "error_log_tail": "",
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

        # 读 init.log
        init_log = log_dir / "init.log"
        init_content = ""
        if init_log.exists():
            result["init_log_exists"] = True
            try:
                init_content = init_log.read_text(encoding="gbk", errors="ignore")
            except Exception as e:
                result["errors"].append(f"读取 init.log 失败: {e}")
                result["failure_kind"] = "log_read_error"
                return result

        # 读 error.log
        error_log = log_dir / "error.log"
        error_content = ""
        if error_log.exists():
            try:
                error_content = error_log.read_text(encoding="gbk", errors="ignore")
                err_lines = [l.strip() for l in error_content.splitlines() if l.strip()]
                result["error_log_tail"] = "\n".join(err_lines[-20:])
            except Exception:
                pass

        # 检查地图 — 游戏内部统一用 "sanguo" 作为地图名
        expected_name_num = f"设置读取地图名[{expected_map_id}]"
        expected_name_sanguo = "设置读取地图名[sanguo]"
        if expected_name_num in init_content or expected_name_sanguo in init_content:
            result["map_id_match"] = True

        # 检查关键阶段
        result["has_sanguo_o"] = "do [map/sanguo/sanguo.o] ok!" in init_content
        result["has_begin_load"] = (
            f"begin load map[{expected_map_id}]" in init_content
            or "begin load map[sanguo]" in init_content
        )

        # 只要地图名匹配了 (sanguo)，就认为地图加载进行中
        # sanguo.o 可能稍后才出现
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
