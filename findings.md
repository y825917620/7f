# 研究发现记录

## 地图资源格式

### .map 文件
- 头部样本：`54 e9 0b 00 ...`
- 体积通常小于解包后的运行包
- 推测：地图元数据、展示信息、选项、缩略图

### .sl 文件
- LZMA 压缩格式，压缩头：`5d 00 00 40 00 ...`
- 解压后以 `LuaRDGTM` 开头
- 应作为运行态地图包主来源

### 解压后运行包（LuaRDGTM）
- 统一以 `LuaRDGTM` 标识开头
- `10002_dec.bin` 属于此类内容
- 后续结构待研究：段数量、偏移表、脚本名、资源名

### 候选挂载点
- `sl/map.map`
- `core/sl/map.map`
- 当前两处写入同一份解包内容

## 游戏启动接口

### 命令行参数
- `/mapfile=` — 可能指定地图文件
- `/livemapfile=` — 可能指定直播/编辑器地图
- `/pipe=` — 命名管道
- `/livepipe=` — 直播管道
- `MemoryMapName=` — 内存映射名，默认 `sanguo`

### 地图状态接口（来自 gpigame.dll）
- `SetLoadMap`
- `UpdateMapID`
- `IsMapOK`
- `GetGameCheckSum`
- `GetCheckSumData`

### 日志阶段
- `GameInit`
- `do [core/gpi.o] ok!`
- `读取地图表格`
- `begin load map`
- `map is not ok`

## 当前问题
1. `mid_val = 10002` 硬编码（game_launcher.py）
2. 固定复制 `map/10002_dec.bin`（game_launcher.py）
3. 日志显示 `读取地图[10002]失败` — 资源层未真正接通
4. `build_launcher.py` 引用不存在的 `src.core.sl_handler`

## 已有模块
- `src/core/config_generator.py` — 配置生成
- `src/core/map_catalog.py` — 地图目录（已创建，待完善）
- `src/core/map_package_analyzer.py` — 地图包分析（已创建，待完善）
- `src/core/map_launch_manifest.py` — 启动清单（已创建，待完善）
- `src/core/map_parser.py` — 地图解析
- `src/core/resource_mount_manager.py` — 资源挂载管理（已创建，待完善）
- `src/launcher/game_launcher.py` — 游戏启动（**需要重构**）
- `src/launcher/game_settings.py` — 游戏设置
- `src/launcher/log_verifier.py` — 日志验证（已创建，待完善）
- `src/data/map_data.py` — 地图数据定义
- `src/ui/main_window.py` — 主窗口
- `src/ui/sponsor_widgets.py` — 赞助组件
