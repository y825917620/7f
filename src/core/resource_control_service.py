# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List

from .map_catalog import MapCatalog
from .map_launch_manifest import MapLaunchManifest
from .resource_mount_manager import ResourceMountManager


class ResourceControlService:
    """UI 面向的资源编排层 — 验证、准备、返回 manifest."""

    def __init__(self, game_dir: Path):
        self.game_dir = Path(game_dir)
        self.catalog = MapCatalog(self.game_dir)
        self.mount_manager = ResourceMountManager(self.game_dir)

    def prepare_launch_manifest(
        self,
        map_id: int,
        options: List[int],
        resolution_index: int = 0,
    ) -> MapLaunchManifest:
        """为指定地图准备启动清单.

        Returns:
            有效的 MapLaunchManifest（is_valid() 为 True）或带错误的 manifest.
        """
        rec = self.catalog.get_info(map_id)
        if rec is None:
            manifest = MapLaunchManifest(
                map_id=map_id,
                game_dir=self.game_dir,
                options=options,
                resolution_index=resolution_index,
            )
            manifest.strategy = "missing_catalog_record"
            manifest.add_error(f"地图 {map_id} 未在 {self.catalog.map_dir} 中找到")
            return manifest

        diag = self.catalog.diagnose(map_id)
        if diag:
            manifest = MapLaunchManifest(
                map_id=map_id,
                game_dir=self.game_dir,
                map_path=rec.get("map_path"),
                sl_path=rec.get("sl_path"),
                options=options,
                resolution_index=resolution_index,
            )
            manifest.strategy = "catalog_invalid"
            manifest.add_error(diag)
            return manifest

        manifest = self.mount_manager.prepare(map_id, rec["sl_path"])
        manifest.options = list(options)
        manifest.resolution_index = resolution_index
        return manifest
