# gpigame.dll + map.o + log_mgr 地图逻辑 / VIP赞助线索分析报告

## 0. 结论先行

这次上传的三个文件把前面的判断补全了：

1. `gpigame.dll` **确实是地图脚本/逻辑核心层**，里面有 `LuaServer`、`LoadLuaTable`、`DecryptMap`、`PackMapToDotO`、`TBL_GetTableTriggerInfo`、`AddCha`、`AddSceneObject` 等接口。
2. `map(1).o` 不是 C/C++ 的 `.o`，而是 **Lua 5.1 字节码文件**。它目前只恢复出 `g_map_display` 和 `g_map_opt` 两个全局表，像是地图选项/显示状态缓存，不是完整 NPC/建筑/刷怪脚本。
3. `log_mgr` 是一次运行错误日志，确认加载的地图是 `10002`，脚本版本 `25`，地图版本 `1`，错误点是缺少或读取失败 `resource/sanguo/ui/loading_misc.dds`。
4. `gpigame.dll` 没有发现明确明文 `VIP / 赞助 / 赞助大使 / 会员 / 充值`。但它提供了 Lua 可访问的 `GetSessionPlayerInfoEx`，并暴露 `player_type_reg / player_type_ini / player_type_db` 三个字段。这三个字段和前面 `game.exe` 里发现的 `UserAdvType_Reg / UserAdvType_Ini / UserAdvType_Db` 高度对应，最像“玩家身份/权限/赞助类型”的本地候选字段。
5. NPC、建筑、出兵、怪物刷新逻辑大概率不是在 `map(1).o` 这个小文件里，而是在 `.sl` payload 解密/解包后得到的更多 Lua 表或脚本中，例如 `tab_cha / tab_sceneobj / tab_UserTrigger / tab_UserAction / tab_UserEvent / tab_condition`。

> 安全边界：本报告只做静态结构分析和证据定位，不提供绕过 VIP/赞助、修改权限、制作外挂、注入游戏或破坏联机公平性的操作步骤。

## 1. 文件指纹

- `gpigame.dll`: `aeac3ed3d7e1a78b1bc268c538026319b5f9e48c72b8d2cbe5f0a6e5993d030c` (3,846,144 bytes)
- `map(1).o`: `6ae20443dde8b557a9b8c18345a036c78a15f8d90f67903682c1843204b4bcff` (2,539 bytes)
- `log_mgr`: `6f73b9625e5824e2e05c6c71a40eb192a38f712b597a8f7051d811bdc9a9ff76` (1,400 bytes)
- `10002.sl`: `b948eb1aed07bca15af1b90ae54148ea785cdf740d80b66193447b29e37e4f33` (5,079,124 bytes)
- `10002.map.bin`: `1a7cfdd3a1235fd097b6268a5c5a9f17596c66200b3485346aac16592acacbcf` (930,401 bytes)
- `game.exe`: `1f76b4043f9ed1c5a1906a25378394961c2bc1df845ea34196e1c06d10475135` (847,872 bytes)

## 2. gpigame.dll 的定位

`gpigame.dll` 是 PE32 DLL，导出了大量 C++ 符号和 C 风格接口。关键点是：它不是单纯渲染库，而是包含 LuaServer、地图加载、表读取、地图打包/解包、角色与场景物件创建的核心模块。

### 2.1 关键导出函数

| Ordinal | RVA | Name |
|---:|---:|---|
| 403 | `0x070370` | `?LoadMap@CGameScene@@QAEHPBDHHH@Z` |
| 260 | `0x0cc7f0` | `?GetMapEncryptInfo@LuaServer@@QAEHPBDPAH@Z` |
| 151 | `0x0d0460` | `?DoFile@LuaServer@@QAEHPBD@Z` |
| 152 | `0x0d0550` | `?DoString@LuaServer@@QAEHPBD@Z` |
| 150 | `0x0d0640` | `?DoBuffer@LuaServer@@QAEHPBDI0@Z` |
| 431 | `0x0d1730` | `?PackMapToDotO@LuaServer@@QAEHPBDPAPAD@Z` |
| 583 | `0x0d41a0` | `?TBL_GetTableTriggerInfo@LuaServer@@QAEXPBD00PAPAD11@Z` |
| 402 | `0x0d7c50` | `?LoadLuaTable@LuaServer@@QAEHPBD00HP6GX00@Z@Z` |
| 429 | `0x0de520` | `?PackMapFromMemory@LuaServer@@QAEHH@Z` |
| 430 | `0x0de790` | `?PackMapFromMemoryOpt@LuaServer@@QAEHXZ` |
| 190 | `0x0ded10` | `?EncryptMap@LuaServer@@QAEHPBD@Z` |
| 141 | `0x0def50` | `?DecryptMap@LuaServer@@QAEHPBDPADPAI@Z` |
| 432 | `0x0df0f0` | `?PackMapWithEncrypt@LuaServer@@QAEHPBDPAPADH@Z` |
| 1293 | `0x10b5c0` | `RunGameLogic` |
| 1416 | `0x10b6d0` | `SetLoadMap` |
| 1211 | `0x10b710` | `LoadMap` |
| 766 | `0x10b730` | `CreateMap` |
| 724 | `0x10baa0` | `AddSceneObject` |
| 1207 | `0x10cb70` | `LoadCharacter` |
| 779 | `0x10cc20` | `DelCharacter` |
| 1521 | `0x10da60` | `UnitMoveTo` |
| 823 | `0x10dd80` | `DoStringI` |
| 821 | `0x10dd90` | `DoFile` |
| 822 | `0x10ddb0` | `DoString` |
| 1506 | `0x10e010` | `TBL_GetTableTriggerInfo` |
| 1238 | `0x10e120` | `PackMapToDotO` |
| 1236 | `0x10e160` | `PackMapFromMemory` |
| 1237 | `0x10e180` | `PackMapFromMemoryOpt` |
| 1210 | `0x10e1f0` | `LoadLuaTable` |
| 1114 | `0x10f8b0` | `GetSessionInfo` |
| 1429 | `0x10f8c0` | `SetPlayerInfo` |
| 721 | `0x10f8d0` | `AddPlayer` |
| 1426 | `0x10f8e0` | `SetOptionInfo` |
| 720 | `0x10f8f0` | `AddOption` |
| 1115 | `0x10f9b0` | `GetSessionJoinInfo` |
| 859 | `0x115980` | `GameInit` |

## 3. 地图加载链路复原

从 `gpigame.dll` 字符串和反汇编可恢复出如下链路：

```text
启动器 / game.exe
  ↓
gpigame.dll!SetLoadMap(map_path)
  ↓
gpigame.dll!LoadMap / CGameScene::LoadMap
  ↓
LuaServer / 地图脚本系统
  ↓
优先加载 map/%s/%s.o
或加载 map/%s/%s_init.lua、map/%s/%s_run.lua
  ↓
执行 map_init
  ↓
读取物件和角色信息
  ↓
执行 tab_cha / tab_sceneobj / tab_UserTrigger / tab_UserAction / tab_UserEvent 等表驱动逻辑
```

在 DLL 中直接找到的路径模板：

```text
map/%s/%s.o
map/%s/%s_run.lua
map/%s/%s_init.lua
```

也找到日志字符串，GBK 解码后含义是：

```text
开始执行地图脚本，读取物件和角色信息！
成功执行 map_init
```

对应反汇编片段已放在：

```text
BeforeRunGameLogic_map_script_loader_1001AFC5.asm
GameInit_10115980.asm
SetLoadMap_export_1010B6D0.asm
LoadMap_export_1010B710.asm
```

## 4. .sl payload 的解码线索

`gpigame.dll` 里明确存在：

```text
LuaServer::DecryptMap
LuaServer::EncryptMap
LuaServer::GetMapEncryptInfo
LuaServer::PackMapToDotO
LuaServer::PackMapWithEncrypt
DEFAULT_KEY
```

静态反汇编显示，`DecryptMap / EncryptMap` 会打开文件，然后调用一个带 `DEFAULT_KEY` 的块加密/解密流程。核心算法特征包括：

- 8 字节分组；
- 有 4 组 S-box 和 P-array 结构；
- 轮函数形态类似 Blowfish；
- `DEFAULT_KEY` 被作为默认 key 字符串传入；
- `map.o` 文件头为 `LuaQ`，即 Lua 5.1 字节码。

这说明 `.sl` 后半段 payload 很可能不是“无意义高熵数据”，而是经过自定义封装/加密/打包后的 Lua 地图数据。现在已经定位到 DLL 中的解密/打包入口，但尚未把 21MB payload 完整还原成业务 Lua 表。

相关反汇编片段：

```text
LuaServer_DecryptMap_100DEF50.asm
LuaServer_EncryptMap_100DED10.asm
LuaServer_GetMapEncryptInfo_100CC7F0.asm
Blowfish_like_decrypt_core_10120D30.asm
Blowfish_like_encrypt_core_10120B30.asm
```

## 5. map(1).o 解析结果

`map(1).o` 文件类型：**Lua bytecode, version 5.1**。

它不是 C/C++ 目标文件，而是 Lua 字节码。已完整反汇编并重建为 Lua 表：

```lua
-- 详见 map_o_reconstructed.lua
g_map_display = 1
 g_map_opt = {...}
```

### 5.1 重建后的 g_map_opt 表

| Key | 11 个数值 |
|---:|---|
| 1 | `0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0` |
| 2 | `1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 3 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 4 | `0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 5 | `0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 6 | `0, 0, 0, 0, 0, 0, 0, 1, -1, -1, 0` |
| 8 | `0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 10 | `0, 0, 0, 0, 1, 0, -1, -1, -1, -1, 0` |
| 13 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 14 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 15 | `0, 0, 0, 0, 0, -1, -1, -1, -1, -1, 0` |
| 16 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 18 | `0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0` |
| 24 | `0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 26 | `0, 0, 0, 0, 0, -1, -1, -1, -1, -1, 0` |
| 27 | `0, 0, 0, 0, 0, -1, -1, -1, -1, -1, 0` |
| 28 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 33 | `0, 0, 0, 0, 0, 0, 0, -1, -1, -1, 0` |
| 40 | `0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0` |
| 41 | `0, 2, 0, 0, 0, 0, 0, 0, 0, -1, 0` |
| 44 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 45 | `-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 48 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 55 | `0, 0, 0, 1, -1, -1, -1, -1, -1, -1, 0` |
| 61 | `0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 67 | `0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0` |
| 70 | `0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0` |
| 73 | `-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 76 | `0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0` |
| 77 | `0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0` |
| 85 | `0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0` |
| 87 | `0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 90 | `0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0` |
| 91 | `0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0` |
| 106 | `0, 0, 0, 0, 0, 0, -1, -1, -1, -1, 0` |

这个文件没有出现：

```text
赞助
赞助大使
VIP
会员
充值
特权
权限
礼包
隐藏英雄
怪物刷新
出兵波次
NPC 名称
建筑名称
```

所以它更像是地图选项状态表，而不是完整地图逻辑表。

完整输出文件：

```text
map_o_reconstructed.lua
map_o_lua51_disassembly.txt
map_o_g_map_opt.tsv
```

## 6. 地图 NPC / 建筑 / 出兵 / 怪物刷新应从哪里找

`gpigame.dll` 已经明确注册/引用以下 Lua 表名：

| Offset | Table name |
|---:|---|
| `0x2e0228` | `template_tab_for_load` |
| `0x2e0240` | `template_tab_for_load = template_tab.` |
| `0x2e0278` | `tab_UserAction` |
| `0x2e0288` | `tab_condition` |
| `0x2e029c` | `tab_UserEvent` |
| `0x2e0324` | `template_tab_` |
| `0x2e03ec` | `tab_icon` |
| `0x2e03f8` | `tab_model` |
| `0x2e041c` | `tab_UserCatalog` |
| `0x2e042c` | `tab_UserTrigger` |
| `0x2e043c` | `tab_penpics` |
| `0x2e0448` | `tab_tget` |
| `0x2e0454` | `tab_ansList` |
| `0x2e0460` | `tab_skillunit_do` |
| `0x2e0474` | `tab_skillunit_cdt` |
| `0x2e0488` | `tab_skillunit` |
| `0x2e0498` | `tab_mission` |
| `0x2e04a4` | `tab_MapAttr` |
| `0x2e04b0` | `tab_GlobalMapInfo` |
| `0x2e04c4` | `tab_cliff` |
| `0x2e04d0` | `tab_interface` |
| `0x2e04e0` | `tab_upgrade` |
| `0x2e04ec` | `tab_effect` |
| `0x2e04f8` | `tab_sound` |
| `0x2e0504` | `tab_item` |
| `0x2e0510` | `tab_skilleff` |
| `0x2e0520` | `tab_skill` |
| `0x2e052c` | `tab_shadow` |
| `0x2e0538` | `tab_sceneobj` |
| `0x2e0548` | `tab_terrain` |
| `0x2e0554` | `tab_cha` |

这些表名的含义很关键：

- `tab_cha`：角色/单位/NPC 基础表候选；
- `tab_sceneobj`：场景物件/建筑/装饰/可交互物候选；
- `tab_UserTrigger`：用户触发器；
- `tab_UserAction`：触发器动作；
- `tab_UserEvent`：触发器事件；
- `tab_condition`：触发条件；
- `tab_MapAttr` / `tab_GlobalMapInfo`：地图属性/全局地图信息；
- `tab_skill / tab_skillunit / tab_skilleff`：技能和技能效果；
- `tab_item / tab_upgrade / tab_effect / tab_sound`：道具、升级、特效、声音。

所以“出兵逻辑 / 怪物刷新逻辑”最可能不是用 `monster/spawn/wave` 这种英文直写，而是以表驱动方式藏在：

```text
tab_UserTrigger
 tab_UserEvent
 tab_UserAction
 tab_condition
 tab_cha
 tab_sceneobj
```

## 7. Lua API 侧证：地图脚本能创建 NPC/单位/建筑

DLL 里存在大量 Lua 绑定字符串，说明地图脚本可以调用引擎 API 创建和控制对象。

### 角色/NPC/单位创建与控制
- `lua_sceAddCha`
- `lua_AddCha_New`
- `lua_AddCha_NewEx`
- `lua_AddCha_NewEx_Use_ContrlID`
- `AddCha`
- `lua_chaSetName`
- `lua_chaGetName`
- `lua_chaSetPlayerID`
- `lua_chaGetPlayerID`
- `lua_chaSetMoveSpeed`
- `lua_chaDie`
- `lua_chaSay`
- `lua_Cha_LoadSkeleton`
- `lua_Cha_LoadAnimation`
- `UnitMoveTo`
### 场景物件/建筑相关
- `AddSceneObject`
- `DelSceneObj`
- `GetSceneObjNumInArea`
- `GetSceneObjNumOnAPoint`
- `SetSceneObjectVisible`
- `GetCurrentSceneObjNum`
- `CanPlaceSceneObject`
### 触发器/表读取
- `TBL_GetTableTriggerInfo`
- `tab_UserTrigger`
- `tab_UserAction`
- `tab_UserEvent`
- `tab_condition`
- `ReadTable`
- `ReadTableEx`
- `ReadTableExtend`
- `LoadLuaTable`
### 玩家/权限候选
- `GetSessionPlayerInfo`
- `GetSessionPlayerInfoEx`
- `player_type_reg`
- `player_type_ini`
- `player_type_db`
- `GetHostPlayerID`
- `GetPlayerID`
- `SetPlayerInfo`
- `LivePlayerInfo`
### 计时器/刷怪逻辑常用入口
- `lua_AddTimer`
- `lua_EnableTimer`
- `lua_EnableAllTimer`
- `game_event_create_character_when_reload_game`
- `GameEvent_MapInit`
- `map_init`

完整 Lua API 字符串列表已输出到：

```text
gpigame_lua_api_strings.tsv
```

## 8. VIP / 赞助线索

### 8.1 没有直接明文

在 `gpigame.dll`、`map(1).o`、`log_mgr` 中，没有发现可靠的明文：

```text
VIP
vip
赞助
赞助大使
会员
充值
特权
```

前面确认过，“赞助大使”明确存在于启动器 UI 资源里，而不是这三个文件的明文区。

### 8.2 最值得追的权限字段

`gpigame.dll` 里有 Lua 侧字段：

```text
player_type_reg
player_type_ini
player_type_db
```

这些字段出现在 `lua_GetSessionPlayerInfoEx` 附近。结合前面 `game.exe` 中的平台共享内存字段：

```text
UserAdvType_Reg
UserAdvType_Ini
UserAdvType_Db
PlatLev
CanExchangeProp
```

可以得到较强推断：

```text
启动器/game.exe 从平台侧拿到玩家扩展身份字段
  ↓
传给 gpigame.dll / Lua 环境
  ↓
地图脚本可以通过 GetSessionPlayerInfoEx 读取 player_type_reg/player_type_ini/player_type_db
  ↓
地图脚本可能据此控制某些显示、权限、称号或福利
```

但目前不能把它直接等同为“VIP/赞助”，因为没有发现脚本里使用这些字段的解密后逻辑。

相关反汇编片段：

```text
Lua_binding_GetSessionPlayerInfoEx_around_1008B600.asm
```

## 9. log_mgr 解析

`log_mgr` 是一次运行日志/上报结构，关键内容：

| Offset | String |
|---:|---|
| `0x20` | `LGIFø` |
| `0x2c` | `log36564-2026.05.15-23.16.14` |
| `0x12f` | `j98050208` |
| `0x178` | `127.0.0.1:0` |
| `0x19c` | `[frame: 5094]MPTexSet::_getImageInfoFromFile, D3DXGetImageInfoFromFile error: resource/sanguo/ui/loading_misc.dds, hr=-2005529767` |
| `0x3bc` | `10002` |
| `0x420` | `STIFP` |
| `0x428` | `ver="1";playername="";bugtype="error文件";pltver="";execver="98050208";scriptver="25";mapver="1";mapname="10002";sessionid="0";hostaddr="127.0.0.1:0";errinfo="[frame: 5094]MPTexSet::_getImageInfoFromFile, D3DXGetImageInfoFromFile error: resource/sanguo/ui/loading_misc.dds, hr=-2005529767` |
| `0x54a` | `";roomid="0";playerforce="";time="1778858174"` |

重点字段：

```text
execver="98050208"
scriptver="25"
mapver="1"
mapname="10002"
hostaddr="127.0.0.1:0"
errinfo="MPTexSet::_getImageInfoFromFile, D3DXGetImageInfoFromFile error: resource/sanguo/ui/loading_misc.dds"
```

它不包含 NPC/建筑/刷怪/VIP 逻辑，只能证明运行时已经进入地图加载流程，并卡在或记录了资源贴图读取错误。

## 10. 当前证据链修正版

| 文件 | 现在判断 |
|---|---|
| 启动器 EXE | 有 `赞助大使` 按钮和网页入口 |
| game.exe | 读取平台共享内存，存在 `UserAdvType_* / PlatLev / CanExchangeProp` 等候选字段 |
| gpigame.dll | 真正地图逻辑引擎，负责 Lua 表读取、地图脚本执行、角色/场景物件创建、地图加密/解密 |
| 10002.map.bin | 地形/预览/房间选项文本层 |
| 10002.sl | 包含 map.bin + 高熵 payload，payload 应是加密/打包地图逻辑数据 |
| map(1).o | Lua 5.1 字节码，只恢复出 `g_map_display / g_map_opt`，像地图选项缓存 |
| log_mgr | 运行日志，确认地图 10002、脚本版本 25、资源错误 |

## 11. 下一步要真正还原 NPC/出兵/怪物刷新，需要做什么

要把 NPC、建筑、出兵波次、怪物刷新完整还原出来，下一步不是继续关键词搜索，而是：

1. 复现 `LuaServer::DecryptMap / PackMapToDotO` 的解密/解包流程；
2. 从 `.sl` 的 payload 中解出更多 `.o` / `.lua` / Lua table；
3. 重点查 `tab_UserTrigger / tab_UserAction / tab_UserEvent / tab_condition / tab_cha / tab_sceneobj`；
4. 在解出的 Lua 表里追 `GetSessionPlayerInfoEx`、`player_type_db/ini/reg` 是否参与判断。

目前已经定位到足够明确的程序入口，但还没有完成 payload 的完整业务级反序列化。
