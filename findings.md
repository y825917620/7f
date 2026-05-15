# 研究发现记录

## 地图资源格式

### .sl 文件结构
- LZMA 压缩，属性头固定：`5d 00 00 40 00` (pb=5, lp=0, lc=3, dict_size=64MB)
- 字节 5-12: 解压后大小 (uint64 LE)
- 字节 13+: LZMA 压缩流
- 所有抽样地图均使用相同 LZMA 参数，算法通用

### LuaRDGTM 运行包格式
- 头部 8 字节: ASCII 标识 `LuaRDGTM`
- 字节 8-11: `.map` 文件大小 (uint32 LE) — 与对应 .map 文件大小精确匹配
- 字节 20-23: 段数量 = 128
- 字节 36+: 偏移表 (128 个 uint32，每个指向一个 1088 字节的段)
- 偏移表后: 128 个 1088 字节的地图元数据段
- 段之后: 主地图数据区 (约 21MB for 10002)
- 不包含 `.lua` 文本脚本，不包含 `sanguo` 字符串引用

### 游戏加载机制 (已证实)
1. game.exe 通过命令行接收地图 ID: `game.exe 10002`
2. game.exe 内部从 `map/{id}.sl` 读取并解压 LuaRDGTM 包
3. game.exe 从解压包中提取地图数据并创建 `map/sanguo/sanguo.o`
4. 游戏日志显示: `do [map/sanguo/sanguo.o] ok!`
5. **启动器不需要创建 `sl/map.map` 或预解压 .sl** — 游戏引擎自行处理

## 游戏启动接口

### 命令行
- 格式: `"{game_dir}\core\game.exe" {map_id}`
- 只传地图 ID，不加额外参数
- 工作目录: `{game_dir}` (data/)

### 共享内存
- `7fgame_game_client_start_info` (512 bytes): offset 0 = map_id (uint32)
- `7fgame_game_client_login` (256 bytes): "localplayer" 字符串

### 互斥体
- `7fxx_dgtm` — 防止多开

### 管道
- 匿名管道，Read 端 = hStdInput
- 写入 16 字节: `struct.pack("<4I", PID, TID, map_id, 0)`
- hStdOutput/hStdError = NUL 设备句柄

### 关键配置
- `GameSetting.inf` 第1行必须为 `1` (不是 `5`)
- `config.lua` 包含 `tempConfigLuaMapOptionInfo` 和 `SetCurrentControlID(1)`
- `edt2.o` 包含 helper_get004/005 等辅助函数

## 已验证结论

1. ✅ `.sl` 文件 LZMA 解压 — 全地图通用算法
2. ✅ LuaRDGTM 头结构 — 128 段元数据 + 主地图数据
3. ✅ 游戏自行加载 .sl — 不需要启动器做文件挂载
4. ✅ `sl/map.map` 文件挂载策略是**错误**的 — 反而干扰游戏
5. ✅ `MemoryMapName=sanguo` 不是默认加载路径
6. ✅ 启动器只需: SHM(mode_id) + 管道(PID/TID/map_id) + NUL重定向
7. ✅ `tab_interface nil` 仅发生在终端启动 — GUI 启动正常
