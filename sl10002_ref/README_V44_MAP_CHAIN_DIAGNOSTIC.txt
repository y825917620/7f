V44 地图加载链路诊断版

目标：修复 V43 OneLog 仍抓 V42A 旧日志的问题，并在不主动 AddCha、不刷怪、不改 VIP 的情况下，记录原图从 map_init 到 GameEvent/Timer/AddCha 的真实断点。

重点日志：
- SL10002_lan_v44_launcher.log
- SL10002_map_protocol_v44.log
- SL10002_resource_mount_v44.log
- SL10002_scene_resource_check.txt
- AddCha.log
- log_mgr

运行：解压到 data 目录覆盖，运行 start_10002.bat，选 1，跑完只发 SL10002_ONE_LOG.txt。
