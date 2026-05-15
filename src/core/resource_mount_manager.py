# -*- coding: utf-8 -*-
"""ResourceMountManager — 拆包 .sl → map/{id}/{id}.map + map/{id}/{id}.o (Blowfish解密)."""

import lzma
import struct
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .map_launch_manifest import MapLaunchManifest
from .map_catalog import MapCatalog

# gpigame.dll DecryptMap 使用的密钥
_BLOWFISH_KEY = b"DEFAULT_KEY" + b"\x00"


def _extract_sl(sl_path: Path, game_dir: Path, map_id: int) -> tuple:
    """拆包 .sl: 返回 (map_data, decrypted_payload, 错误信息).

    Steps:
    1. LZMA_ALONE 解压 .sl
    2. 解析 LuaRDGTM 头
    3. 提取内嵌 .map
    4. Blowfish/ECB 解密 payload → Lua 5.1 bytecode
    """
    try:
        raw = sl_path.read_bytes()
        dec = lzma.decompress(raw, format=lzma.FORMAT_ALONE)

        if dec[:8] != b"LuaRDGTM":
            return None, None, "不是 LuaRDGTM 容器"

        map_size = struct.unpack_from("<I", dec, 0x08)[0]
        payload_size = struct.unpack_from("<I", dec, 0x0C)[0]
        map_off = 0x10
        payload_off = map_off + map_size

        map_data = dec[map_off:payload_off]
        payload_enc = dec[payload_off:payload_off + payload_size]

        # Blowfish/ECB 解密
        n = len(payload_enc) & ~7
        cipher = Cipher(algorithms.Blowfish(_BLOWFISH_KEY), modes.ECB())
        decryptor = cipher.decryptor()
        payload_dec = decryptor.update(payload_enc[:n]) + decryptor.finalize()

        return map_data, payload_dec, None
    except Exception as e:
        return None, None, f"拆包 .sl 失败: {e}"


class ResourceMountManager:
    """拆包 .sl → map/{id}/{id}.map + map/{id}/{id}.o."""

    def __init__(self, game_dir: Path, cache_dir: Optional[Path] = None):
        self.game_dir = Path(game_dir)
        self.cache_dir = cache_dir or (self.game_dir.parent / "cache" / "launch")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def prepare(self, map_id: int, sl_path: Path) -> MapLaunchManifest:
        """拆包 .sl 并写入 map/{id}/{id}.map 和 map/{id}/{id}.o."""
        manifest = MapLaunchManifest(map_id=map_id, game_dir=self.game_dir, sl_path=sl_path)

        if not Path(sl_path).exists():
            manifest.add_error(f".sl 文件不存在: {sl_path}")
            manifest.strategy = "missing_sl"
            return manifest

        map_data, lua_payload, err = _extract_sl(Path(sl_path), self.game_dir, map_id)
        if err:
            manifest.add_error(err)
            manifest.strategy = "extract_failed"
            return manifest

        # 写入 map/{id}/{id}.map 和 map/{id}/{id}.o
        map_dir = self.game_dir / "map" / str(map_id)
        map_dir.mkdir(parents=True, exist_ok=True)

        map_path = map_dir / f"{map_id}.map"
        o_path = map_dir / f"{map_id}.o"
        map_path.write_bytes(map_data)
        o_path.write_bytes(lua_payload)

        manifest.unpacked_path = o_path
        manifest.mount_points = [map_path, o_path]
        manifest.strategy = "sl_extract_decrypt"
        return manifest

    def dry_run(self, map_id: int, sl_path: Path) -> dict:
        catalog = MapCatalog(self.game_dir)
        return {
            "map_id": map_id,
            "catalog_diag": catalog.diagnose(map_id),
            "ready": catalog.diagnose(map_id) is None and Path(sl_path).exists(),
        }
