---
task_id: "task_002"
status: "active"
role: "executor"
priority: "high"
created_by: "planner"
created_at: "2026-05-13T12:00:00Z"
---

# Task: 开发独立命令行地图加载工具

## Objective
开发一个完全不依赖 GUI 的命令行地图加载工具 `map_loader.py`，可直接通过命令行参数启动指定地图，生成正确的配置文件并调用 `game.exe`。

## Plan
1. 设计 CLI 接口：
   ```
   map_loader.py --map 10001 [--option 0,1,2,0,-1,...] [--resolution 1] [--game-dir path]
   ```
2. 复用现有解析逻辑：
   - `map_parser.py` 的 `MapOptionParser.parse()` 解析 .map 文件
   - `config_generator.py` 生成 `config.lua` / `core/edt2.o`
3. 复用启动逻辑：
   - 创建互斥锁 `7fxx_dgtm`
   - 创建管道 + CreateProcessA 启动 `core/game.exe`
   - 写入 16 字节管道数据
   - 生成 `GameSetting.inf` 和 `vip_config.txt`
4. 添加完整的错误处理和日志输出
5. 支持 `--dry-run` 模式（只生成配置文件，不启动游戏）

## Acceptance Criteria
- [ ] `map_loader.py` 可以独立运行，无需 PyQt6
- [ ] 支持 `--map` 指定地图ID
- [ ] 支持 `--option` 覆盖默认选项（11个值的逗号分隔列表）
- [ ] 支持 `--resolution` 指定分辨率索引
- [ ] 支持 `--game-dir` 指定游戏根目录
- [ ] 支持 `--dry-run` 只生成文件不启动
- [ ] 支持 `--list` 列出所有可用地图
- [ ] 支持 `--info 10001` 显示指定地图的详细信息（选项、玩家信息）
- [ ] 启动流程与 GUI 启动器完全一致（互斥锁、管道、命令行参数）
- [ ] 有清晰的日志输出，方便调试

## Context
- 现有代码在 `E:\玩家原创\神龙地图启动器5.2\神龙地图启动器_新版\`
- `map_parser.py` 已能解析 .map 文件的选项和玩家信息
- `config_generator.py` 已能生成 config.lua
- `launcher.py` 的 `_launch_game()` 方法包含完整的启动逻辑
- 互斥锁名称: `7fxx_dgtm`
- 管道数据: `struct.pack('<4I', PID+TID, 0, 0, 0)`
- game.exe 路径: `{game_dir}/core/game.exe`

## Notes
- 不要引入 PyQt6 依赖，保持纯命令行
- 使用 `ctypes` + `kernel32.CreateProcessA` 启动游戏
- 参考 `launcher.py` 中 `_launch_game()` 的完整实现
- 默认游戏目录可以尝试从当前目录向上查找包含 `core/game.exe` 的目录
