# -*- coding: utf-8 -*-
"""LogVerifier — 启动后解析最新日志，确认地图加载状态."""

import glob
import os
import time
from pathlib import Path
from typing import Optional, Dict, List


class LogVerifier:
    """读取游戏日志目录，判断启动结果."""

    def __init__(self, game_dir: Path):
        self.game_dir = Path(game_dir)

    def find_latest_log_dir(self) -> Optional[Path]:
        """找到最新的日志目录（格式: log{pid}-{timestamp}）."""
        log_dirs = []
        for entry in self.game_dir.glob("log*"):
            if entry.is_dir() and entry.name != "log_mgr":
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

        Returns:
            {
                "ok": bool,
                "log_dir": str or None,
                "init_log_exists": bool,
                "map_id_match": bool,
                "has_sanguo_o": bool,
                "has_begin_load": bool,
                "after_run_count": int,
                "render_count": int,
                "errors": List[str],
                "tail_lines": List[str],
            }
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
            "tail_lines": [],
        }

        if log_dir is None:
            log_dir = self.find_latest_log_dir()
            if log_dir:
                result["log_dir"] = str(log_dir)

        if not log_dir or not log_dir.exists():
            result["errors"].append("未找到日志目录")
            return result

        init_log = log_dir / "init.log"
        if not init_log.exists():
            result["errors"].append("未找到 init.log")
            return result

        result["init_log_exists"] = True

        try:
            content = init_log.read_text(encoding="gbk", errors="ignore")
        except Exception as e:
            result["errors"].append(f"读取 init.log 失败: {e}")
            return result

        # 检查地图 ID（游戏内部可能使用 sanguo 而非数字 ID）
        expected_name_num = f"设置读取地图名[{expected_map_id}]"
        expected_name_sanguo = "设置读取地图名[sanguo]"
        if expected_name_num in content or expected_name_sanguo in content:
            result["map_id_match"] = True
        else:
            result["errors"].append(f"日志未包含 '{expected_name_num}' 或 '{expected_name_sanguo}'")

        # 检查关键阶段
        result["has_sanguo_o"] = "do [map/sanguo/sanguo.o] ok!" in content
        result["has_begin_load"] = (
            f"begin load map[{expected_map_id}]" in content
            or "begin load map[sanguo]" in content
        )
        result["after_run_count"] = content.count("enter:AfterRunGameLogic")
        result["render_count"] = content.count("enter:Render")

        # 检查失败标志
        if "读取地图[sanguo]失败, 游戏退出!" in content:
            result["errors"].append("日志显示 '读取地图[sanguo]失败, 游戏退出!'")
        if "tab_interface" in content and "nil" in content:
            result["errors"].append("日志显示 tab_interface 为 nil（UI 初始化失败）")
        if f"读取地图[{expected_map_id}]失败" in content:
            result["errors"].append(f"日志显示 '读取地图[{expected_map_id}]失败'")

        # 尾部日志
        lines = content.strip().splitlines()
        result["tail_lines"] = lines[-20:] if len(lines) >= 20 else lines

        # 综合判定
        result["ok"] = (
            result["map_id_match"]
            and result["has_sanguo_o"]
            and result["after_run_count"] > 2
            and result["render_count"] > 2
            and len(result["errors"]) == 0
        )

        return result
