SL10002 V33 POST-MAPINIT MOD RUNTIME

修正 V31 的时机判断：V31 一直等待 GameEvent_MapInit，但日志显示原图只暴露/触发 map_init，map_init 返回后 tab_cha/tab_sceneobj 已经是 table。V33 将 map_init 返回作为完整地图初始化边界，随后才允许 ModRuntime 执行。

要点：
- config.lua / edt2.o 阶段只安装 hook。
- map_init 返回后再执行 overlay。
- GameEvent_MapInit 不再作为强制条件。
- 仍不修改 VIP/赞助/认证字段。
- 不直接 numeric 调用 sceAddCha；只通过 tab_cha row + sceAddCha 包装或原 AddCha 包装。

运行后只发 SL10002_ONE_LOG.txt。
