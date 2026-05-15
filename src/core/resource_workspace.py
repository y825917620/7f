# -*- coding: utf-8 -*-
"""资源工作区 — 管理 maps/source、maps/workspace、mods、cache/launch 目录规范."""

import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from .map_package_analyzer import MapPackageAnalyzer


class ResourceWorkspace:
    """管理地图资源的导入、解包、工作区、缓存生命周期."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.source_dir = self.project_root / "maps" / "source"
        self.workspace_dir = self.project_root / "maps" / "workspace"
        self.mods_dir = self.project_root / "mods"
        self.cache_dir = self.project_root / "cache" / "launch"

        for d in [self.source_dir, self.workspace_dir, self.mods_dir, self.cache_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # === 地图导入 ===

    def import_map(self, map_id: int, map_path: Path, sl_path: Path) -> Optional[Path]:
        """将原始地图文件导入 source 层（只读保存）.

        Returns:
            manifest 文件路径，失败返回 None.
        """
        source_map_dir = self.source_dir / str(map_id)
        source_map_dir.mkdir(parents=True, exist_ok=True)

        dest_map = source_map_dir / f"{map_id}.map"
        dest_sl = source_map_dir / f"{map_id}.sl"

        if map_path and map_path.exists():
            shutil.copy2(map_path, dest_map)
        if sl_path and sl_path.exists():
            shutil.copy2(sl_path, dest_sl)

        return self._generate_map_manifest(map_id, source_map_dir)

    def _generate_map_manifest(self, map_id: int, source_dir: Path) -> Path:
        """为已导入的地图生成 map_manifest.json."""
        manifest = {
            "map_id": map_id,
            "imported_at": datetime.now().isoformat(),
            "source_dir": str(source_dir),
            "files": {},
        }

        map_file = source_dir / f"{map_id}.map"
        if map_file.exists():
            data = map_file.read_bytes()
            manifest["files"][".map"] = {
                "path": str(map_file),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }

        sl_file = source_dir / f"{map_id}.sl"
        if sl_file.exists():
            data = sl_file.read_bytes()
            manifest["files"][".sl"] = {
                "path": str(sl_file),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            # 预分析
            report = MapPackageAnalyzer.analyze(sl_file)
            manifest["files"][".sl"]["analysis"] = {
                "ok": report["ok"],
                "decompressed_size": report["decompressed_size"],
                "dec_sha256": report.get("dec_sha256", ""),
                "header_valid": report["header_valid"],
            }

        manifest_path = source_dir / "map_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest_path

    def load_map_manifest(self, map_id: int) -> Optional[dict]:
        """读取地图的 map_manifest.json."""
        path = self.source_dir / str(map_id) / "map_manifest.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # === 解包到工作区 ===

    def unpack_to_workspace(self, map_id: int, sl_path: Optional[Path] = None) -> Optional[Path]:
        """解包 .sl 到工作区，不污染游戏运行目录.

        Returns:
            解包后文件的路径，失败返回 None.
        """
        if sl_path is None:
            sl_path = self.source_dir / str(map_id) / f"{map_id}.sl"
            if not sl_path.exists():
                return None

        workspace_dir = self.workspace_dir / str(map_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)

        decompressed = MapPackageAnalyzer.decompress(sl_path)
        if decompressed is None:
            return None

        unpacked_file = workspace_dir / f"{map_id}_unpacked.map"
        unpacked_file.write_bytes(decompressed)

        # 记录解包信息
        info = {
            "map_id": map_id,
            "unpacked_at": datetime.now().isoformat(),
            "source_sl": str(sl_path),
            "sl_sha256": hashlib.sha256(sl_path.read_bytes()).hexdigest(),
            "unpacked_size": len(decompressed),
            "unpacked_sha256": hashlib.sha256(decompressed).hexdigest(),
        }
        (workspace_dir / "unpack_info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        return unpacked_file

    # === 启动缓存 ===

    def prepare_launch_cache(self, map_id: int, unpacked_path: Path) -> Path:
        """将解包后的地图包复制到启动缓存目录.

        Returns:
            缓存文件路径.
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.cache_dir / f"{map_id}_{session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)

        cached = session_dir / "map_package.bin"
        shutil.copy2(unpacked_path, cached)
        return cached

    # === Mod 管理 ===

    def create_mod(self, mod_id: str, description: str = "") -> Path:
        """创建一个新的 mod 目录."""
        mod_dir = self.mods_dir / mod_id
        mod_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "mod_id": mod_id,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "enabled": True,
            "overrides": {},
        }
        (mod_dir / "mod_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return mod_dir

    def list_mods(self) -> List[dict]:
        """列出所有 mod."""
        mods = []
        if not self.mods_dir.exists():
            return mods
        for d in self.mods_dir.iterdir():
            if d.is_dir():
                mf = d / "mod_manifest.json"
                if mf.exists():
                    mods.append(json.loads(mf.read_text(encoding="utf-8")))
        return mods

    # === 游戏资源索引 ===

    def index_game_resources(self, resource_dir: Path) -> dict:
        """扫描公共游戏资源目录，建立只读索引."""
        index = {"base_dir": str(resource_dir), "files": {}}
        if not resource_dir.exists():
            return index

        for entry in resource_dir.rglob("*"):
            if entry.is_file():
                rel = str(entry.relative_to(resource_dir))
                try:
                    stat = entry.stat()
                    index["files"][rel] = {
                        "bytes": stat.st_size,
                        "mtime": stat.st_mtime,
                    }
                except Exception:
                    pass
        return index
