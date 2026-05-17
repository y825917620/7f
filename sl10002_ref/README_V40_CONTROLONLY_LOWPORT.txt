SL10002 V40 CONTROLONLY LOWPORT CLOCK/DELAY

Changes from V39:
1. HostService port changed from 39002 to 29002 to avoid the game showing a sign-extended port such as 127.0.0.1:4294940762.
2. Default protocol variant changed to ControlOnly. Continuous fake 0x0138 type=2 noop turnstream is disabled by default because V39 still ended at logic frame 5.
3. 0x0272 is now traced and ACKed with 0x0172.
4. 0x026A after load-ready is ACK-only plus light start=2 control; it no longer resends full player/session tables.
5. 0x0265 exitguard table refresh is disabled; the launcher only ACKs 0x0165 and records it.
6. ModRuntime remains disabled. This build tests base game clock/delay/session recognition only.

Run start_10002.bat, choose mode 1, then send SL10002_ONE_LOG.txt only.
