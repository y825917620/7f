# 研究发现 (2026-05-17 更新)

## 启动契约 (来自 SL10002 FinalLauncher 参考 + 测试证实)

| 项 | 值 |
|------|-----|
| 命令行 | `game.exe /mapfile=10002 MemoryMapName=SL10002_LANV45_10002_{pid}` |
| SHM 1 | "10002" + 自定义名, 0x435 bytes PlatformBlock |
| SHM 2 | `7fgame_game_client_start_info` (未使用, 游戏读 MemoryMapName) |
| 互斥体 | `7fxx_dgtm` |
| HostService | TCP 127.0.0.1:29002 |
| 地图文件 | `map/{id}/{id}.map` + `map/{id}/{id}.o` + `map/sanguo/sanguo.o` |
| config.lua | SrvScriptInfo/load_rolesdk return 1 (本地会话) |
| edt2.o | helper_get004={map_id,1,1,control_id} |
| GetMapOptionDisplay | return 1 |
| g_map_display | = 1 |
| bInheritHandles | FALSE |
| 管道/NUL | 无 |

## 终端测试结果 (2026-05-17)
- HostService TCP 29002: CONNECTED ✓
- 游戏 PID 创建成功 ✓
- AfterRun > 5 帧 (有时10帧) ✓
- sanguo.o 加载: 有时成功有时失败 (取决于终端/GUI环境)
- tab_interface nil: 终端环境出现, GUI exe 待验证
