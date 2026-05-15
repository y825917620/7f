# -*- coding: utf-8 -*-
"""MapLaunchManifest — 一次启动所需的结构化清单."""

import json
import hashlib
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime


class MapLaunchManifest:
    """记录一次启动的完整上下文，作为唯一真实来源."""

    def __init__(
        self,
        map_id: int,
        game_dir: Path,
        map_path: Optional[Path] = None,
        sl_path: Optional[Path] = None,
        unpacked_path: Optional[Path] = None,
        mount_points: Optional[List[Path]] = None,
        options: Optional[List[int]] = None,
        player_index: int = 0,
        resolution_index: int = 0,
    ):
        self.map_id = map_id
        self.game_dir = Path(game_dir)
        self.map_path = Path(map_path) if map_path else None
        self.sl_path = Path(sl_path) if sl_path else None
        self.unpacked_path = Path(unpacked_path) if unpacked_path else None
        self.mount_points = [Path(p) for p in (mount_points or [])]
        self.options = list(options) if options else [-1] * 10 + [0]
        self.player_index = player_index
        self.resolution_index = resolution_index
        self.created_at = datetime.now().isoformat()
        self.sl_sha256: Optional[str] = None
        self.unpacked_sha256: Optional[str] = None
        self.strategy: str = "unknown"
        self.errors: List[str] = []

    def set_hashes(self, sl_sha256: Optional[str] = None, unpacked_sha256: Optional[str] = None):
        self.sl_sha256 = sl_sha256
        self.unpacked_sha256 = unpacked_sha256

    def add_error(self, msg: str):
        self.errors.append(msg)

    def is_valid(self) -> bool:
        return len(self.errors) == 0 and self.unpacked_path is not None and self.unpacked_path.exists()

    def to_dict(self) -> dict:
        return {
            "map_id": self.map_id,
            "game_dir": str(self.game_dir),
            "map_path": str(self.map_path) if self.map_path else None,
            "sl_path": str(self.sl_path) if self.sl_path else None,
            "unpacked_path": str(self.unpacked_path) if self.unpacked_path else None,
            "mount_points": [str(p) for p in self.mount_points],
            "options": self.options,
            "player_index": self.player_index,
            "resolution_index": self.resolution_index,
            "created_at": self.created_at,
            "sl_sha256": self.sl_sha256,
            "unpacked_sha256": self.unpacked_sha256,
            "strategy": self.strategy,
            "errors": self.errors,
            "valid": self.is_valid(),
        }

    def save(self, path: Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> "MapLaunchManifest":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        m = cls(
            map_id=data["map_id"],
            game_dir=Path(data["game_dir"]),
            map_path=Path(data["map_path"]) if data.get("map_path") else None,
            sl_path=Path(data["sl_path"]) if data.get("sl_path") else None,
            unpacked_path=Path(data["unpacked_path"]) if data.get("unpacked_path") else None,
            mount_points=[Path(p) for p in data.get("mount_points", [])],
            options=data.get("options"),
            player_index=data.get("player_index", 0),
            resolution_index=data.get("resolution_index", 0),
        )
        m.created_at = data.get("created_at", m.created_at)
        m.sl_sha256 = data.get("sl_sha256")
        m.unpacked_sha256 = data.get("unpacked_sha256")
        m.strategy = data.get("strategy", "unknown")
        m.errors = data.get("errors", [])
        return m
