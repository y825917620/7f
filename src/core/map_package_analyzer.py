# -*- coding: utf-8 -*-
"""MapPackageAnalyzer — 只读分析 .sl 压缩包，验证并解包."""

import lzma
import hashlib
from pathlib import Path
from typing import Optional, Tuple


class MapPackageAnalyzer:
    """分析 .sl 文件：验证 LZMA 头、解压、校验 LuaRDGTM 运行包."""

    # 固定的 LZMA 属性头（pb=5, lp=0, lc=3, dict_size=64MB）
    EXPECTED_LZMA_PROPS = bytes([0x5d, 0x00, 0x00, 0x40, 0x00])
    EXPECTED_HEADER = b"LuaRDGTM"

    @classmethod
    def analyze(cls, sl_path: Path) -> dict:
        """分析 .sl 文件，返回结构化报告（不抛出异常）.

        Returns:
            {
                "ok": bool,
                "map_id": int or None,
                "sl_size": int,
                "lzma_props": str,          # hex
                "lzma_props_valid": bool,
                "uncomp_size_from_header": int,
                "decompressed_size": int,
                "size_match": bool,
                "header_valid": bool,       # LuaRDGTM
                "sl_sha256": str,
                "dec_sha256": str,
                "error": str or None,
            }
        """
        report = {
            "ok": False,
            "map_id": None,
            "sl_size": 0,
            "lzma_props": "",
            "lzma_props_valid": False,
            "uncomp_size_from_header": 0,
            "decompressed_size": 0,
            "size_match": False,
            "header_valid": False,
            "sl_sha256": "",
            "dec_sha256": "",
            "error": None,
        }

        sl_path = Path(sl_path)
        if not sl_path.exists():
            report["error"] = f".sl 文件不存在: {sl_path}"
            return report

        # 解析 map_id
        try:
            report["map_id"] = int(sl_path.stem)
        except ValueError:
            report["error"] = f"无法从文件名解析地图 ID: {sl_path.name}"
            return report

        report["sl_size"] = sl_path.stat().st_size

        # 读取并计算 sha256
        try:
            data = sl_path.read_bytes()
        except Exception as e:
            report["error"] = f"读取 .sl 失败: {e}"
            return report

        report["sl_sha256"] = hashlib.sha256(data).hexdigest()

        if len(data) < 13:
            report["error"] = f".sl 文件过小 ({len(data)} bytes)"
            return report

        # 解析 LZMA 头
        props = data[:5]
        report["lzma_props"] = props.hex()
        report["lzma_props_valid"] = (props == cls.EXPECTED_LZMA_PROPS)

        uncomp_size = int.from_bytes(data[5:13], "little")
        report["uncomp_size_from_header"] = uncomp_size

        compressed = data[13:]

        # 尝试解压
        try:
            decompressor = lzma.LZMADecompressor(
                format=lzma.FORMAT_RAW,
                filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 67108864}],
            )
            decompressed = decompressor.decompress(compressed)
            report["decompressed_size"] = len(decompressed)
            report["dec_sha256"] = hashlib.sha256(decompressed).hexdigest()
            report["size_match"] = (len(decompressed) == uncomp_size)
            report["header_valid"] = decompressed.startswith(cls.EXPECTED_HEADER)
        except Exception as e:
            report["error"] = f"LZMA 解压失败: {e}"
            return report

        # 综合判定
        report["ok"] = (
            report["lzma_props_valid"]
            and report["size_match"]
            and report["header_valid"]
        )
        if not report["ok"] and report["error"] is None:
            parts = []
            if not report["lzma_props_valid"]:
                parts.append("LZMA 属性头不匹配")
            if not report["size_match"]:
                parts.append(f"解压大小不匹配 (期望 {uncomp_size}, 实际 {report['decompressed_size']})")
            if not report["header_valid"]:
                parts.append("解压后头部不是 LuaRDGTM")
            report["error"] = "; ".join(parts)

        return report

    @classmethod
    def decompress(cls, sl_path: Path) -> Optional[bytes]:
        """解压 .sl 文件，返回解压后的 bytes，失败返回 None."""
        report = cls.analyze(sl_path)
        if not report["ok"]:
            return None
        data = sl_path.read_bytes()
        compressed = data[13:]
        decompressor = lzma.LZMADecompressor(
            format=lzma.FORMAT_RAW,
            filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 67108864}],
        )
        return decompressor.decompress(compressed)

    @classmethod
    def batch_analyze(cls, map_ids: list, map_dir: Path) -> dict:
        """批量分析多张地图，返回汇总报告.

        Returns:
            {
                "total": int,
                "ok": int,
                "failed": int,
                "missing_sl": int,
                "results": {map_id: report},
            }
        """
        summary = {"total": len(map_ids), "ok": 0, "failed": 0, "missing_sl": 0, "results": {}}
        for mid in map_ids:
            sl_path = map_dir / f"{mid}.sl"
            if not sl_path.exists():
                summary["missing_sl"] += 1
                summary["results"][mid] = {"ok": False, "error": ".sl 文件不存在"}
                continue
            report = cls.analyze(sl_path)
            summary["results"][mid] = report
            if report["ok"]:
                summary["ok"] += 1
            else:
                summary["failed"] += 1
        return summary
