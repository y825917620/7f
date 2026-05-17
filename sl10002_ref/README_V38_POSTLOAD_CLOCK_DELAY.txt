SL10002 V39 POSTLOAD CLOCK/DELAY BASELINE

Purpose:
- Fix V37 timing mistake: V37 sent start=2/session/game_start before the client reported map-load complete.
- V39 waits for the real client load-ready packets:
  0x0261 progress100 and/or 0x025F ready.
- After load-ready, V39 sends:
  player/session bundle, room info, option info, start=2 control, first 0x0138 game_start, then continuous 0x0138 turn stream.
- V39 explicitly ACKs:
  client 0x0261 -> server 0x0161
  client 0x025F -> server 0x015F
  client 0x025D -> server 0x015D exact token echo
- V39 clears stale log_mgr before launch so the next ONE_LOG shows only current-run errors.
- V39 repairs invalid loading_misc/mission_misc/main_misc DDS from their real companion TGA when needed.
- ModRuntime remains disabled. No AddCha overlay, no VIP/sponsor/auth bypass, no game.exe patch.

Use:
1. Extract/overwrite into data directory.
2. Run start_10002.bat.
3. Choose 1.
4. After exit, send only SL10002_ONE_LOG.txt.
