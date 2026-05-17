# -*- coding: utf-8 -*-

import socket
import struct
import time

from src.launcher.host_service import HostService, _build_player_record


def _recv_packet(sock: socket.socket):
    header = sock.recv(4)
    if len(header) < 4:
        return None, None
    opcode, total_len = struct.unpack("<HH", header)
    plen = max(0, total_len - 4)
    payload = b""
    while len(payload) < plen:
        chunk = sock.recv(plen - len(payload))
        if not chunk:
            break
        payload += chunk
    return opcode, payload


def _drain_packets(sock: socket.socket, seconds: float = 1.5):
    end = time.time() + seconds
    packets = []
    while time.time() < end:
        try:
            op, payload = _recv_packet(sock)
        except socket.timeout:
            continue
        if op is None:
            break
        packets.append((op, payload))
    return packets


def test_host_service_login_packet_layout():
    port = 29123
    hs = HostService(player_slot=3, player_name="Player3", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(("127.0.0.1", port))

        payload = b"\x00" * 196
        s.sendall(struct.pack("<HH", 0x0259, len(payload) + 4) + payload)

        # 0x013A login
        op, login = _recv_packet(s)
        assert op == 0x013A
        assert len(login) == 0x34
        global_id = struct.unpack_from("<Q", login, 0x00)[0]
        server_time = struct.unpack_from("<I", login, 0x08)[0]
        room_id = struct.unpack_from("<I", login, 0x0C)[0]
        assert global_id >= 100001
        assert server_time > 1000000000
        assert room_id == 1
        s.close()
    finally:
        hs.stop()


def test_host_service_loading_control_uses_zero_turn_until_ready():
    port = 29128
    hs = HostService(player_slot=1, player_name="Player1", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(("127.0.0.1", port))
        s.sendall(struct.pack("<HH", 0x0259, 196) + (b"\x00" * 192))

        _recv_packet(s)  # 0x013A
        op, control = _recv_packet(s)

        assert op == 0x0133
        assert control[0:4] == b"\x01\x00\x00\x00"
        assert control[4] == 30
        assert control[5] == 0
        s.close()
    finally:
        hs.stop()


def test_host_service_sends_keepalive_after_handshake():
    port = 29124
    hs = HostService(player_slot=1, player_name="Player1", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(("127.0.0.1", port))
        payload = b"\x00" * 196
        s.sendall(struct.pack("<HH", 0x0259, len(payload) + 4) + payload)

        # Drain initial response packets (0x013A + bootstrap 0x0133).
        for _ in range(2):
            _recv_packet(s)

        deadline = time.time() + 2.0
        got_keepalive = False
        while time.time() < deadline:
            op, data = _recv_packet(s)
            if op == 0x0133 and len(data) == 12:
                got_keepalive = True
                break
        assert got_keepalive is True
        s.close()
    finally:
        hs.stop()


def test_host_service_echoes_udp_ping_packets():
    port = 29130
    hs = HostService(player_slot=1, player_name="Player1", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2.0)
        payload = b"ping-token"
        s.sendto(payload, ("127.0.0.1", port))
        data, addr = s.recvfrom(1024)

        assert data == payload
        assert addr[0] == "127.0.0.1"
        s.close()
    finally:
        hs.stop()


def test_host_service_waits_for_progress_100_before_postload_bundle():
    port = 29125
    hs = HostService(player_slot=1, player_name="Player1", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(("127.0.0.1", port))
        s.sendall(struct.pack("<HH", 0x0259, 196) + (b"\x00" * 192))
        _drain_packets(s, 0.3)

        # Observed load progress packets are two bytes: progress, marker.
        # 0x1e64 means 30%, so it must only be ACKed and must not start the
        # player/session bundle yet.
        s.sendall(struct.pack("<HH", 0x0261, 6) + b"\x1e\x64")
        packets = _drain_packets(s, 1.2)
        ops = [op for op, _ in packets]
        assert 0x0161 in ops
        assert 0x0130 not in ops
        assert 0x015C not in ops
        assert 0x0138 not in ops

        # 0x6464 means 100%; only then may the game receive player/session
        # tables and the first game-start turn.
        s.sendall(struct.pack("<HH", 0x0261, 6) + b"\x64\x64")
        packets = _drain_packets(s, 1.2)
        ops = [op for op, _ in packets]

        assert 0x0130 in ops
        assert 0x015C in ops
        assert 0x0138 in ops
        assert 0x0150 not in ops

        player_payload = next(payload for op, payload in packets if op == 0x0130)
        assert struct.unpack_from("<I", player_payload, 0)[0] == 1
        assert struct.unpack_from("<H", player_payload, 6)[0] == 0x6F
        s.close()
    finally:
        hs.stop()


def test_player_record_uses_nonzero_regular_player_type():
    record = _build_player_record(0, 1, "Player1")

    assert record[0x69] == 0
    assert record[0x6A] == 1
    assert record[0x6B] == 1
    assert record[0x6C] == 1
    assert record[0x6D] == 1


def test_host_service_acks_reconnect_and_scene_ready_after_start():
    port = 29126
    hs = HostService(player_slot=1, player_name="Player1", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(("127.0.0.1", port))
        s.sendall(struct.pack("<HH", 0x0259, 196) + (b"\x00" * 192))
        _drain_packets(s, 0.3)
        s.sendall(struct.pack("<HH", 0x0261, 6) + b"\x64\x64")
        _drain_packets(s, 0.8)

        reconnect_payload = b"\x18\x00\x00\x00\x01"
        s.sendall(struct.pack("<HH", 0x026A, 4 + len(reconnect_payload)) + reconnect_payload)
        s.sendall(struct.pack("<HH", 0x0272, 4))
        packets = _drain_packets(s, 1.2)
        by_op = {}
        for op, payload in packets:
            by_op.setdefault(op, []).append(payload)

        assert reconnect_payload in by_op.get(0x016A, [])
        assert b"" in by_op.get(0x0172, [])
        assert 0x0150 in by_op
        assert 0x015C in by_op
        assert 0x0133 in by_op
        s.close()
    finally:
        hs.stop()


def test_host_service_sends_turn_sync_on_ready_heartbeat():
    port = 29127
    hs = HostService(player_slot=1, player_name="Player1", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(("127.0.0.1", port))
        s.sendall(struct.pack("<HH", 0x0259, 196) + (b"\x00" * 192))
        _drain_packets(s, 0.3)
        s.sendall(struct.pack("<HH", 0x0261, 6) + b"\x64\x64")
        _drain_packets(s, 0.8)

        token = b"\x01\x02\x03\x04"
        s.sendall(struct.pack("<HH", 0x025D, 8) + token)
        packets = _drain_packets(s, 1.2)
        frame_payloads = [payload for op, payload in packets if op == 0x0138]

        assert frame_payloads
        turn_sync = [payload for payload in frame_payloads if len(payload) == 13 and payload[4] == 2]
        assert turn_sync
        assert turn_sync[0][9] == 0
        s.close()
    finally:
        hs.stop()


def test_host_service_forwards_client_command_packet_as_turn_command():
    port = 29129
    hs = HostService(player_slot=1, player_name="Player1", host_port=port)
    hs.start()
    try:
        assert hs.wait_until_ready(2.0) is True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(("127.0.0.1", port))
        s.sendall(struct.pack("<HH", 0x0259, 196) + (b"\x00" * 192))
        _drain_packets(s, 0.3)
        s.sendall(struct.pack("<HH", 0x0261, 6) + b"\x64\x64")
        _drain_packets(s, 0.8)

        raw_client_packet = struct.pack("<HH", 0x0263, 9) + b"\x10\x20\x30\x40\x50"
        s.sendall(raw_client_packet)
        packets = _drain_packets(s, 1.2)
        by_op = {}
        for op, payload in packets:
            by_op.setdefault(op, []).append(payload)

        assert b"\x10\x20\x30\x40\x50" in by_op.get(0x0163, [])
        turn_payloads = by_op.get(0x0138, [])
        assert turn_payloads
        forwarded = [p for p in turn_payloads if p[4] == 2 and p[7:] == raw_client_packet]
        assert forwarded
        assert struct.unpack_from("<H", forwarded[0], 5)[0] == len(raw_client_packet)
        s.close()
    finally:
        hs.stop()
