SL10002 ModRuntime V33

Delayed in-game runtime. config.lua/edt2.o only installs hooks. Overlay AddCha/AddSceneObj starts only after original map_init/GameEvent_MapInit has completed. No numeric direct sceAddCha call.
