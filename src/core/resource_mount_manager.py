# -*- coding: utf-8 -*-
"""ResourceMountManager — sl/map.map 虚拟文件系统准备.

原启动器流程:
  1. 从 map/{id}.sl 解压 LuaRDGTM 包
  2. 写入 sl/map.map (虚拟文件系统)
  3. 游戏从 sl/map.map 中读取 map/sanguo/sanguo.o 等资源
"""

import lzma
from pathlib import Path
from typing import Optional

from .map_package_analyzer import MapPackageAnalyzer
from .map_launch_manifest import MapLaunchManifest
from .map_catalog import MapCatalog


class ResourceMountManager:
    """管理 sl/map.map 虚拟文件系统的创建和验证."""

    def __init__(self, game_dir: Path, cache_dir: Optional[Path] = None):
        self.game_dir = Path(game_dir)
        self.cache_dir = cache_dir or (self.game_dir.parent / "cache" / "launch")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def prepare(self, map_id: int, sl_path: Path) -> MapLaunchManifest:
        """解压 .sl 并写入 sl/map.map."""
        manifest = MapLaunchManifest(
            map_id=map_id,
            game_dir=self.game_dir,
            sl_path=sl_path,
        )

        sl_path = Path(sl_path)
        if not sl_path.exists():
            manifest.add_error(f".sl 文件不存在: {sl_path}")
            manifest.strategy = "missing_sl"
            return manifest

        report = MapPackageAnalyzer.analyze(sl_path)
        if not report["ok"]:
            manifest.add_error(report.get("error") or ".sl 格式验证未通过")
            manifest.strategy = "invalid_sl"
            return manifest

        manifest.set_hashes(
            sl_sha256=report.get("sl_sha256"),
            dec_sha256=report.get("dec_sha256"),
        )

        # 解压并写入 sl/map.map (虚拟文件系统)
        try:
            sl_dir = self.game_dir / "sl"
            sl_dir.mkdir(exist_ok=True)
            map_map = sl_dir / "map.map"

            data = sl_path.read_bytes()
            decompressed = lzma.decompress(data)
            map_map.write_bytes(decompressed)

            manifest.unpacked_path = map_map
            manifest.mount_points = [map_map]
            manifest.strategy = "sl_vfs"
        except Exception as e:
            manifest.add_error(f"解压 sl/map.map 失败: {e}")
            manifest.strategy = "decompress_failed"

        return manifest

    def dry_run(self, map_id: int, sl_path: Path) -> dict:
        """校验报告，不做文件操作."""
        catalog = MapCatalog(self.game_dir)
        return {
            "map_id": map_id,
            "catalog_diag": catalog.diagnose(map_id),
            "sl_analysis": MapPackageAnalyzer.analyze(sl_path),
            "ready": catalog.diagnose(map_id) is None and MapPackageAnalyzer.analyze(sl_path)["ok"],
        }
