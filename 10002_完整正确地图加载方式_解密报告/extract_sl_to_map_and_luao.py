#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析神龙/7F 系地图 .sl 容器：
1) 先对外层 .sl 做 LZMA 解压；
2) 识别 LuaRDGTM 容器头；
3) 拆出内嵌 .map；
4) 使用 gpigame.dll 中的 DEFAULT_KEY\0 做 Blowfish/ECB 解密；
5) 输出 Lua 5.1 bytecode .o。

仅用于你自己提供的样本做静态分析/兼容性研究。
"""
from pathlib import Path
import struct, lzma, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def parse_sl(sl_path: str, out_dir: str):
    sl_path = Path(sl_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = sl_path.read_bytes()

    # 10002.sl 外层是 raw LZMA_ALONE 格式。
    dec = lzma.decompress(raw, format=lzma.FORMAT_ALONE)
    (out_dir / f"{sl_path.stem}_decompressed_LuaRDGTM.bin").write_bytes(dec)

    if dec[:8] != b"LuaRDGTM":
        raise ValueError(f"not LuaRDGTM container, head={dec[:16].hex()}")

    map_size = struct.unpack_from("<I", dec, 0x08)[0]
    payload_size = struct.unpack_from("<I", dec, 0x0C)[0]
    map_off = 0x10
    payload_off = map_off + map_size

    map_data = dec[map_off:payload_off]
    payload_enc = dec[payload_off:payload_off + payload_size]

    map_out = out_dir / f"{sl_path.stem}.map"
    enc_out = out_dir / f"{sl_path.stem}_payload_encrypted.bin"
    lua_out = out_dir / f"{sl_path.stem}.o"

    map_out.write_bytes(map_data)
    enc_out.write_bytes(payload_enc)

    # gpigame.dll 调用时传入长度 0x0c，实际密钥为 DEFAULT_KEY + NUL。
    key = b"DEFAULT_KEY" + b"\x00"
    n = len(payload_enc) & ~7  # Blowfish 8-byte block 对齐
    cipher = Cipher(algorithms.Blowfish(key), modes.ECB())
    decryptor = cipher.decryptor()
    payload_dec = decryptor.update(payload_enc[:n]) + decryptor.finalize()
    lua_out.write_bytes(payload_dec)

    print("input:", sl_path)
    print("decompressed_size:", len(dec))
    print("magic:", dec[:8])
    print("map_size:", map_size, hex(map_size))
    print("payload_size:", payload_size, hex(payload_size))
    print("payload_encrypted_multiple8:", n, hex(n))
    print("payload_tail_bytes_not_decrypted:", len(payload_enc) - n)
    print("map_out:", map_out)
    print("lua_bytecode_out:", lua_out)
    print("lua_head:", payload_dec[:16].hex())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python extract_sl_to_map_and_luao.py 10002.sl out_dir")
        sys.exit(1)
    parse_sl(sys.argv[1], sys.argv[2])
