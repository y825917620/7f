# -*- coding: utf-8 -*-
"""ResourceMountManager — 游戏自行加载 .sl，启动器只需确保文件存在."""

from pathlib import Path
from typing import Optional

from .map_package_analyzer import MapPackageAnalyzer
from .map_launch_manifest import MapLaunchManifest
from .map_catalog import MapCatalog


class ResourceMountManager:
    """资源就绪检查 — 游戏引擎自行从 map/{id}.sl 加载地图。

    底层研究发现：
    - game.exe 内部解压 map/{id}.sl 并创建 map/sanguo/sanguo.o
    - 启动器不需要做文件挂载（sl/map.map 反而会干扰游戏）
    - 启动器只需确保 .sl 文件存在且可读
    """

    def __init__(self, game_dir: Path, cache_dir: Optional[Path] = None):
        self.game_dir = Path(game_dir)
        self.cache_dir = cache_dir or (self.game_dir.parent / "cache" / "launch")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def prepare(self, map_id: int, sl_path: Path) -> MapLaunchManifest:
        """验证资源就绪，生成 manifest（不做文件复制）。

        游戏引擎自行从 map/{id}.sl 加载地图数据，
        启动器只需确保文件存在且格式有效。
        """
        manifest = MapLaunchManifest(
            map_id=map_id,
            game_dir=self.game_dir,
            sl_path=sl_path,
        )

        # 验证 .sl 文件存在
        sl_path = Path(sl_path)
        if not sl_path.exists():
            manifest.add_error(f".sl 文件不存在: {sl_path}")
            manifest.strategy = "missing_sl"
            return manifest

        # 验证 .sl 可解压且为有效 LuaRDGTM
        report = MapPackageAnalyzer.analyze(sl_path)
        if not report["ok"]:
            manifest.add_error(report.get("error") or ".sl 格式验证未通过")
            manifest.strategy = "invalid_sl"
            return manifest

        manifest.set_hashes(
            sl_sha256=report.get("sl_sha256"),
            dec_sha256=report.get("dec_sha256"),
        )
        manifest.strategy = "game_native"
        manifest._sl_report = report
        return manifest

    def dry_run(self, map_id: int, sl_path: Path) -> dict:
        """校验报告，不做任何文件操作."""
        catalog = MapCatalog(self.game_dir)
        return {
            "map_id": map_id,
            "catalog_diag": catalog.diagnose(map_id),
            "sl_analysis": MapPackageAnalyzer.analyze(sl_path),
            "ready": catalog.diagnose(map_id) is None and MapPackageAnalyzer.analyze(sl_path)["ok"],
        }
