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
    # game-side parser expects packet total length (header + payload), not payload length.
    total_len = 4 + len(payload)
    return struct.pack("<HH", opcode, total_len) + payload


def _build_login_result(player_slot: int) -> bytes:
    """0x013A 登录成功响应 (0x34 bytes)."""
    b = bytearray(0x34)
    unix = int(time.time())
    # global_id is treated as 64-bit by game net logs.
    global_id = 100000 + max(1, player_slot)
    struct.pack_into("<Q", b, 0x00, global_id)
    struct.pack_into("<I", b, 0x08, unix)                  # server_time
    struct.pack_into("<I", b, 0x0C, 1)                     # room_id
    return bytes(b)


def _build_control_frame(start: int, turn: int, keep_alive: int) -> bytes:
    """控制帧 (12 bytes): start, fps=30, turn, keep_alive."""
    b = bytearray(12)
    struct.pack_into("<I", b, 0, start)
    b[4] = 30                    # fps
    b[5] = (turn & 0xFF) if int(start) == 2 else 0
    struct.pack_into("<I", b, 6, keep_alive)
    return bytes(b)


def _build_ping_echo(payload: bytes, fallback_keepalive: int) -> bytes:
    # Mirror client 0x025D token payload to 0x015D when possible.
    if payload and len(payload) >= 4:
        return payload
    b = bytearray(4)
    struct.pack_into("<I", b, 0, fallback_keepalive)
    return bytes(b)


def _build_game_start_first_turn_payload() -> bytes:
    return _build_frame_pulse_payload(0)


def _build_frame_pulse_payload(frame: int) -> bytes:
    b = bytearray(5)
    struct.pack_into("<I", b, 0, max(0, int(frame)))
    b[4] = 1
    return bytes(b)


def _build_turn_sync_payload(frame: int, player_pos: int = 0) -> bytes:
    b = bytearray(13)
    struct.pack_into("<I", b, 0, max(0, int(frame)))
    b[4] = 2
    struct.pack_into("<H", b, 5, 6)
    struct.pack_into("<H", b, 7, 0x012E)
    b[9] = max(0, min(23, int(player_pos)))
    b[10] = 0
    struct.pack_into("<H", b, 11, 0)
    return bytes(b)


def _build_client_command_ack_payload(payload: bytes) -> bytes:
    return bytes(payload or b"")


def _build_client_command_turn_payload(frame: int, raw_packet: bytes) -> bytes:
    raw_packet = bytes(raw_packet or b"")
    cmd_len = min(len(raw_packet), 0xFFFF)
    b = bytearray(7 + cmd_len)
    struct.pack_into("<I", b, 0, max(0, int(frame)))
    b[4] = 2
    struct.pack_into("<H", b, 5, cmd_len)
    b[7:7 + cmd_len] = raw_packet[:cmd_len]
    return bytes(b)


def _is_load_complete_progress(payload: bytes) -> bool:
    # Observed 0x0261 payloads are: progress byte, marker byte.
    # Examples from runtime traces: 1e64, 2864, 3c64, 5064, 5a64, 6464.
    return len(payload) >= 2 and payload[0] == 0x64 and payload[1] == 0x64


def _build_room_info_payload(map_id: int, player_slot: int) -> bytes:
    b = bytearray(0x20)
    struct.pack_into("<I", b, 0x00, 1)
    struct.pack_into("<I", b, 0x04, int(map_id))
    struct.pack_into("<I", b, 0x08, max(1, int(player_slot)))
    struct.pack_into("<I", b, 0x0C, 1)
    struct.pack_into("<I", b, 0x10, 24)
    struct.pack_into("<I", b, 0x14, int(time.time()))
    struct.pack_into("<I", b, 0x18, 1)
    struct.pack_into("<I", b, 0x1C, 0)
    return bytes(b)


def _build_player_record(slot: int, player_slot: int, player_name: str) -> bytes:
    """0x017A 玩家记录 (0x6F bytes each)."""
    pid = slot + 1
    r = bytearray(0x6F)
    uid = 100001 + slot
    struct.pack_into("<I", r, 0x00, uid)
    struct.pack_into("<I", r, 0x05, uid)
    pid_name = _get_slot_name(slot, player_slot, player_name)
    name_bytes = (pid_name + "\0").encode("utf-16-le")[:0x60]
    r[0x09:0x09+len(name_bytes)] = name_bytes
    r[0x69] = slot       # network pos
    # side: 1-10=side1, 11-22=side2, 23=neutral hostile, 24=neutral
    if pid <= 10: r[0x6A] = 1
    elif pid <= 22: r[0x6A] = 2
    elif pid == 23: r[0x6A] = 23
    else: r[0x6A] = 24
    # The game scripts index player_type_* tables from 1. Zero is not a valid
    # ordinary-player type and crashes RefreshPlayerInfo().
    r[0x6B] = 1
    r[0x6C] = 1
    r[0x6D] = 1
    return bytes(r)


def _get_slot_name(slot: int, local_player_slot: int, local_player_name: str) -> str:
    pid = slot + 1
    if pid == 9:
        return "星雨阁"
    if pid == 20:
        return "炎黄联盟"
    if pid == 21:
        return "东夷集团"
    if pid == 22:
        return "上古邪神"
    if pid == 23:
        return "中立敌对"
    if pid == 24:
        return "中立无敌意"
    if pid == int(local_player_slot):
        return local_player_name
    if pid == 1:
        return "Player1"
    return f"P{pid}"


class HostService:
    """本地游戏服务器会话模拟."""

    def __init__(self, player_slot: int = 1, player_name: str = "Player1",
                 host_ip: str = "127.0.0.1", host_port: int = HOST_PORT):
        self.player_slot = player_slot
        self.player_name = player_name
        self.host_ip = host_ip
        self.host_port = int(host_port)
        self._sock = None
        self._udp_sock = None
        self._running = False
        self._thread = None
        self._udp_thread = None
        self._keep_counter = 0
        self._ready = threading.Event()
        self._client_lock = threading.Lock()
        self._active_conn = None

    def start(self):
        self._running = True
        self._ready.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._udp_thread = threading.Thread(target=self._run_udp, daemon=True)
        self._udp_thread.start()
        self._thread.start()

    def wait_until_ready(self, timeout: float = 3.0) -> bool:
        return self._ready.wait(timeout)

    def stop(self):
        self._running = False
        self._ready.clear()
        with self._client_lock:
            conn = self._active_conn
            self._active_conn = None
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        if self._udp_sock:
            try:
                self._udp_sock.close()
            except Exception:
                pass

    def _run(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind((self.host_ip, self.host_port))
            self._sock.listen(8)
            self._sock.settimeout(1.0)
            self._ready.set()
            self._log(f"HostService listening on {self.host_ip}:{self.host_port}")

            while self._running:
                try:
                    conn, addr = self._sock.accept()
                    self._log(f"Game connected from {addr}")
                    with self._client_lock:
                        old_conn = self._active_conn
                        self._active_conn = conn
                    if old_conn:
                        try:
                            old_conn.close()
                        except Exception:
                            pass
                    threading.Thread(target=self._handle_game, args=(conn,), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        self._log(f"Accept error: {e}")
                    break
        except Exception as e:
            self._log(f"HostService error: {e}")
        finally:
            self._ready.clear()

    def _run_udp(self):
        try:
            self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._udp_sock.bind((self.host_ip, self.host_port))
            self._udp_sock.settimeout(1.0)
            self._log(f"HostService UDP listening on {self.host_ip}:{self.host_port}")
            while self._running:
                try:
                    data, addr = self._udp_sock.recvfrom(4096)
                    if data:
                        self._udp_sock.sendto(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        self._log(f"UDP error: {e}")
                    break
        except Exception as e:
            self._log(f"HostService UDP error: {e}")

    def _send_session_bundle(self, conn: socket.socket, state: dict):
        # player list (internal 0x015A => wire 0x0130). This is session
        # players, not map owner slots; neutral/hostile map owners must not be
        # advertised as real connected players.
        local_slot = max(0, min(23, int(self.player_slot) - 1))
        records = _build_player_record(local_slot, self.player_slot, self.player_name)
        header = bytearray(8)
        struct.pack_into("<I", header, 0, 1)
        struct.pack_into("<H", header, 4, 0)
        struct.pack_into("<H", header, 6, 0x6F)
        conn.sendall(_build_packet(0x0130, bytes(header) + records))

        # Keep only the full player list.
        # In current runtime traces, sending extra 0x0150 after a 24-record list
        # makes the client-side player count become 25, then scripts fail in
        # RefreshPlayerInfo().

        # option/item/room info
        conn.sendall(_build_packet(0x0142, b"\x00"))
        conn.sendall(_build_packet(0x0144, b"\x00\x00"))
        conn.sendall(_build_packet(0x015C, _build_room_info_payload(state["map_id"], self.player_slot)))

        # refresh login/control and first turn to enter logic
        conn.sendall(_build_packet(0x013A, _build_login_result(self.player_slot)))
        conn.sendall(_build_packet(0x0133, _build_control_frame(2, state["turn"], state["keep_counter"])))
        conn.sendall(_build_packet(0x0138, _build_game_start_first_turn_payload()))
        state["bundle_sent"] = True
        state["client_ready"] = True
        self._log("postload session bundle sent")

    def _handle_game(self, conn: socket.socket):
        conn.settimeout(0.5)
        buf = b""
        handshake_ok = False
        state = {
            "client_ready": False,
            "turn": 1,
            "keep_counter": 1,
            "bundle_sent": False,
            "map_id": 10002,
            "frame": 1,
        }
        last_control_ts = time.time()
        try:
            self._log(f"Session started, waiting for game opcodes...")
            while self._running:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    buf += data

                    while len(buf) >= 4:
                        opcode = struct.unpack_from("<H", buf, 0)[0]
                        plen = struct.unpack_from("<H", buf, 2)[0]
                        total = plen
                        if total < 4:
                            self._log(f"Invalid packet length: {total}, drop session")
                            return
                        if len(buf) < total:
                            break
                        payload = buf[4:total]
                        raw_packet = buf[:total]
                        buf = buf[total:]
                        if opcode == 0x0259:
                            handshake_ok = True
                            state["client_ready"] = False
                        self._handle_opcode(conn, opcode, payload, state, raw_packet)

                except socket.timeout:
                    now = time.time()
                    # V49 baseline: keep sending 0x0133 control frames after login.
                    if handshake_ok and now - last_control_ts >= 0.1:
                        self._keep_counter += 1
                        try:
                            cf = _build_control_frame(2 if state["client_ready"] else 1, state["turn"], state["keep_counter"])
                            conn.sendall(_build_packet(0x0133, cf))
                            last_control_ts = now
                            state["turn"] += 1
                            state["keep_counter"] += 1
                        except Exception:
                            break
                except ConnectionResetError:
                    break
                except Exception as e:
                    self._log(f"Session error: {e}")
                    break
        except Exception as e:
            self._log(f"Session error: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
            with self._client_lock:
                if self._active_conn is conn:
                    self._active_conn = None
            self._log("Game disconnected")

    def _handle_opcode(self, conn: socket.socket, opcode: int, payload: bytes, state: dict, raw_packet: bytes = b""):
        """处理游戏发来的 opcode. 记录所有收到的 opcode."""
        # V49: 记录所有收到的 opcode
        plen = len(payload)
        self._log(f"[RECV] opcode=0x{opcode:04X} len={plen} head={payload[:min(plen,16)].hex()}")

        if opcode == 0x0259:
            # 游戏首次请求 → 回复登录成功 + 玩家/房间/选项信息
            login_payload = _build_login_result(self.player_slot)
            conn.sendall(_build_packet(0x013A, login_payload))
            self._log(f"0x0259 -> sent 0x013A login (0x34 bytes)")
            # Bootstrap loading control.
            conn.sendall(_build_packet(0x0133, _build_control_frame(1, state["turn"], state["keep_counter"])))
            self._log("0x0259 -> sent 0x0133 loading-control")

        elif opcode == 0x0261:
            # load progress ACK: 0x0261 -> 0x0161
            conn.sendall(_build_packet(0x0161, payload))
            if _is_load_complete_progress(payload) and not state["bundle_sent"]:
                self._send_session_bundle(conn, state)
        elif opcode == 0x025F:
            # load-ready ACK: 0x025F -> 0x015F
            conn.sendall(_build_packet(0x015F, payload))
            if not state["bundle_sent"]:
                self._send_session_bundle(conn, state)
        elif opcode == 0x025D:
            # 客户端心跳 token 回显
            conn.sendall(_build_packet(0x015D, _build_ping_echo(payload, state["keep_counter"])))
            conn.sendall(_build_packet(0x0133, _build_control_frame(2 if state["client_ready"] else 1, state["turn"], state["keep_counter"])))
            if state["client_ready"]:
                conn.sendall(_build_packet(0x0138, _build_turn_sync_payload(state["frame"], self.player_slot - 1)))
                state["frame"] += 1
        elif opcode == 0x0263:
            # In-game client command/state packet. ACK the payload and forward
            # the full client packet inside a type=2 turn command list.
            conn.sendall(_build_packet(0x0163, _build_client_command_ack_payload(payload)))
            if raw_packet:
                conn.sendall(_build_packet(0x0138, _build_client_command_turn_payload(state["frame"], raw_packet)))
                state["frame"] += 1
            conn.sendall(_build_packet(0x0133, _build_control_frame(2, state["turn"], state["keep_counter"])))
            state["turn"] += 1
            state["keep_counter"] += 1
        elif opcode == 0x0272:
            # Post-load/game-scene-ready notification. Mirror ACK and keep the
            # client in the current control state.
            conn.sendall(_build_packet(0x0172, payload))
            conn.sendall(_build_packet(0x0133, _build_control_frame(2 if state["client_ready"] else 1, state["turn"], state["keep_counter"])))
            state["turn"] += 1
            state["keep_counter"] += 1
        elif opcode == 0x026A:
            # Session/reconnect check. ACK-only after ready; resending the full
            # player list here can corrupt player counts.
            conn.sendall(_build_packet(0x016A, payload))
            if not state["client_ready"]:
                conn.sendall(_build_packet(0x013A, _build_login_result(self.player_slot)))
            else:
                local_slot = max(0, min(23, int(self.player_slot) - 1))
                conn.sendall(_build_packet(0x0150, _build_player_record(local_slot, self.player_slot, self.player_name)))
                conn.sendall(_build_packet(0x015C, _build_room_info_payload(state["map_id"], self.player_slot)))
            conn.sendall(_build_packet(0x0133, _build_control_frame(2 if state["client_ready"] else 1, state["turn"], state["keep_counter"])))
            state["turn"] += 1
            state["keep_counter"] += 1
        elif opcode == 0x0265:
            # Exit/close notification. Only acknowledge; do not refresh session
            # tables while the client is closing.
            conn.sendall(_build_packet(0x0165, payload))

    @property
    def is_listening(self):
        return self._sock is not None and self._running

    def _log(self, msg: str):
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            path = Path("data/SL10002_host_service.log")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {msg}\n")
            # 同时写 ONE_LOG 预启动
            onelog = Path("data/SL10002_ONE_LOG.txt")
            if not onelog.exists():
                onelog.write_text(f"SL10002 V49 {ts}\n[HS] {msg}\n", encoding="utf-8")
        except Exception:
            pass
