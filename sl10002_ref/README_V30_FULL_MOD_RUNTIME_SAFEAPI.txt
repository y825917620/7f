V30 FULL MOD RUNTIME SAFE API

Fixes V29 popup: lua_sceAddCha parameter error.
Root cause: V29 called sceAddCha with numeric ID directly. Original 10002.o uses AddCha(id,x,y,dir,owner) wrapper; low-level sceAddCha expects a table row, not a raw numeric ID.

V30 changes:
- No brute-force engine calls.
- No direct numeric sceAddCha calls.
- Uses AddCha/AddSceneObj original signatures from bytecode when available.
- If wrappers are absent, creates compatible wrappers only when tab_cha/tab_sceneobj rows exist.
- Keeps LAN HostService timing/heartbeat/0x0263 trace.
- Does not modify VIP/sponsor/auth fields.
