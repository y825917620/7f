---
task_id: "task_003"
status: "active"
role: "executor"
priority: "medium"
created_by: "planner"
created_at: "2026-05-13T12:00:00Z"
---

# Task: 重新优化项目目录结构

## Objective
将当前混乱的单层目录结构重构为清晰的分层架构，分离核心解析、启动逻辑、UI 组件和独立工具，同时保持现有功能不受影响。

## Current Structure（问题）
```
神龙地图启动器_新版/
  launcher.py           ← 主程序，混杂了UI、启动、数据所有逻辑
  config_generator.py   ← 配置文件生成
  map_parser.py         ← .map文件解析
  map_data.py           ← 静态地图数据
  sponsor_widgets.py    ← 赞助UI组件
  神龙地图启动器_新版.spec  ← PyInstaller配置
  *.json / *.txt        ← 各种调试/中间文件
  build/ / dist/        ← 打包输出
```

## Target Structure
```
神龙地图启动器_新版/
  src/
    core/               # 核心解析引擎（无UI依赖）
      __init__.py
      map_parser.py     # .map文件解析
      resource_analyzer.py  # 二进制资源分析
      config_generator.py   # config.lua / edt2.o 生成
    launcher/           # 启动逻辑（无UI依赖）
      __init__.py
      game_launcher.py  # 互斥锁、管道、CreateProcessA
      game_settings.py  # GameSetting.inf 读写
    data/               # 静态数据
      __init__.py
      map_data.py       # MAP_INFO, MAP_CATEGORIES
      map_player_info.json  # 解析出的玩家信息
      vip_products.py   # VIP产品列表
    ui/                 # GUI组件
      __init__.py
      main_window.py    # 主窗口
      map_list.py       # 地图列表组件
      option_panel.py   # 选项面板
      sponsor_widgets.py    # 赞助/推广组件
    tools/              # 独立命令行工具
      __init__.py
      map_loader.py     # CLI地图加载工具
      extract_map_info.py   # 批量提取.map信息
  assets/               # 图标、缩略图缓存
    icon.ico
  dist/                 # 打包输出
  build/                # 打包中间文件
  tests/                # 测试脚本
  task_plan.md / findings.md / progress.md  # 项目规划
```

## Plan
1. 创建新的目录结构
2. 将现有文件按功能分类移动到对应目录
3. 添加 `__init__.py` 使每个目录成为 Python 包
4. 更新所有 import 路径
5. 更新 PyInstaller spec 文件，适配新结构
6. 保留 `launcher.py` 在根目录作为入口点（或者创建新的 `main.py`）
7. 清理不再需要的中间文件（*.json 调试文件等可保留在 data/ 下）

## Acceptance Criteria
- [ ] 新目录结构已创建
- [ ] 所有 Python 文件已移动到正确位置
- [ ] 所有 import 已更新且能正确运行
- [ ] `python -m src.ui.main_window` 能启动 GUI
- [ ] `python -m src.tools.map_loader --help` 能运行 CLI
- [ ] PyInstaller spec 已更新并能成功打包
- [ ] 原 `launcher.py` 等旧文件已删除（确认新结构运行正常后）

## Context
- 当前所有文件在 `E:\玩家原创\神龙地图启动器5.2\神龙地图启动器_新版\`
- PyInstaller spec 文件: `神龙地图启动器_新版.spec`
- 现有 import 关系较简单，主要是 `from map_data import ...`、`from map_parser import ...` 等

## Notes
- 重构时不要修改功能代码，只做移动和 import 更新
- 保留 `map_data.py` 的兼容性，它是核心数据文件
- spec 文件中的 `pathex` 需要包含 `src/`
- 移动文件后先测试 Python 能否 import，再测试打包
