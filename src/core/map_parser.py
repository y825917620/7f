# -*- coding: utf-8 -*-
""".map 文件解析器 - 提取选项定义、玩家配置、缩略图、VIP 信息等."""

import re
import struct
from pathlib import Path


class MapOptionParser:
    """解析 .map 文件中的选项定义、玩家配置、缩略图等."""

    # 地图信息类关键词（通常不显示在游戏选项面板中）
    INFO_KEYWORDS = {
        "作者", "QQ群", "Q群", "qq群", "修改", "公告", "版本", "更新",
        "完成度", "死亡次数", "本图", "论坛", "感谢", "地图作者",
    }

    @staticmethod
    def _read_text(data, encoding="gb18030"):
        """将二进制数据解码为文本，用于正则搜索."""
        return data.decode(encoding, errors="replace")

    @staticmethod
    def _extract_fourcc(data, marker):
        """在二进制数据中搜索 FourCC 标记，读取其 offset + size 并返回内容.

        Args:
            data: 文件二进制数据 (bytes)
            marker: FourCC 标记 (如 b'CHNM', b'INFO')

        Returns:
            解码后的字符串，如果未找到则返回空字符串.
        """
        pos = data.find(marker)
        if pos == -1:
            return ""
        # FourCC 后紧跟 4 字节 offset + 4 字节 size (little-endian)
        if pos + 12 > len(data):
            return ""
        offset = struct.unpack_from("<I", data, pos + 4)[0]
        size = struct.unpack_from("<I", data, pos + 8)[0]
        if offset + size > len(data) or size == 0:
            return ""
        content = data[offset:offset + size]
        # 去除尾部的 \x00 和控制字符
        content = content.rstrip(b'\x00').rstrip(bytes(range(1, 32)))
        try:
            return content.decode("gb18030", errors="replace").strip()
        except Exception:
            return ""

    @staticmethod
    def extract_thumbnail(map_path):
        """从 .map 文件中提取 LOGO 缩略图 (128x128 BMP).

        Returns:
            BMP 数据的 bytes，如果未找到则返回 None.
        """
        try:
            with open(map_path, "rb") as f:
                data = f.read()
        except Exception:
            return None

        # LOGO 是标准 BMP，固定大小 65590 字节（128x128, 32bpp）
        # 在文件中搜索 BMP 头 "BM" 并验证文件大小
        for i in range(len(data) - 6):
            if data[i:i+2] == b"BM":
                file_size = struct.unpack_from("<I", data, i + 2)[0]
                if file_size == 65590:
                    return data[i:i + file_size]
        return None

    @staticmethod
    def extract_mmap(map_path):
        """从 .map 文件中提取 MMAP 大地图预览 BMP.

        Returns:
            BMP 数据的 bytes，如果未找到则返回 None.
        """
        try:
            with open(map_path, "rb") as f:
                data = f.read()
        except Exception:
            return None

        candidates = []
        for i in range(len(data) - 6):
            if data[i:i+2] == b"BM":
                file_size = struct.unpack_from("<I", data, i + 2)[0]
                if 10000 < file_size < 5000000:  # 合理的 BMP 大小
                    candidates.append((i, file_size))

        if not candidates:
            return None

        # 如果只有一个候选，返回它
        if len(candidates) == 1:
            i, size = candidates[0]
            return data[i:i + size]

        # 如果有多个，选择最大的（MMAP 通常比 LOGO 大得多）
        # LOGO = 65590，MMAP 通常几十万字节
        candidates.sort(key=lambda x: x[1], reverse=True)
        i, size = candidates[0]
        return data[i:i + size]

    @staticmethod
    def parse(map_path):
        """解析 .map 文件，返回完整地图信息.

        Returns:
            {
                "options": [...],
                "player_num": 9,
                "player_mode": "正常",
                "bar_names": {...},
                "side_names": {...},
                "chn_name": "中文地图名",
                "info": "地图描述",
                "vip_info": {"sponsor": ..., "author": ..., "qq_group": ...},
            }
        """
        try:
            with open(map_path, "rb") as f:
                data = f.read()
        except Exception:
            return None

        text = MapOptionParser._read_text(data)

        # 1. 提取所有 #T#名称#默认值
        option_defs = []
        for m in re.finditer(r"#T#([^#\x00\n]+)#([^#\x00\n]+)", text):
            name = m.group(1).strip()
            default_val = m.group(2).strip()
            default_val = default_val.rstrip(''.join(chr(i) for i in range(32)))
            option_defs.append({"name": name, "default": default_val})

        # 2. 找到选项数量标记
        count_match = re.search(
            r"#T#[^#]+#[^#\x00\n]+\x00{0,10}(\x01\x00\x00\x00|\x02\x00\x00\x00|\x03\x00\x00\x00|\x04\x00\x00\x00|\x05\x00\x00\x00|\x06\x00\x00\x00|\x07\x00\x00\x00|\x08\x00\x00\x00|\x09\x00\x00\x00|\x0a\x00\x00\x00|\x0b\x00\x00\x00|\x0c\x00\x00\x00)",
            text,
        )
        option_count = 0
        if count_match:
            count_byte = count_match.group(1)
            option_count = count_byte[0] if isinstance(count_byte[0], int) else ord(count_byte[0])
        elif option_defs:
            option_count = len(option_defs)

        # 3. 解析 @N#值1#值2... 列表
        value_lists = []
        if count_match:
            count_pos = count_match.end()
            remaining = text[count_pos:count_pos + 5000]
            for m in re.finditer(r"@(\d+)#([^@\x00\n]+)", remaining):
                num_values = int(m.group(1))
                vals_text = m.group(2)
                vals = vals_text.split("#")
                if vals:
                    vals[-1] = vals[-1].rstrip(''.join(chr(i) for i in range(32)))
                if len(vals) == num_values:
                    value_lists.append(vals)
                elif len(vals) > num_values:
                    value_lists.append(vals[:num_values])
                else:
                    value_lists.append(vals)

        # 4. 将默认值与可选值列表匹配
        options = []
        for i, opt_def in enumerate(option_defs):
            if i >= option_count:
                break
            if i < len(value_lists):
                values = value_lists[i]
                default_idx = 0
                for idx, val in enumerate(values):
                    if val == opt_def["default"]:
                        default_idx = idx
                        break
                options.append({
                    "name": opt_def["name"],
                    "default_index": default_idx,
                    "values": values,
                })
            else:
                options.append({
                    "name": opt_def["name"],
                    "default_index": 0,
                    "values": [opt_def["default"]],
                })

        # 5. 提取玩家数量
        player_num = 1
        m = re.search(r"PLAYER_NUM=(\d+)", text)
        if m:
            player_num = int(m.group(1))

        # 6. 提取 player_mode
        player_mode = "正常"
        m = re.search(r'player_mode1_name="([^"]+)"', text)
        if m:
            player_mode = m.group(1)

        # 7. 提取 bar 名称
        bar_names = {}
        for m in re.finditer(r'bar(\d+)_name="([^"]+)"', text):
            bar_names[int(m.group(1))] = m.group(2)

        # 8. 提取 side 名称
        side_names = {}
        for m in re.finditer(r'side(\d+)_name="([^"]+)"', text):
            side_names[int(m.group(1))] = m.group(2)

        # 9. 提取中文地图名 (CHNM) — 使用二进制 FourCC 搜索
        chn_name = MapOptionParser._extract_fourcc(data, b"CHNM")

        # 10. 提取地图描述 (INFO) — 使用二进制 FourCC 搜索
        info = MapOptionParser._extract_fourcc(data, b"INFO")

        # 11. 提取 VIP/赞助信息（从选项中过滤）
        vip_info = {}
        for opt in options:
            name = opt["name"]
            vals = opt["values"]
            if "赞助" in name or "本图赞助" in name:
                vip_info["sponsor"] = vals[0] if vals else ""
            if "作者" in name and "本图作者" in name:
                vip_info["author"] = vals[0] if vals else ""
            if "QQ群" in name and "本图QQ群" in name:
                vip_info["qq_group"] = vals[0] if vals else ""

        return {
            "options": options,
            "player_num": player_num,
            "player_mode": player_mode,
            "bar_names": bar_names,
            "side_names": side_names,
            "chn_name": chn_name,
            "info": info,
            "vip_info": vip_info,
        }

    @staticmethod
    def get_game_options(parsed):
        """过滤出游戏选项（排除地图信息类选项）。返回最多10个选项。"""
        if not parsed:
            return []
        game_opts = []
        for opt in parsed["options"]:
            if len(opt["values"]) == 1:
                is_info = any(kw in opt["name"] for kw in MapOptionParser.INFO_KEYWORDS)
                if is_info:
                    continue
            game_opts.append(opt)
        return game_opts[:10]


if __name__ == "__main__":
    import json

    project_root = Path(__file__).parent.parent.parent
    results = {}
    for map_id in range(10001, 10109):
        path = project_root / "map" / f"{map_id}.map"
        parsed = MapOptionParser.parse(path)
        if parsed:
            game_opts = MapOptionParser.get_game_options(parsed)
            results[map_id] = {
                "all_options": [(o["name"], o["values"], o["default_index"]) for o in parsed["options"]],
                "game_options": [(o["name"], o["values"], o["default_index"]) for o in game_opts],
                "player_num": parsed["player_num"],
                "bar_names": parsed["bar_names"],
                "side_names": parsed["side_names"],
                "chn_name": parsed["chn_name"],
                "info": parsed["info"],
                "vip_info": parsed["vip_info"],
            }
            # 测试缩略图提取
            thumb = MapOptionParser.extract_thumbnail(path)
            results[map_id]["has_thumbnail"] = thumb is not None

    with open(project_root / "parsed_options_v2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Parsed {len(results)} maps")
    thumb_count = sum(1 for v in results.values() if v.get("has_thumbnail"))
    print(f"Thumbnails: {thumb_count}")
