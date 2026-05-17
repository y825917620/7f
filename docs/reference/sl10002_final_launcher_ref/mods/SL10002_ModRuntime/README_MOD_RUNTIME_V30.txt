SL10002 ModRuntime V30

This version fixes the V29 lua_sceAddCha parameter popup.
It no longer brute-force calls lua_sceAddCha/sceAddCha with numeric IDs.
It uses signatures recovered from 10002.o bytecode:
  AddCha(id, x, y, dir, owner)
  AddSceneObj(id, x, y, dir, owner)
If those wrappers are absent, it only uses low-level sce* APIs when tab_cha[id] or tab_sceneobj[id] is an actual table.
