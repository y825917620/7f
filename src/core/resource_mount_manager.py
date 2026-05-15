# -*- coding: utf-8 -*-
"""ResourceMountManager — 从 .sl 解包并双挂载到 sl/map.map + core/sl/map.map."""

import lzma
from datetime import datetime
from pathlib import Path
from typing import Optional

from .map_package_analyzer import MapPackageAnalyzer
from .map_launch_manifest import MapLaunchManifest
from .map_catalog import MapCatalog


def _atomic_write(path: Path, data: bytes) -> None:
    """原子写入：先写临时文件再替换."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


class ResourceMountManager:
    """管理 sl/map.map 虚拟文件系统的创建和验证."""

    # 挂载点 — 同时写根目录和 core 目录，让运行时读取路径可验证。
    MOUNT_POINTS = [
        Path("sl") / "map.map",
        Path("core") / "sl" / "map.map",
    ]

    def __init__(self, game_dir: Path, cache_dir: Optional[Path] = None):
        self.game_dir = Path(game_dir)
        self.cache_dir = cache_dir or (self.game_dir.parent / "cache" / "launch")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def prepare(self, map_id: int, sl_path: Path) -> MapLaunchManifest:
        """解压 .sl 并双挂载到 sl/map.map 和 core/sl/map.map.

        Steps:
        1. 分析 .sl 格式
        2. 解压到缓存目录
        3. 双挂载到两个运行态路径
        4. 生成 manifest
        """
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

        # 解压 — 优先用原版方式 lzma.decompress(整个文件)
        raw_data = sl_path.read_bytes()
        try:
            decompressed = lzma.decompress(raw_data)
        except Exception:
            # 回退: FORMAT_RAW LZMA1 (兼容测试数据和非标准格式)
            try:
                decomp = lzma.LZMADecompressor(
                    format=lzma.FORMAT_RAW,
                    filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 67108864}],
                )
                decompressed = decomp.decompress(raw_data[13:])
            except Exception as e:
                manifest.add_error(f"LZMA 解压失败: {e}")
                manifest.strategy = "decompress_failed"
                return manifest

        # 写缓存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.cache_dir / f"{map_id}_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        cache_file = session_dir / "map_package.bin"
        cache_file.write_bytes(decompressed)

        manifest.set_hashes(
            sl_sha256=report.get("sl_sha256"),
            unpacked_sha256=report.get("dec_sha256"),
        )

        # 双挂载
        mounted = []
        for rel_path in self.MOUNT_POINTS:
            target = self.game_dir / rel_path
            _atomic_write(target, decompressed)
            mounted.append(target)

        manifest.unpacked_path = cache_file
        manifest.mount_points = mounted
        manifest.strategy = "file_dual_mount"
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
