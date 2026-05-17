SL10002 Final Launcher V28A - Original Mechanics Bridge

This build continues the LAN HostService route and changes the ModRuntime policy:
- Prefer the original map hero selection flow.
- Prefer original base spawn and original wave/timer mechanisms.
- Do not force-create heroes/buildings/waves unless fallback_overlay=true is explicitly set in mod_config.lua.
- Trace original AddCha/AddSceneObject/Timer calls to confirm whether the original dynamic chain is releasing.

Run:
1. Extract to the data directory.
2. Double-click start_10002.bat.
3. Choose mode 1 first.
4. Send only SL10002_ONE_LOG.txt next time.

Diagnostics:
- SL10002_original_mechanics_v28a_trace.txt
- SL10002_mod_runtime_v28a.log
- SL10002_0263_v28a_trace.txt
- AddCha.log
