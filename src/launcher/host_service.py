# -*- coding: utf-8 -*-
"""SL10002 本地 HostService — 模拟游戏服务器会话（TCP 29002）."""

import socket
import struct
import time
import threading
from pathlib import Path

HOST_PORT = 29002


def _build_packet(opcode: int, payload: bytes) -> bytes:
    """构建数据包: opcode(u16) + len(u16) + payload."""
    return struct.pack("<HH", opcode, len(payload)) + payload


def _build_login_result(player_slot: int) -> bytes:
    """0x013A 登录成功响应 (0x34 bytes)."""
    b = bytearray(0x34)
    unix = int(time.time())
    struct.pack_into("<I", b, 0x00, max(1, player_slot))  # global_id
    struct.pack_into("<I", b, 0x04, unix)                  # server_time
    struct.pack_into("<I", b, 0x08, 1)                     # session_ok
    struct.pack_into("<I", b, 0x0C, 1)                     # room_id
    return bytes(b)


def _build_control_frame(start: int, turn: int, keep_alive: int) -> bytes:
    """控制帧 (12 bytes): start, fps=30, turn, keep_alive."""
    b = bytearray(12)
    struct.pack_into("<I", b, 0, start)
    b[4] = 30                    # fps
    b[5] = turn & 0xFF           # turn
    struct.pack_into("<I", b, 6, keep_alive)
    return bytes(b)


def _build_player_record(slot: int, player_slot: int, player_name: str) -> bytes:
    """0x017A 玩家记录 (0x6F bytes each)."""
    pid = slot + 1
    r = bytearray(0x6F)
    uid = 100001 + slot
    struct.pack_into("<I", r, 0x00, uid)
    struct.pack_into("<I", r, 0x05, uid)
    name_bytes = player_name.encode("utf-16-le")[:0x60]
    r[0x09:0x09+len(name_bytes)] = name_bytes
    r[0x69] = slot       # network pos
    # side: 1-10=side1, 11-22=side2, 23=neutral hostile, 24=neutral
    if pid <= 10: r[0x6A] = 1
    elif pid <= 22: r[0x6A] = 2
    elif pid == 23: r[0x6A] = 23
    else: r[0x6A] = 24
    return bytes(r)


class HostService:
    """本地游戏服务器会话模拟."""

    def __init__(self, player_slot: int = 1, player_name: str = "Player1"):
        self.player_slot = player_slot
        self.player_name = player_name
        self._sock = None
        self._running = False
        self._thread = None
        self._keep_counter = 0

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass

    def _run(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind(("127.0.0.1", HOST_PORT))
            self._sock.listen(1)
            self._sock.settimeout(60)
            self._log(f"HostService listening on 127.0.0.1:{HOST_PORT}")

            while self._running:
                try:
                    conn, addr = self._sock.accept()
                    self._log(f"Game connected from {addr}")
                    self._handle_game(conn)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        self._log(f"Accept error: {e}")
                    break
        except Exception as e:
            self._log(f"HostService error: {e}")

    def _handle_game(self, conn: socket.socket):
        conn.settimeout(30)
        buf = b""
        try:
            # 发送登录成功
            login_payload = _build_login_result(self.player_slot)
            conn.sendall(_build_packet(0x013A, login_payload))
            self._log(f"Sent login result (0x013A)")

            while self._running:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    buf += data
                    while len(buf) >= 4:
                        opcode = struct.unpack_from("<H", buf, 0)[0]
                        plen = struct.unpack_from("<H", buf, 2)[0]
                        total = 4 + plen
                        if len(buf) < total:
                            break
                        # 处理并响应
                        self._handle_opcode(conn, opcode, buf[4:total])
                        buf = buf[total:]
                except socket.timeout:
                    self._keep_counter += 1
                    cf = _build_control_frame(0, 0, self._keep_counter)
                    try:
                        conn.sendall(_build_packet(0xFFFF, cf))
                    except Exception:
                        break
                except Exception:
                    break
        except Exception as e:
            self._log(f"Session error: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
            self._log("Game disconnected")

    def _handle_opcode(self, conn: socket.socket, opcode: int, payload: bytes):
        """处理游戏发来的 opcode."""
        if opcode == 0x017A:
            # 玩家列表请求 — 发送 24 个玩家记录
            records = b""
            for slot in range(24):
                records += _build_player_record(slot, self.player_slot, self.player_name)
            # 先发头部 (0x015A)
            header = bytearray(8)
            struct.pack_into("<I", header, 0, 24)  # count
            struct.pack_into("<H", header, 4, 0)
            struct.pack_into("<H", header, 6, 0x6F)  # record size
            conn.sendall(_build_packet(0x015A, bytes(header)))
            conn.sendall(_build_packet(0x017A, records))
            self._log(f"Sent player records (0x015A+0x017A)")

        elif opcode == 0x016E:
            conn.sendall(_build_packet(0x016E, b"\x00\x00"))

        elif opcode == 0x0186:
            resp = bytearray(4)
            struct.pack_into("<I", resp, 0, 1)
            conn.sendall(_build_packet(0x0186, bytes(resp)))

        elif opcode == 0x0138:
            # 心跳 — 发送控制帧
            cf = _build_control_frame(2, 0, self._keep_counter)
            conn.sendall(_build_packet(0xFFFF, cf))

    def _log(self, msg: str):
        path = Path("data/SL10002_host_service.log")
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {msg}\n")
        except Exception:
            pass
