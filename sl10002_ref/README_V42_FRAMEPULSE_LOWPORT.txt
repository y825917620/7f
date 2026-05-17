SL10002 V42 - Sparse FramePulse LowPort baseline

Purpose:
- Keep V41's correct pieces: low port 29002, strict post-load 0x0261/0x025F gate, 0x0272 ACK, 0x026A ACK-only, exact 0x025D token echo.
- Fix V41's remaining gap: ControlOnly kept the socket alive but did not drive visible game clock/map logic. V42 sends a sparse 0x0138 type=1 frame pulse after heartbeat instead of continuous 0x0138 type=2 TurnStream.
- ModRuntime/AddCha/AddSceneObj remain disabled. No VIP/sponsor changes.

How to test:
1. Extract this zip into the data directory and overwrite.
2. Run start_10002.bat.
3. Choose 1.
4. After game exits, send only SL10002_ONE_LOG.txt.

Expected diagnostics:
- SL10002_lan_v42_launcher.log
- SL10002_loadready_v42_trace.txt
- SL10002_026A_v42_trace.txt
- SL10002_0272_v42_trace.txt
- log_mgr if the game generates one

Key V42 markers:
- v42_sparse_framepulse_0138_frame
- no cmd012e_turn_stream_0138_type2_frame unless ProtocolVariant=TurnStream is manually selected
