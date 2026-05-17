SL10002 ModRuntime V28A - Original Mechanics Bridge

Purpose:
- Keep the original map's hero selection, city/unit click flow, base spawn and wave/timer logic as the preferred path.
- Do not force-spawn heroes or monsters by default.
- Trace whether original map logic calls AddCha / AddSceneObject / lua_AddTimer.

Important:
- This does not remove authentication.
- This does not modify VIP/sponsor fields.
- This does not patch game.exe.
- fallback_overlay is false by default. Enable only for API-signature diagnostics.

Files to check after running:
- SL10002_mod_runtime_v28a.log
- SL10002_original_mechanics_v28a_trace.txt
- SL10002_0263_v28a_trace.txt
- AddCha.log
- SL10002_ONE_LOG.txt
