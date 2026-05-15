# 游戏启动契约文档

## 1. 进程启动参数

### 1.1 命令行
```
"{game_dir}\core\game.exe" {map_id}
```
- `map_id`: 十进制整数，如 `10002`
- 工作目录必须设为 `{game_dir}`（即 `data/`），不能设为 `data/core/`，否则游戏找不到 `ui/` 资源

### 1.2 CreateProcess 关键细节
- **lpApplicationName**: 可执行文件完整路径
- **lpCommandLine**: 带引号的路径 + 空格 + map_id
- **lpCurrentDirectory**: `data/` 根目录（字符串形式，非 `core/`）
- **dwCreationFlags**: 0（正常启动），原始代码误用 `CREATE_SUSPENDED`（0x04）+ `ResumeThread`，已修正
- **stdout/stderr**: 必须重定向到 `NUL` 设备句柄。GUI 模式下若无合法句柄，游戏 C++ 日志系统会在初始化时崩溃，导致 1 秒闪退。

## 2. 互斥体与共享内存

### 2.1 命名互斥体
- **名称**: `7fxx_dgtm`
- **用途**: 防止多开，游戏会尝试打开此互斥体
- **创建**: `CreateMutexA(NULL, FALSE, "7fxx_dgtm")`

### 2.2 共享内存段 1 — 启动信息
- **名称**: `7fgame_game_client_start_info`
- **大小**: 512 字节
- **写入**: 偏移 0 处写入 `uint32` 类型的 `map_id`
- **其余**: 清零

### 2.3 共享内存段 2 — 登录信息
- **名称**: `7fgame_game_client_login`
- **大小**: 256 字节
- **写入**: 字符串 `"localplayer"`
- **其余**: 清零

## 3. 管道数据

### 3.1 匿名管道
- 创建匿名管道，将 Read 端作为子进程的 `hStdInput`
- 子进程创建成功后，向 Write 端写入 16 字节:
```c
struct {
    uint32_t pid;
    uint32_t tid;
    uint32_t map_id;
    uint32_t reserved;  // 0
}
```
- 小端序（`struct.pack("<4I", ...)`）

### 3.2 NUL 重定向（关键修复）
```c
hNul = CreateFileA("NUL", GENERIC_WRITE, FILE_SHARE_READ|FILE_SHARE_WRITE, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
```
将 `hStdOutput` 和 `hStdError` 均设为 `hNul`，游戏启动后关闭句柄。

## 4. 环境变量

- `PATH` 需要包含 `{game_dir}\core`，以便 `game.exe` 加载同目录 DLL（如 `gpigame.dll`）

## 5. 日志验证阶段

游戏启动后会在 `{game_dir}\log{pid}-{timestamp}\` 目录生成日志:

| 文件 | 用途 |
|------|------|
| `init.log` | 初始化流程，包含地图加载状态 |
| `error.log` | 错误信息 |
| `log_err.log` | 日志系统错误 |

### 5.1 成功标志
- `init.log` 中出现 `do [map/sanguo/sanguo.o] ok!`
- `init.log` 中出现 `enter:AfterRunGameLogic` 多次（>2）
- `init.log` 中出现 `enter:Render` 多次（>2）

### 5.2 失败标志
- `init.log` 中出现 `读取地图[...]失败, 游戏退出!`
- `init.log` 中出现 `tab_interface is nil`（Lua UI 初始化失败）
- `error.log` 中出现 `ksui::lua_UIProgress_SetValue` 等 UI 函数错误

## 6. 已知问题与对策

| 问题 | 根因 | 对策 |
|------|------|------|
| 1 秒闪退 | GUI 无控制台，stdout 无效句柄导致 C++ 日志崩溃 | NUL 重定向 |
| tab_interface nil | 游戏 C++ UI 系统需要 GUI 父进程上下文（消息泵） | 打包为 PyInstaller GUI exe 运行 |
| sl/ 目录副作用 | 原启动器不创建 sl/，旧代码创建导致冲突 | 删除旧 sl/，仅复制核心地图包 |

## 7. tab_interface nil 实验记录 (2026-05-15)

5 轮启动上下文实验，全部在终端环境下失败：

| 实验 | 参数变化 | 结果 |
|------|----------|------|
| 1 | 默认 (NUL重定向 + 管道 + SHM) | ui_init_failed |
| 2 | 同上，重复验证 | ui_init_failed |
| 3 | 地图 10005 (非10002) | ui_init_failed |
| 4 | CREATE_SUSPENDED + ResumeThread | ui_init_failed |
| 5 | CONOUT$ 替换 NUL | ui_init_failed |

在全部实验中：
- Manifest 有效，双挂载点存在且内容正确
- 日志均到达 `设置读取地图名[sanguo]`
- error.log 中均有 `scripts\game_init.lua:104: attempt to index global 'tab_interface' (a nil value)`
- 游戏进程在 UI 初始化失败后无法继续加载地图

结论：`tab_interface nil` 与启动参数、资源挂载、管道/NUL 无关。
game.exe 的 C++ UI 系统 (`tab_interface`) 需要从 GUI 父进程继承窗口消息泵。
终端/控制台进程无法提供此上下文。解决方案：PyInstaller 打包为 Windows GUI 应用。
