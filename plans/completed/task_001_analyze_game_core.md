---
task_id: "task_001"
status: "active"
role: "executor"
priority: "high"
created_by: "planner"
created_at: "2026-05-13T12:00:00Z"
---

# Task: 分析游戏核心文件

## Objective
分析神龙地图启动器配套的游戏核心文件，提取所有关键信息，为独立地图加载工具提供完整的数据支撑。

## Plan
1. 分析 `data/core/gpi.o` — Lua 字节码，提取所有可读的字符串和函数名
2. 分析 `data/core/rolesdk.o` — 角色/账号 SDK，提取字符串
3. 分析 `data/core/tdb.o` — 触发器/数据库文件，提取字符串
4. 分析 `data/GameSetting.inf` — 21 行配置，确定每行的确切含义
   - 第1行已确认 = 分辨率选项索引
   - 其余 20 行需要通过与原启动器行为对比确认
5. 分析 `data/core/gpigame.dll` — 搜索更多导出函数和关键字符串
   - VIP/Player/Map 相关函数
   - 启动时加载的文件路径
   - 账号系统相关字符串

## Acceptance Criteria
- [ ] 输出 `gpi_strings.txt` — gpi.o 中所有可提取的字符串
- [ ] 输出 `rolesdk_strings.txt` — rolesdk.o 中所有可提取的字符串
- [ ] 输出 `tdb_strings.txt` — tdb.o 中所有可提取的字符串
- [ ] 输出 `gamesetting_analysis.json` — GameSetting.inf 每行含义的推测和验证
- [ ] 输出 `gpigame_analysis.json` — gpigame.dll 中关键函数和字符串的分类列表

## Context
- 游戏根目录: `E:\玩家原创\神龙地图启动器5.2\data\`
- core 目录: `E:\玩家原创\神龙地图启动器5.2\data\core\`
- 已知 gpi.o 包含 `GameSetting`、`PlayGif`、`SetGame_AttrRange` 等字符串
- 已知 GameSetting.inf 当前内容: `5,0,1,1,42,0,43,10,3,0,0,0,0,0,0,0,0,0,0,0,1`

## Notes
- 使用 Python 脚本读取二进制文件并提取可打印字符串
- gpi.o、rolesdk.o、tdb.o 都是 Lua 字节码或二进制文件
- 不需要反编译 Lua 字节码，只需要提取字符串
