# -*- coding: utf-8 -*-
"""ResourceMountManager — 按策略执行地图包挂载."""

import shutil
from pathlib import Path
from typing import List, Optional

from .map_package_analyzer import MapPackageAnalyzer
from .map_launch_manifest import MapLaunchManifest
from .map_catalog import MapCatalog


class ResourceMountManager:
    """负责将解包后的地图包写入正确的运行态挂载点."""

    # 候选挂载点（相对于 game_dir）
    CANDIDATE_MOUNT_POINTS = [
        Path("sl") / "map.map",
        Path("core") / "sl" / "map.map",
    ]

    def __init__(self, game_dir: Path, cache_dir: Optional[Path] = None):
        self.game_dir = Path(game_dir)
        self.cache_dir = cache_dir or (self.game_dir.parent / "cache" / "launch")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def prepare(self, map_id: int, sl_path: Path) -> MapLaunchManifest:
        """为一次启动准备地图资源，生成 manifest.

        Steps:
            1. 分析 .sl 文件
            2. 解压到缓存目录
            3. 计算哈希
            4. 复制到挂载点
            5. 生成 manifest
        """
        manifest = MapLaunchManifest(
            map_id=map_id,
            game_dir=self.game_dir,
            sl_path=sl_path,
        )

        # 1. 分析
        report = MapPackageAnalyzer.analyze(sl_path)
        if not report["ok"]:
            manifest.add_error(report.get("error") or ".sl 分析未通过")
            manifest.strategy = "analysis_failed"
            return manifest

        manifest.set_hashes(sl_sha256=report.get("sl_sha256"))

        # 2. 解压到缓存
        cache_file = self.cache_dir / f"{map_id}_unpacked.map"
        try:
            decompressed = MapPackageAnalyzer.decompress(sl_path)
            if decompressed is None:
                manifest.add_error("LZMA 解压返回 None")
                manifest.strategy = "decompress_failed"
                return manifest
            cache_file.write_bytes(decompressed)
        except Exception as e:
            manifest.add_error(f"写入缓存失败: {e}")
            manifest.strategy = "cache_write_failed"
            return manifest

        manifest.unpacked_path = cache_file
        manifest.unpacked_sha256 = report.get("dec_sha256")

        # 3. 挂载到运行态路径
        mounted = []
        for rel_path in self.CANDIDATE_MOUNT_POINTS:
            target = self.game_dir / rel_path
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cache_file, target)
                mounted.append(target)
            except Exception as e:
                manifest.add_error(f"挂载到 {rel_path} 失败: {e}")

        if not mounted:
            manifest.strategy = "mount_failed"
            return manifest

        manifest.mount_points = mounted
        manifest.strategy = "file_mount"
        return manifest

    def prepare_with_strategy(self, map_id: int, sl_path: Path, strategy: str) -> MapLaunchManifest:
        """使用指定策略准备地图资源.

        Args:
            strategy: "file_mount" | "mapfile_arg" | "memory_map"
        """
        if strategy == "file_mount":
            return self.prepare(map_id, sl_path)

        manifest = MapLaunchManifest(map_id=map_id, game_dir=self.game_dir, sl_path=sl_path)
        report = MapPackageAnalyzer.analyze(sl_path)
        if not report["ok"]:
            manifest.add_error(report.get("error") or ".sl 分析未通过")
            manifest.strategy = "analysis_failed"
            return manifest

        manifest.set_hashes(sl_sha256=report.get("sl_sha256"))

        # 解压到缓存
        cache_file = self.cache_dir / f"{map_id}_unpacked.map"
        try:
            decompressed = MapPackageAnalyzer.decompress(sl_path)
            if decompressed is None:
                manifest.add_error("LZMA 解压返回 None")
                manifest.strategy = "decompress_failed"
                return manifest
            cache_file.write_bytes(decompressed)
        except Exception as e:
            manifest.add_error(f"写入缓存失败: {e}")
            manifest.strategy = "cache_write_failed"
            return manifest

        manifest.unpacked_path = cache_file
        manifest.unpacked_sha256 = report.get("dec_sha256")

        if strategy == "mapfile_arg":
            # /mapfile= 策略：不复制到游戏目录，仅记录缓存路径
            manifest.strategy = "mapfile_arg"
            manifest.mount_points = [cache_file]

        elif strategy == "memory_map":
            # MemoryMapName= 策略：不复制文件，由 GameBridge 创建内存映射
            manifest.strategy = "memory_map"
            manifest.mount_points = [cache_file]

        return manifest

    def dry_run(self, map_id: int, sl_path: Path) -> dict:
        """干运行：只生成校验报告，不实际挂载."""
        catalog = MapCatalog(self.game_dir)

        report = {
            "map_id": map_id,
            "catalog_diag": catalog.diagnose(map_id),
            "sl_analysis": MapPackageAnalyzer.analyze(sl_path),
            "candidate_mount_points": [str(self.game_dir / p) for p in self.CANDIDATE_MOUNT_POINTS],
        }
        report["ready"] = (
            report["catalog_diag"] is None
            and report["sl_analysis"]["ok"]
        )
        return report

    def cleanup(self, manifest: MapLaunchManifest):
        """可选：启动失败后清理挂载点（但保留缓存和 manifest 用于诊断）."""
        pass
