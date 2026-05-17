SL10002 V42A RESOURCE PRELOAD + FRAMEPULSE LOWPORT

Purpose:
- Restore the launcher-side loading-stage map resource preparation that was skipped by V40/V41/V42 FastPath builds.
- Keep ModRuntime disabled. No AddCha overlay, no scene-object generation, no VIP/sponsor modification, no game.exe patching.
- Preload resources before HostService/game.exe launch, then continue protocol clock/delay testing with 29002 low port and sparse FramePulse.

Main changes:
1. Copies prepared 10002.map and 10002.o to data\map\10002 and data\core\map\10002.
2. Runs MountReferencedMapResources() against deployed data\map\10002\10002.o before HostService starts.
3. Writes SL10002_resource_mount_v42a.log with total/mounted/already/missing/skipped_bad_compat.
4. Writes SL10002_scene_resource_check.txt after the preload scan.
5. Keeps UI resource repair from real TGA/DDS only; never writes fake placeholder UI files.
6. Keeps protocol baseline:
   - Port 29002
   - wait for 0x0261 progress=100 / 0x025F ready
   - 0x0272 ACK
   - 0x026A ACK-only
   - exact 0x025D token echo
   - sparse 0x0138 type=1 FramePulse after heartbeat

Use:
- Extract into data directory and overwrite.
- Run start_10002.bat.
- Choose 1.
- Send only SL10002_ONE_LOG.txt.
