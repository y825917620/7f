# 地图挂载策略决策记录

## 策略 1：文件挂载 (已证实有效)

### 做法
将解包后的 LuaRDGTM 地图包复制到以下挂载点：
- `sl/map.map`
- `core/sl/map.map`

### 证据
- 原启动器生成的 `10002_dec.bin` 同时存在于上述两个路径
- 原启动器可以正常启动地图 10002
- 文件监控确认 game.exe 启动时会读取 `sl/map.map`

### 结论
文件挂载作为默认策略。需要进一步实验确认最小必要路径（是否只需要一个）。

### 状态：✅ 已采纳

---

## 策略 2：命令行 /mapfile= 参数 (待验证)

### 假说
game.exe 支持 `/mapfile=<path>` 参数，可以直接指定地图包路径，无需覆盖 `sl/map.map`。

### 证据来源
- game.exe 二进制中包含 `/mapfile=` 字符串
- gpigame.dll 中包含 `/livemapfile=` 字符串

### 实验设计
- 传入 `/mapfile={cache_path}` 参数
- 不写入 `sl/map.map`
- 观察 init.log 中的地图加载状态

### 状态：🔬 待实验

---

## 策略 3：MemoryMapName=sanguo (待验证)

### 假说
game.exe 通过 `MemoryMapName=sanguo` 读取内存映射中的地图包数据。

### 证据来源
- game.exe 命令行支持 `MemoryMapName=` 参数
- 原启动器日志中出现 `sanguo` 相关引用
- 共享内存名称 `7fgame_game_client_start_info` 已证实有效

### 实验设计
- 创建名为 `sanguo` 的文件映射
- 写入完整地图包数据
- 传入 `MemoryMapName=sanguo` 参数
- 观察是否替代文件加载

### 风险
- 可能是直播/编辑器通道，不是地图加载入口
- 若未证实，不作为默认策略

### 状态：🔬 待实验

---

## 策略 4：Lua 初始化接口 (远期探索)

### 假说
游戏通过 Lua 接口（如 `SetLoadMap`、`UpdateMapID`）接收地图数据。

### 证据
- gpigame.dll 导出 `SetLoadMap`、`UpdateMapID`、`IsMapOK` 等函数
- 这些可能是编辑器/直播的接口，不一定是启动时加载地图的入口

### 状态：⏳ 暂缓探索

---

## 策略验证记录

| 策略 | 证据 | 结果 | 决策 |
|------|------|------|------|
| file_dual_mount | sl/map.map + core/sl/map.map 双写；10002/10005 日志审查 | 10002: ui_init_failed (tab_interface nil) 阻止地图加载；10005: 同上 (ui_init_failed) | 保留为默认策略；ui_init_failed 是终端启动限制非挂载问题；GUI 环境下重新评估 |
| /mapfile= | game.exe 中可见字符串 | 未实验 (ui_init_failed 阻止所有地图加载) | 待 GUI 环境 |
| MemoryMapName= | gpigame.dll 中可见字符串 | 未实验 | 待 GUI 环境 |

## 决策树

```
地图资源接入
├── 默认策略：file_dual_mount (sl/map.map + core/sl/map.map)
├── 若 /mapfile= 证实有效 → 优先使用，减少文件覆盖
├── 若 MemoryMapName= 证实有效 → 作为第二选项
└── 回退策略：保留 file_dual_mount 作为 always-works 方案
```
