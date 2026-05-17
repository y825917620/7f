SL10002 V43 RESOURCE PRELOAD + CONTROLONLY SAFE

- Restores full 10002.o referenced-resource preload before game.exe.
- Creates a real UI compatibility alias if ValuableItemShop.tga is missing, using ValuableShop.tga.
- Uses low port 29002.
- Defaults to ControlOnly: no sparse FramePulse after ready, to avoid V42A frame:1 crash.
- ModRuntime/AddCha overlay remains disabled.
- Keeps 0x0261/0x025F post-load gating, 0x0272 ACK, 0x026A ACK-only, and 0x025D exact token echo.
