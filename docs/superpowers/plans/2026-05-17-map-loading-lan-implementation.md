# 地图加载与局域网联机完整实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让启动器稳定完成地图选择、资源准备、游戏启动、日志验证，并支持局域网主机/客户端进入同一地图会话。

**Architecture:** 以 `MapLaunchManifest` 作为一次启动的唯一事实来源。UI 只负责收集用户选择，`ResourceControlService` 负责地图包验证与挂载，`GameBridge` 只负责 Win32 启动契约，`LanSessionService` 负责主机/客户端联机握手和游戏期控制帧。

**Tech Stack:** Python 3.11, PyQt6, Windows Win32 API via `ctypes`, Lua 5.1 compiler, `.sl` LZMA/LuaRDGTM 包解析, TCP socket, pytest.

---

## 验收标准

- 单机模式：从 UI 选择任意已安装地图，生成配置，启动 `game.exe`，日志中出现地图加载成功标志，无 `tab_interface nil`、读取地图失败、Lua 初始化错误。
- 主机模式：主机选择地图和选项，服务端口启动，游戏进入会话，客户端能看到同一地图/选项。
- 客户端模式：输入主机 IP 和端口，收到主机 manifest 摘要，锁定地图和选项，启动本地 `game.exe` 并连接主机。
- 资源安全：原始 `data/map/{id}.map` 与 `data/map/{id}.sl` 不被覆盖；运行时生成物集中写入明确挂载点和缓存。
- 验证闭环：每次启动都保存 `launch_manifest.json`、启动诊断日志、游戏日志判定结果。
- 打包后验证：PyInstaller GUI exe 可以完成同样流程；终端运行导致的 `tab_interface nil` 只作为诊断提示，不作为成功路径。

---

## 当前关键断点

1. `tests/test_game_bridge_contract.py` 已经按 `GameBridge(manifest)` 写，但 `src/launcher/game_launcher.py` 仍是旧签名 `GameBridge(game_dir, map_id, options, ...)`。
2. `ResourceControlService` 已存在，但 UI 没有真正通过它获得启动 manifest。
3. `ResourceMountManager`、`docs/map_mounting_decisions.md`、`findings.md` 对默认挂载策略存在冲突，需要用可重复测试锁定。
4. `HostService` 目前是本地单进程模拟，尚未成为真正的 LAN 主机/客户端协议层。
5. 日志验证存在，但没有成为启动完成后的强制判定。

---

## 文件职责图

### 修改

- `src/core/map_package_analyzer.py`  
  只负责 `.sl` 格式分析、LZMA 解压、LuaRDGTM 结构校验，输出结构化报告和解压 bytes。

- `src/core/resource_mount_manager.py`  
  只负责把已验证地图包写到运行时挂载点。不得启动游戏，不得读取 UI 状态。

- `src/core/resource_control_service.py`  
  UI 面向编排层：地图索引、资源验证、挂载、manifest 创建、manifest 保存。

- `src/core/map_launch_manifest.py`  
  一次启动的完整结构：地图、选项、分辨率、玩家、模式、主机地址、挂载点、生成文件、错误、日志路径。

- `src/launcher/game_launcher.py`  
  消费 `MapLaunchManifest`，生成启动前配置，创建 Win32 SHM/管道/互斥体，启动进程。不得自行解包地图。

- `src/launcher/host_service.py`  
  拆成协议构建与服务运行两部分，支持真实 LAN 连接。

- `src/launcher/log_verifier.py`  
  统一成功/失败判定，返回结构化 `LaunchVerificationResult`。

- `src/ui/main_window.py`  
  使用 `ResourceControlService` 和新的 LAN 服务，不直接调用低层 Win32。

- `build_launcher.py` / `神龙地图启动器.spec`  
  更新隐藏导入、数据文件、GUI 打包参数。

### 新建

- `src/launcher/lan_protocol.py`  
  定义房间握手、地图 manifest 摘要、玩家信息、启动同步、心跳帧的编码/解码。

- `src/launcher/lan_session.py`  
  主机/客户端会话状态机，供 UI 调用。

- `tests/test_launch_manifest_contract.py`  
  manifest 字段、序列化、错误报告。

- `tests/test_lan_protocol.py`  
  LAN 包编码/解码和兼容性。

- `tests/test_lan_session.py`  
  本地 socket 主机/客户端集成测试。

- `tests/test_ui_launch_flow.py`  
  使用 monkeypatch 验证 UI 调用链，不真正启动游戏。

---

## 阶段 0：证据归一化与启动契约冻结

### Task 0.1：建立启动契约快照测试

**Files:**
- Create: `tests/test_current_launch_contract_snapshot.py`
- Read: `findings.md`
- Read: `docs/game_launch_contract.md`
- Read: `docs/map_mounting_decisions.md`

- [ ] 写测试，记录当前文档冲突必须被解决。

```python
from pathlib import Path


def test_launch_contract_documents_are_explicit():
    root = Path(__file__).resolve().parents[1]
    findings = (root / "findings.md").read_text(encoding="utf-8")
    contract = (root / "docs" / "game_launch_contract.md").read_text(encoding="utf-8")
    decisions = (root / "docs" / "map_mounting_decisions.md").read_text(encoding="utf-8")

    assert "CreateProcess" in contract
    assert "7fgame_game_client_start_info" in contract
    assert "tab_interface nil" in findings
    assert "默认策略" in decisions
```

- [ ] 运行：

```powershell
python -m pytest tests\test_current_launch_contract_snapshot.py -q
```

Expected: PASS。

- [ ] 人工确认并更新三个文档，使它们只保留一个默认路径：

```text
UI -> ResourceControlService -> MapLaunchManifest -> GameBridge -> game.exe -> LogVerifier
```

### Task 0.2：冻结默认启动契约

**Files:**
- Modify: `docs/game_launch_contract.md`
- Modify: `docs/map_mounting_decisions.md`
- Modify: `findings.md`

- [ ] 明确默认命令行，只允许一种默认形式：

```text
"{game_dir}\core\game.exe" {map_id}
```

- [ ] 明确启动前资源策略：

```text
默认策略名称：file_runtime_mount
输入：data/map/{map_id}.map 和 data/map/{map_id}.sl
输出：由 ResourceMountManager 生成运行时挂载点
禁止：覆盖原始 .map/.sl
```

- [ ] 明确 `MemoryMapName=sanguo` 与 `/mapfile=` 只作为实验策略，不作为默认路径。

---

## 阶段 1：MapLaunchManifest 成为唯一事实来源

### Task 1.1：扩展 manifest 字段和校验

**Files:**
- Modify: `src/core/map_launch_manifest.py`
- Test: `tests/test_launch_manifest_contract.py`

- [ ] 写失败测试：

```python
from pathlib import Path

from src.core.map_launch_manifest import MapLaunchManifest


def test_manifest_contains_launch_network_and_mount_context(tmp_path: Path):
    mounted = tmp_path / "data" / "sl" / "map.map"
    mounted.parent.mkdir(parents=True)
    mounted.write_bytes(b"LuaRDGTM")

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=tmp_path / "data",
        unpacked_path=mounted,
        mount_points=[mounted],
        options=[1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0],
        resolution_index=0,
        mode="host",
        host_ip="192.168.1.10",
        host_port=29002,
        player_name="Player1",
        player_slot=1,
    )

    data = manifest.to_dict()
    assert data["mode"] == "host"
    assert data["host_ip"] == "192.168.1.10"
    assert data["host_port"] == 29002
    assert data["player_name"] == "Player1"
    assert data["player_slot"] == 1
    assert data["valid"] is True
```

- [ ] 实现字段：

```python
mode: str = "single"
host_ip: str = "127.0.0.1"
host_port: int = 29002
player_name: str = "Player1"
player_slot: int = 1
generated_files: list[Path] = []
log_dir: Optional[Path] = None
verification: Optional[dict] = None
```

- [ ] `to_dict()` 和 `load()` 必须完整往返这些字段。

- [ ] 运行：

```powershell
python -m pytest tests\test_launch_manifest_contract.py -q
```

Expected: PASS。

---

## 阶段 2：地图资源准备与挂载

### Task 2.1：统一 `.sl` 解压接口

**Files:**
- Modify: `src/core/map_package_analyzer.py`
- Test: `tests/test_map_package_analyzer.py`

- [ ] 测试 `analyze()` 和 `decompress()` 使用同一套 LZMA 逻辑。

```python
from pathlib import Path

from src.core.map_package_analyzer import MapPackageAnalyzer
from tests.conftest import make_sl_bytes


def test_decompress_returns_luardgtm_payload(tmp_path: Path):
    sl_path = tmp_path / "10002.sl"
    payload = b"LuaRDGTM" + b"\x00" * 64
    sl_path.write_bytes(make_sl_bytes(payload))

    report = MapPackageAnalyzer.analyze(sl_path)
    assert report["ok"] is True
    assert MapPackageAnalyzer.decompress(sl_path) == payload
```

- [ ] 如果真实 `.sl` 使用 `lzma.FORMAT_ALONE` 而测试 fixture 使用 raw header，则实现兼容入口：

```python
def decompress_sl_bytes(data: bytes) -> bytes:
    if data.startswith(bytes([0x5D, 0x00, 0x00, 0x40, 0x00])):
        # parse 5-byte props + 8-byte size + raw stream
        ...
    return lzma.decompress(data, format=lzma.FORMAT_ALONE)
```

### Task 2.2：实现默认运行时挂载策略

**Files:**
- Modify: `src/core/resource_mount_manager.py`
- Test: `tests/test_resource_mount_manager.py`

- [ ] 写测试：

```python
from pathlib import Path

from src.core.resource_mount_manager import ResourceMountManager


def test_prepare_writes_runtime_mounts_without_mutating_original(temp_game_dir: Path):
    original_map = temp_game_dir / "map" / "10002.map"
    original_sl = temp_game_dir / "map" / "10002.sl"
    map_before = original_map.read_bytes()
    sl_before = original_sl.read_bytes()

    manifest = ResourceMountManager(temp_game_dir).prepare(10002, original_sl)

    assert manifest.is_valid()
    assert manifest.strategy == "file_runtime_mount"
    assert (temp_game_dir / "sl" / "map.map").exists()
    assert (temp_game_dir / "core" / "sl" / "map.map").exists()
    assert original_map.read_bytes() == map_before
    assert original_sl.read_bytes() == sl_before
```

- [ ] 实现时 `mount_points` 至少包含：

```text
data/sl/map.map
data/core/sl/map.map
```

- [ ] 如仍需要 `map/sanguo/sanguo.o`，把它作为兼容挂载点写入 manifest，不让它成为唯一策略。

### Task 2.3：ResourceControlService 生成并保存 manifest

**Files:**
- Modify: `src/core/resource_control_service.py`
- Test: `tests/test_resource_control_service.py`

- [ ] 目标调用：

```python
manifest = service.prepare_launch_manifest(
    map_id=10002,
    options=[-1] * 10 + [0],
    resolution_index=0,
    mode="host",
    host_ip="127.0.0.1",
    host_port=29002,
    player_name="Player1",
    player_slot=1,
)
```

- [ ] 断言：

```python
assert manifest.is_valid()
assert manifest.mode == "host"
assert manifest.host_port == 29002
assert (temp_game_dir / "cache" / "launch" / "launch_manifest.json").exists()
```

---

## 阶段 3：GameBridge 改为只消费 manifest

### Task 3.1：构造函数改造

**Files:**
- Modify: `src/launcher/game_launcher.py`
- Test: `tests/test_game_bridge_contract.py`

- [ ] 目标接口：

```python
bridge = GameBridge(manifest)
```

- [ ] 旧接口全部移除或放进兼容包装函数：

```python
def launch_game(manifest: MapLaunchManifest) -> tuple[GameBridge | None, str]:
    bridge = GameBridge(manifest)
    if not bridge.prepare():
        return None, "\n".join(bridge.prepare_errors)
    ok, err = bridge.launch()
    return (bridge, f"PID={bridge.process_id}") if ok else (None, err)
```

- [ ] `GameBridge.prepare()` 只做：

```text
生成 config.lua
生成/编译 map.o
生成/编译 core/edt2.o
更新 GameSetting.inf
记录 generated_files
```

- [ ] 禁止 `GameBridge` 调用 `.sl` 解压或挂载函数。

### Task 3.2：Win32 启动契约实现

**Files:**
- Modify: `src/launcher/game_launcher.py`
- Test: `tests/test_game_bridge_contract.py`

- [ ] `_build_cmdline()` 默认返回：

```python
return f'"{game_path}" {self.manifest.map_id}'
```

- [ ] `launch()` 创建：

```text
CreateMutexA("7fxx_dgtm")
CreateFileMappingA("7fgame_game_client_start_info", 512 bytes)
CreateFileMappingA("7fgame_game_client_login", 256 bytes)
匿名管道，read 端作为 hStdInput
NUL 作为 hStdOutput/hStdError
CreateProcessA(..., cwd=game_dir)
WriteFile(pipe, struct.pack("<4I", pid, tid, map_id, 0))
```

- [ ] 单元测试使用 monkeypatch 替代真实 `ctypes.windll.kernel32`，只断言调用顺序和参数。

---

## 阶段 4：日志验证成为启动结果的一部分

### Task 4.1：结构化日志验证

**Files:**
- Modify: `src/launcher/log_verifier.py`
- Test: `tests/test_log_verifier.py`

- [ ] 定义结果：

```python
@dataclass
class LaunchVerificationResult:
    status: str  # success | pending | failed
    reason: str
    log_dir: Path | None
    evidence: list[str]
```

- [ ] 成功证据：

```text
do [map/sanguo/sanguo.o] ok!
enter:AfterRunGameLogic
enter:Render
```

- [ ] 失败证据：

```text
读取地图
失败
tab_interface is nil
attempt to index global 'tab_interface'
ksui::lua_UIProgress_SetValue
```

### Task 4.2：启动后自动验证

**Files:**
- Modify: `src/launcher/game_launcher.py`
- Modify: `src/ui/main_window.py`

- [ ] `launch_game()` 返回 PID 后，启动轻量验证循环：

```text
0-3 秒：pending
3-15 秒：读取最新 log 目录
成功/失败：写入 manifest.verification
超时：pending_timeout
```

- [ ] UI 状态栏显示：

```text
PID=1234 | 等待日志
PID=1234 | 地图加载成功
PID=1234 | 启动失败: tab_interface nil，建议使用打包 GUI exe
```

---

## 阶段 5：LAN 协议层

### Task 5.1：定义启动器之间的 LAN 协议

**Files:**
- Create: `src/launcher/lan_protocol.py`
- Test: `tests/test_lan_protocol.py`

- [ ] 包格式：

```text
magic: b"SLAN"
version: uint16 = 1
type: uint16
length: uint32
payload: UTF-8 JSON
```

- [ ] 消息类型：

```python
HELLO = 1
ROOM_STATE = 2
PLAYER_JOIN = 3
PLAYER_LEAVE = 4
READY = 5
START_LAUNCH = 6
HEARTBEAT = 7
ERROR = 8
```

- [ ] 测试：

```python
from src.launcher.lan_protocol import encode_packet, decode_packets, ROOM_STATE


def test_room_state_round_trip():
    packet = encode_packet(ROOM_STATE, {"map_id": 10002, "options": [1, 0, 0]})
    decoded, rest = decode_packets(packet)
    assert rest == b""
    assert decoded[0].type == ROOM_STATE
    assert decoded[0].payload["map_id"] == 10002
```

### Task 5.2：主机会话服务

**Files:**
- Create: `src/launcher/lan_session.py`
- Test: `tests/test_lan_session.py`

- [ ] `LanHostSession` 职责：

```text
监听 0.0.0.0:{port}
接受客户端
发送 ROOM_STATE
维护玩家列表
收到 READY
主机点击启动后广播 START_LAUNCH
```

- [ ] `LanClientSession` 职责：

```text
连接主机
发送 HELLO
接收 ROOM_STATE
本地生成 manifest
发送 READY
收到 START_LAUNCH 后启动游戏
```

- [ ] 集成测试在本机随机端口运行，不依赖真实 game.exe。

---

## 阶段 6：游戏内部 HostService 与 LAN 会话对齐

### Task 6.1：拆分游戏协议构建函数

**Files:**
- Modify: `src/launcher/host_service.py`
- Test: `tests/test_host_service_protocol.py`

- [ ] 保留并测试：

```python
_build_packet()
_build_login_result()
_build_control_frame()
_build_player_record()
```

- [ ] 新增 `GameHostService(host_ip, host_port, players, local_slot)`，不再硬编码只绑定 `127.0.0.1`。

### Task 6.2：主机/客户端启动参数差异

**Files:**
- Modify: `src/launcher/game_launcher.py`
- Modify: `src/core/map_launch_manifest.py`

- [ ] 主机 manifest：

```text
mode=host
host_ip=本机局域网 IP
host_port=29002
player_slot=1
```

- [ ] 客户端 manifest：

```text
mode=client
host_ip=主机 IP
host_port=29002
player_slot=主机分配槽位
```

- [ ] `build_platform_block()` 用 manifest 字段生成，而不是 UI 参数。

---

## 阶段 7：UI 串联

### Task 7.1：主流程改造

**Files:**
- Modify: `src/ui/main_window.py`
- Test: `tests/test_ui_launch_flow.py`

- [ ] UI 点击启动时：

```python
service = ResourceControlService(gd)
manifest = service.prepare_launch_manifest(
    map_id=mid,
    options=options,
    resolution_index=self._res_combo.currentIndex(),
    mode=mode,
    host_ip=self._host_ip.text().strip() or "127.0.0.1",
    host_port=int(self._host_port.text().strip() or "29002"),
    player_name=self._player_name.text().strip() or "Player1",
    player_slot=self._player_slot.value(),
)
bridge, msg = launch_game(manifest)
```

- [ ] 客户端模式下，地图表格和选项控件锁定为主机下发的 ROOM_STATE。

### Task 7.2：房间状态 UI

**Files:**
- Modify: `src/ui/main_window.py`

- [ ] 主机显示：

```text
房间 IP:PORT
玩家列表
准备状态
启动同步状态
```

- [ ] 客户端显示：

```text
连接状态
主机地图
主机选项
本机槽位
```

---

## 阶段 8：端到端验证

### Task 8.1：自动化测试矩阵

**Run:**

```powershell
python -m pytest tests\test_map_package_analyzer.py tests\test_resource_mount_manager.py tests\test_resource_control_service.py tests\test_game_bridge_contract.py tests\test_lan_protocol.py tests\test_lan_session.py tests\test_log_verifier.py -q
```

Expected: 全部 PASS。

### Task 8.2：真实游戏手工验证

**Cases:**

- [ ] 单机地图 `10002`
- [ ] 单机地图 `10005`
- [ ] 主机 `10002` + 本机客户端
- [ ] 两台机器 LAN：主机 `10002`，客户端加入
- [ ] 客户端断线重连
- [ ] 主机关闭房间

**Each case records:**

```text
manifest path
PID
log dir
verification status
failure evidence if any
```

### Task 8.3：GUI 打包验证

**Run:**

```powershell
python build_launcher.py
```

Expected:

```text
dist/神龙地图启动器.exe exists
GUI 启动不出现 tab_interface nil
```

---

## 实施顺序

1. 阶段 0：先冻结契约，避免继续在 `/mapfile=`、`MemoryMapName=sanguo`、文件挂载之间摇摆。
2. 阶段 1-3：打通单机地图加载主链路。
3. 阶段 4：把“进程启动了”和“地图真的加载了”分开判断。
4. 阶段 5-6：做 LAN 房间和游戏内部 host service。
5. 阶段 7：UI 接入。
6. 阶段 8：真实游戏、双机、打包验证。

---

## 风险与处理

| 风险 | 表现 | 处理 |
|---|---|---|
| 文档结论冲突 | 测试按一种契约写，代码按另一种契约跑 | 阶段 0 必须先完成 |
| `tab_interface nil` | 终端运行失败，GUI 运行可能成功 | 作为 LogVerifier 的明确诊断，不把终端进程启动当成功 |
| 地图挂载路径不确定 | 读取地图失败 | 保留实验策略，但默认策略只允许一个 |
| LAN 游戏协议不完整 | 客户端连接后卡住或不同步 | 先做启动器间同步，再逐步补游戏控制帧 |
| 打包缺导入 | exe 启动报模块缺失 | build 脚本加入所有新模块 hidden imports |

---

## 完成定义

- 所有新增和相关旧测试通过。
- `ResourceControlService` 是 UI 唯一资源入口。
- `GameBridge` 只接受 `MapLaunchManifest`。
- `launch_manifest.json` 每次启动都会保存。
- 单机和 LAN 均有手工验证记录。
- 打包后的 GUI exe 能完成真实启动流程。
