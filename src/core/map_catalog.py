# -*- coding: utf-8 -*-
"""MapCatalog — 扫描地图库，建立只读索引."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib


class MapCatalog:
    """扫描 data/map/ 目录，建立地图 ID 到 .map/.sl 的索引."""

    def __init__(self, game_dir: Path):
        self.game_dir = Path(game_dir)
        self.map_dir = self.game_dir / "map"
        self._index: Dict[int, dict] = {}
        self._scan()

    def _scan(self):
        """扫描目录建立索引."""
        self._index.clear()
        if not self.map_dir.exists():
            return

        for entry in self.map_dir.iterdir():
            if not entry.is_file():
                continue
            name = entry.name
            if name.endswith(".map"):
                try:
                    map_id = int(name[:-4])
                except ValueError:
                    continue
                rec = self._index.setdefault(map_id, {"map_id": map_id})
                rec["map_path"] = entry
                rec["map_size"] = entry.stat().st_size
            elif name.endswith(".sl"):
                try:
                    map_id = int(name[:-3])
                except ValueError:
                    continue
                rec = self._index.setdefault(map_id, {"map_id": map_id})
                rec["sl_path"] = entry
                rec["sl_size"] = entry.stat().st_size

        # 诊断标记
        for rec in self._index.values():
            rec["has_map"] = "map_path" in rec
            rec["has_sl"] = "sl_path" in rec
            rec["ok"] = rec["has_map"] and rec["has_sl"]

    def list_maps(self) -> List[int]:
        """返回所有已索引的地图 ID 列表."""
        return sorted(self._index.keys())

    def get_info(self, map_id: int) -> Optional[dict]:
        """获取指定地图的索引信息."""
        return self._index.get(map_id)

    def diagnose(self, map_id: int) -> Optional[str]:
        """返回地图的诊断信息，None 表示健康."""
        rec = self._index.get(map_id)
        if rec is None:
            return f"地图 {map_id} 未找到"
        if not rec["has_map"]:
            return f"地图 {map_id} 缺少 .map 元数据文件"
        if not rec["has_sl"]:
            return f"地图 {map_id} 缺少 .sl 运行包"
        # 格式验证（使用 MapPackageAnalyzer 检查 .sl 是否可解压）
        if rec.get("sl_path"):
            from .map_package_analyzer import MapPackageAnalyzer
            report = MapPackageAnalyzer.analyze(rec["sl_path"])
            if not report["ok"]:
                return report.get("error") or f"地图 {map_id} .sl 格式验证失败"
        return None

    def all_diagnoses(self) -> Dict[int, str]:
        """返回所有异常地图的诊断字典."""
        result = {}
        for mid in self.list_maps():
            msg = self.diagnose(mid)
            if msg:
                result[mid] = msg
        return result

    def refresh(self):
        """重新扫描目录."""
        self._scan()
