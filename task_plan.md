# 基于原版反编译成果的启动器改造计划

## 核心发现

原启动器是 **原生 C++ MFC 程序**，不是 Python。关键差异：

| 项 | 原版 C++ | 我们的 Python |
|------|----------|--------------|
| 命令行 | `game.exe MemoryMapName=sanguo` | `game.exe 10002` |
| SHM 大小 | `7fgame_game_client_login` = **4 bytes** | 256 bytes |
| 地图数据传输 | **MemoryMapName=sanguo** 内存映射 | `sl/map.map` 文件 |
| 管道/NUL | 无 | 有（当前版本可能无） |
| 配置文件 | `login.ini` | `GameSetting.inf` |
| edt2.o | `GetMapOptionDisplay() return 0` | return 1 |
| g_map_display | `= 0` | = 0 ✓ |

## 改造任务

### 1. 命令行添加 MemoryMapName=sanguo [P0]
   原版: `"core\game.exe" MemoryMapName=sanguo`
   修改: `_build_cmdline()` 追加 ` MemoryMapName=sanguo`

### 2. 创建 sanguo 共享内存，写入地图数据 [P0]
   原版: `CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, size, "sanguo")`
   修改: 在 GameBridge.launch() 中创建名为 "sanguo" 的内存映射，
   将 LuaRDGTM 解压数据写入

### 3. 修正 GetMapOptionDisplay 返回 0 [P1]
   原版: `function GetMapOptionDisplay() return 0 end`
   修改: config_generator.py

### 4. 移除 sl/map.map 创建 [P1]  
   原版不创建此文件，游戏从 MemoryMapName=sanguo 读取
   修改: ResourceMountManager

### 5. 修正 SHM 大小 [P2]
   原版: 7fgame_game_client_login = 4 bytes
   修改: GameBridge

### 6. 无管道/NUL [P2]
   原版: dwFlags=0x1, bInheritHandles=FALSE
   修改: 确认 GameBridge.launch()

## 不纳入本轮
- login.ini 配置（后续）
- MFC 窗口/对话框
- 赞助大使UI
