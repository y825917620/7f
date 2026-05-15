# Resource-Control Launcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reliable resource-control launcher that can import, analyze, unpack, mount, launch, verify, and later edit game/map resources without hardcoded map assumptions.

**Architecture:** Split the project into a resource control layer, a launch manifest layer, a mount strategy layer, and a game bridge layer. The launcher must treat original resources as read-only, generate explicit manifests for every operation, and verify game logs after every launch. Current code has partial modules, but launch still fails around `tab_interface nil` / map loading and lacks a complete manifest-driven resource contract.

**Tech Stack:** Python 3.11, PyQt6, Windows Win32 process/shared-memory/pipe APIs via `ctypes`, Lua 5.1 compiler (`lua51_bin/luac5.1.exe`), LZMA raw package handling, JSON manifests, `pytest` for automated tests.

---

## Current State Snapshot

The project already contains partial resource modules:

- `src/core/map_catalog.py`
- `src/core/map_package_analyzer.py`
- `src/core/map_launch_manifest.py`
- `src/core/resource_mount_manager.py`
- `src/core/resource_workspace.py`
- `src/launcher/game_launcher.py`
- `src/launcher/log_verifier.py`

The code compiles with:

```powershell
python -m py_compile src\core\map_catalog.py src\core\map_package_analyzer.py src\core\map_launch_manifest.py src\core\resource_mount_manager.py src\core\resource_workspace.py src\launcher\game_launcher.py src\launcher\log_verifier.py src\ui\main_window.py
```

However, the implementation is not complete against the desired architecture:

- `ResourceMountManager` writes only `data/sl/map.map` and does not consistently write or verify `data/core/sl/map.map`.
- `GameBridge.prepare()` still calls its own `_ensure_sl_map()` instead of consuming a verified launch manifest from `ResourceMountManager`.
- `MapLaunchManifest.set_hashes()` accepts `unpacked_sha256`, but `ResourceMountManager.prepare()` calls it with `dec_sha256`, which must be fixed.
- The launcher does not persist `launch_manifest.json` for each run.
- The current launch can fail before map loading with `tab_interface nil`, meaning game UI initialization context is still incomplete.
- The log verifier has a separate implementation from `diagnose_launch()`; they should be unified.
- Resource workspaces exist but are not used by the launch pipeline.
- There is no test suite for the new resource modules.

Known latest failure signatures:

- `scripts\game_init.lua:104: attempt to index global 'tab_interface' (a nil value)`
- Previous run: `读取地图[10002]失败, 游戏退出!`
- Latest log may stop after `读取地图表格, 加载地图相关脚本!`, before `begin load map[...]`.

Do not treat "game.exe process started" as success. Success means the selected map ID and mounted package are confirmed in logs and no map/resource/Lua initialization error is present.

---

## File Responsibility Map

### Existing Files To Modify

- `src/core/map_catalog.py`
  - Keep as read-only scanner.
  - Add stable resource records and deterministic diagnostics.

- `src/core/map_package_analyzer.py`
  - Own `.sl` analysis and raw LZMA decompression.
  - Produce verified decompressed `LuaRDGTM` package bytes.

- `src/core/map_launch_manifest.py`
  - Become the single source of truth for one launch.
  - Store map ID, paths, hashes, mount points, strategy, options, settings, and validation errors.

- `src/core/resource_mount_manager.py`
  - Own mount strategy execution.
  - Write launch cache and chosen mount points.
  - Never decide the map ID by itself.

- `src/core/resource_workspace.py`
  - Own `maps/source`, `maps/workspace`, `mods`, `cache/launch`.
  - Import resources without mutating original game runtime.

- `src/launcher/game_launcher.py`
  - Own only game process creation and Win32 injection.
  - Consume `MapLaunchManifest`; do not unpack or inspect resources directly.

- `src/launcher/log_verifier.py`
  - Own launch result verification.
  - Replace duplicate logic in `diagnose_launch()`.

- `src/ui/main_window.py`
  - UI should request a manifest and launch result.
  - UI should not write resource files or call low-level Win32 code.

- `build_launcher.py`
  - Remove or correct stale hidden import `src.core.sl_handler`.

### New Files To Create

- `src/core/resource_control_service.py`
  - High-level orchestration API used by UI:
    - validate selected map
    - create/update manifests
    - prepare launch cache
    - return launch-ready manifest

- `src/core/game_resource_index.py`
  - Read-only index of public game assets under `data/resource`.

- `tests/conftest.py`
  - Test fixtures for temp game directories and sample `.sl` files.

- `tests/test_map_package_analyzer.py`
  - Analyzer and decompression tests.

- `tests/test_map_launch_manifest.py`
  - Manifest serialization/validation tests.

- `tests/test_resource_mount_manager.py`
  - File mount and launch cache tests.

- `tests/test_resource_workspace.py`
  - Import/unpack workspace tests.

- `tests/test_game_bridge_contract.py`
  - Ensure GameBridge consumes manifest and does not perform resource work.

- `tests/test_log_verifier.py`
  - Verify success/failure classification from synthetic logs.

### Documentation Files To Update

- `docs/map_resource_format.md`
  - Record confirmed `.map`, `.sl`, and `LuaRDGTM` facts.

- `docs/game_launch_contract.md`
  - Record command line, shared memory, pipe payload, CWD, PATH, and log stages.

- `docs/map_mounting_decisions.md`
  - Record chosen/experimental mount strategies and evidence.

- `launcher_refactoring_plan.html`
  - Keep as human-facing overview; implementation truth lives in this Markdown plan.

---

## Implementation Rules

- Use TDD for all resource modules.
- Do not use previous throwaway test scripts as truth.
- Do not edit original files in `data/map`, `data/resource`, or `data/core` except the minimal known runtime mount points during launch.
- Every launch must produce a `launch_manifest.json`.
- Every mount must record input hash, output hash, mount points, and strategy.
- Every failure must stop before process creation unless the failure is explicitly part of a controlled launch experiment.
- All paths in manifests must be absolute or project-root relative consistently. Choose absolute paths for runtime manifests.
- Avoid hardcoded `10002` except in tests whose name explicitly says they test a sample map.

---

## Task 1: Add Test Fixtures And Baseline Sample Package Utilities

**Files:**

- Create: `tests/conftest.py`

- [ ] **Step 1: Create pytest fixtures**

Add this file:

```python
# -*- coding: utf-8 -*-

import lzma
from pathlib import Path

import pytest


def make_sl_bytes(payload: bytes) -> bytes:
    compressor = lzma.LZMACompressor(
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 67108864}],
    )
    compressed = compressor.compress(payload) + compressor.flush()
    props = bytes([0x5D, 0x00, 0x00, 0x40, 0x00])
    size = len(payload).to_bytes(8, "little")
    return props + size + compressed


@pytest.fixture
def sample_payload() -> bytes:
    return b"LuaRDGTMa2 synthetic package for tests"


@pytest.fixture
def temp_game_dir(tmp_path: Path, sample_payload: bytes) -> Path:
    game_dir = tmp_path / "data"
    (game_dir / "map").mkdir(parents=True)
    (game_dir / "core").mkdir()
    (game_dir / "resource").mkdir()

    (game_dir / "map" / "10002.map").write_bytes(b"MAPMETA10002")
    (game_dir / "map" / "10002.sl").write_bytes(make_sl_bytes(sample_payload))
    return game_dir
```

- [ ] **Step 2: Run fixture smoke command**

Run:

```powershell
python -m pytest --fixtures tests
```

Expected:

- pytest lists `sample_payload` and `temp_game_dir`.

---

## Task 2: Stabilize `MapPackageAnalyzer`

**Files:**

- Modify: `src/core/map_package_analyzer.py`
- Test: `tests/test_map_package_analyzer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_map_package_analyzer.py`:

```python
# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.map_package_analyzer import MapPackageAnalyzer
from tests.conftest import make_sl_bytes


def test_analyze_valid_raw_lzma_sl(tmp_path: Path):
    payload = b"LuaRDGTM payload"
    sl_path = tmp_path / "10005.sl"
    sl_path.write_bytes(make_sl_bytes(payload))

    report = MapPackageAnalyzer.analyze(sl_path)

    assert report["ok"] is True
    assert report["map_id"] == 10005
    assert report["decompressed_size"] == len(payload)
    assert report["header_valid"] is True
    assert report["dec_sha256"]


def test_decompress_returns_payload_for_valid_sl(tmp_path: Path):
    payload = b"LuaRDGTM another payload"
    sl_path = tmp_path / "10006.sl"
    sl_path.write_bytes(make_sl_bytes(payload))

    assert MapPackageAnalyzer.decompress(sl_path) == payload


def test_analyze_rejects_non_luardgtm_payload(tmp_path: Path):
    sl_path = tmp_path / "10007.sl"
    sl_path.write_bytes(make_sl_bytes(b"BADHEADER"))

    report = MapPackageAnalyzer.analyze(sl_path)

    assert report["ok"] is False
    assert report["header_valid"] is False
    assert "LuaRDGTM" in report["error"]
```

- [ ] **Step 2: Run test to verify current state**

Run:

```powershell
python -m pytest tests\test_map_package_analyzer.py -v
```

Expected:

- If tests fail, failures should identify report fields or decompression behavior.
- If tests pass, continue; the tests still protect future changes.

- [ ] **Step 3: Fix analyzer implementation if needed**

Ensure `MapPackageAnalyzer`:

- Uses raw LZMA decompression with header bytes `[0x5D, 0, 0, 0x40, 0]`.
- Verifies uncompressed size from bytes `5:13`.
- Verifies decompressed bytes start with `b"LuaRDGTM"`.
- Returns `dec_sha256` and `sl_sha256`.
- Does not write files.

- [ ] **Step 4: Run tests again**

Run:

```powershell
python -m pytest tests\test_map_package_analyzer.py -v
```

Expected:

- `3 passed`.

---

## Task 3: Fix And Expand `MapLaunchManifest`

**Files:**

- Modify: `src/core/map_launch_manifest.py`
- Test: `tests/test_map_launch_manifest.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_map_launch_manifest.py`:

```python
# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.map_launch_manifest import MapLaunchManifest


def test_manifest_records_hashes_and_mount_points(tmp_path: Path):
    unpacked = tmp_path / "cache" / "map_package.bin"
    unpacked.parent.mkdir()
    unpacked.write_bytes(b"LuaRDGTM data")

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=tmp_path / "data",
        sl_path=tmp_path / "data" / "map" / "10002.sl",
        unpacked_path=unpacked,
        mount_points=[tmp_path / "data" / "sl" / "map.map"],
        options=[-1] * 10 + [0],
    )
    manifest.set_hashes(sl_sha256="abc", unpacked_sha256="def")
    manifest.strategy = "file_dual_mount"

    data = manifest.to_dict()

    assert data["sl_sha256"] == "abc"
    assert data["unpacked_sha256"] == "def"
    assert data["strategy"] == "file_dual_mount"
    assert data["valid"] is True


def test_manifest_round_trip(tmp_path: Path):
    unpacked = tmp_path / "map_package.bin"
    unpacked.write_bytes(b"LuaRDGTM data")
    path = tmp_path / "launch_manifest.json"

    manifest = MapLaunchManifest(10005, tmp_path / "data", unpacked_path=unpacked)
    manifest.strategy = "cache_only"
    manifest.save(path)

    loaded = MapLaunchManifest.load(path)

    assert loaded.map_id == 10005
    assert loaded.strategy == "cache_only"
    assert loaded.unpacked_path == unpacked
```

- [ ] **Step 2: Run test**

Run:

```powershell
python -m pytest tests\test_map_launch_manifest.py -v
```

Expected:

- Tests pass after fixing `set_hashes` callers and path serialization if necessary.

- [ ] **Step 3: Standardize `set_hashes`**

Keep this signature:

```python
def set_hashes(self, sl_sha256: Optional[str] = None, unpacked_sha256: Optional[str] = None):
    self.sl_sha256 = sl_sha256
    self.unpacked_sha256 = unpacked_sha256
```

Do not use `dec_sha256` as a parameter name outside analyzer reports. Convert analyzer field to manifest field in `ResourceMountManager`.

---

## Task 4: Make `ResourceMountManager` Manifest-Driven And Dual-Mount Aware

**Files:**

- Modify: `src/core/resource_mount_manager.py`
- Test: `tests/test_resource_mount_manager.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_resource_mount_manager.py`:

```python
# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.resource_mount_manager import ResourceMountManager


def test_prepare_writes_launch_cache_and_both_mount_points(temp_game_dir: Path, sample_payload: bytes):
    manager = ResourceMountManager(temp_game_dir, cache_dir=temp_game_dir.parent / "cache" / "launch")

    manifest = manager.prepare(10002, temp_game_dir / "map" / "10002.sl")

    assert manifest.is_valid()
    assert manifest.strategy == "file_dual_mount"
    assert manifest.unpacked_path.exists()
    assert manifest.unpacked_path.read_bytes() == sample_payload
    assert (temp_game_dir / "sl" / "map.map").read_bytes() == sample_payload
    assert (temp_game_dir / "core" / "sl" / "map.map").read_bytes() == sample_payload
    assert len(manifest.mount_points) == 2
    assert manifest.sl_sha256
    assert manifest.unpacked_sha256


def test_prepare_rejects_missing_sl(temp_game_dir: Path):
    manager = ResourceMountManager(temp_game_dir)

    manifest = manager.prepare(10099, temp_game_dir / "map" / "10099.sl")

    assert manifest.is_valid() is False
    assert manifest.strategy == "missing_sl"
    assert manifest.errors
```

- [ ] **Step 2: Run tests and observe failure**

Run:

```powershell
python -m pytest tests\test_resource_mount_manager.py -v
```

Expected current failures:

- `set_hashes()` keyword mismatch or missing `core/sl/map.map`.
- Strategy is likely `sl_vfs` instead of `file_dual_mount`.

- [ ] **Step 3: Implement dual mount and cache**

Update `ResourceMountManager.prepare()` so it:

1. Analyzes `.sl`.
2. Decompresses with `MapPackageAnalyzer.decompress()`.
3. Writes decompressed bytes to `cache/launch/{map_id}_{timestamp}/map_package.bin`.
4. Writes the same bytes to both:
   - `game_dir/sl/map.map`
   - `game_dir/core/sl/map.map`
5. Sets:
   - `manifest.unpacked_path` to cache file
   - `manifest.mount_points` to both mount points
   - `manifest.strategy = "file_dual_mount"`
   - `manifest.set_hashes(sl_sha256=report["sl_sha256"], unpacked_sha256=report["dec_sha256"])`

Use a temporary file then replace target for each mount:

```python
def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests\test_resource_mount_manager.py -v
```

Expected:

- `2 passed`.

---

## Task 5: Connect Workspace Import/Unpack To The Real Launch Cache

**Files:**

- Modify: `src/core/resource_workspace.py`
- Test: `tests/test_resource_workspace.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_resource_workspace.py`:

```python
# -*- coding: utf-8 -*-

import json
from pathlib import Path

from src.core.resource_workspace import ResourceWorkspace


def test_import_map_preserves_source_and_manifest(temp_game_dir: Path):
    workspace = ResourceWorkspace(temp_game_dir.parent)

    manifest_path = workspace.import_map(
        10002,
        temp_game_dir / "map" / "10002.map",
        temp_game_dir / "map" / "10002.sl",
    )

    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["map_id"] == 10002
    assert data["files"][".map"]["sha256"]
    assert data["files"][".sl"]["analysis"]["ok"] is True


def test_unpack_to_workspace_writes_unpacked_info(temp_game_dir: Path, sample_payload: bytes):
    workspace = ResourceWorkspace(temp_game_dir.parent)
    workspace.import_map(10002, temp_game_dir / "map" / "10002.map", temp_game_dir / "map" / "10002.sl")

    unpacked = workspace.unpack_to_workspace(10002)

    assert unpacked.exists()
    assert unpacked.read_bytes() == sample_payload
    info_path = temp_game_dir.parent / "maps" / "workspace" / "10002" / "unpack_info.json"
    assert info_path.exists()
    info = json.loads(info_path.read_text(encoding="utf-8"))
    assert info["unpacked_sha256"]
```

- [ ] **Step 2: Run tests**

Run:

```powershell
python -m pytest tests\test_resource_workspace.py -v
```

Expected:

- Tests pass or reveal manifest field issues.

- [ ] **Step 3: Fix resource index bug**

In `index_game_resources()`, current code stores `stat.st_mtime` under `"size"` and `stat.st_size` under `"bytes"`. Replace with:

```python
index["files"][rel] = {
    "bytes": stat.st_size,
    "mtime": stat.st_mtime,
    "sha256": hashlib.sha256(entry.read_bytes()).hexdigest(),
}
```

- [ ] **Step 4: Re-run tests**

Run:

```powershell
python -m pytest tests\test_resource_workspace.py -v
```

Expected:

- `2 passed`.

---

## Task 6: Add `ResourceControlService` As The UI-Facing Orchestrator

**Files:**

- Create: `src/core/resource_control_service.py`
- Test: `tests/test_resource_control_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_resource_control_service.py`:

```python
# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.resource_control_service import ResourceControlService


def test_prepare_launch_manifest_for_existing_map(temp_game_dir: Path, sample_payload: bytes):
    service = ResourceControlService(temp_game_dir)

    manifest = service.prepare_launch_manifest(
        map_id=10002,
        options=[-1] * 10 + [0],
        resolution_index=0,
    )

    assert manifest.is_valid()
    assert manifest.map_id == 10002
    assert manifest.options == [-1] * 10 + [0]
    assert manifest.unpacked_path.read_bytes() == sample_payload
    assert manifest.strategy == "file_dual_mount"


def test_prepare_launch_manifest_reports_missing_map(temp_game_dir: Path):
    service = ResourceControlService(temp_game_dir)

    manifest = service.prepare_launch_manifest(
        map_id=10199,
        options=[-1] * 10 + [0],
        resolution_index=0,
    )

    assert manifest.is_valid() is False
    assert manifest.errors
```

- [ ] **Step 2: Implement service**

Create `src/core/resource_control_service.py`:

```python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List

from .map_catalog import MapCatalog
from .map_launch_manifest import MapLaunchManifest
from .resource_mount_manager import ResourceMountManager


class ResourceControlService:
    def __init__(self, game_dir: Path):
        self.game_dir = Path(game_dir)
        self.catalog = MapCatalog(self.game_dir)
        self.mount_manager = ResourceMountManager(self.game_dir)

    def prepare_launch_manifest(
        self,
        map_id: int,
        options: List[int],
        resolution_index: int = 0,
    ) -> MapLaunchManifest:
        rec = self.catalog.get_info(map_id)
        if rec is None:
            manifest = MapLaunchManifest(map_id=map_id, game_dir=self.game_dir, options=options, resolution_index=resolution_index)
            manifest.strategy = "missing_catalog_record"
            manifest.add_error(f"地图 {map_id} 未在 {self.catalog.map_dir} 中找到")
            return manifest

        diag = self.catalog.diagnose(map_id)
        if diag:
            manifest = MapLaunchManifest(
                map_id=map_id,
                game_dir=self.game_dir,
                map_path=rec.get("map_path"),
                sl_path=rec.get("sl_path"),
                options=options,
                resolution_index=resolution_index,
            )
            manifest.strategy = "catalog_invalid"
            manifest.add_error(diag)
            return manifest

        manifest = self.mount_manager.prepare(map_id, rec["sl_path"])
        manifest.map_path = rec.get("map_path")
        manifest.options = list(options)
        manifest.resolution_index = resolution_index
        return manifest
```

- [ ] **Step 3: Run tests**

Run:

```powershell
python -m pytest tests\test_resource_control_service.py -v
```

Expected:

- `2 passed`.

---

## Task 7: Refactor `GameBridge` To Consume Manifest Only

**Files:**

- Modify: `src/launcher/game_launcher.py`
- Test: `tests/test_game_bridge_contract.py`

- [ ] **Step 1: Write contract tests**

Create `tests/test_game_bridge_contract.py`:

```python
# -*- coding: utf-8 -*-

from pathlib import Path

from src.core.map_launch_manifest import MapLaunchManifest
from src.launcher.game_launcher import GameBridge


def test_game_bridge_accepts_manifest_without_unpacking(temp_game_dir: Path):
    mounted = temp_game_dir / "sl" / "map.map"
    mounted.parent.mkdir()
    mounted.write_bytes(b"LuaRDGTM mounted")

    manifest = MapLaunchManifest(
        map_id=10002,
        game_dir=temp_game_dir,
        unpacked_path=mounted,
        mount_points=[mounted],
        options=[-1] * 10 + [0],
    )
    manifest.strategy = "file_dual_mount"

    bridge = GameBridge(manifest)

    assert bridge.map_id == 10002
    assert bridge.game_dir == temp_game_dir
    assert bridge.manifest is manifest
```

- [ ] **Step 2: Change `GameBridge.__init__`**

Replace constructor shape with:

```python
def __init__(self, manifest: MapLaunchManifest):
    self.manifest = manifest
    self.game_dir = Path(manifest.game_dir)
    self.map_id = int(manifest.map_id)
    self.options = list(manifest.options)
    self.resolution_index = manifest.resolution_index
    self._handles = {}
    self._process_info = None
    self._prepare_errors = []
```

- [ ] **Step 3: Remove resource unpacking from `GameBridge.prepare()`**

`GameBridge.prepare()` must:

1. Refuse invalid manifest.
2. Generate `config.lua`.
3. Generate/compile `map.o` if compiler exists.
4. Update `GameSetting.inf`.
5. Save `launch_manifest.json`.

It must not call `_ensure_sl_map()`.

Use:

```python
manifest_path = self.game_dir / "launcher_logs" / f"launch_{self.map_id}_{self.process_safe_timestamp()}.json"
self.manifest.save(manifest_path)
```

Add helper:

```python
@staticmethod
def process_safe_timestamp():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
```

- [ ] **Step 4: Keep `launch()` Win32 behavior**

Do not change process creation yet except to ensure all map IDs come from `self.map_id`.

- [ ] **Step 5: Update `launch_game` entry point**

New signature:

```python
def launch_game(manifest: MapLaunchManifest) -> tuple[Optional[GameBridge], str]:
```

It should:

1. Create `GameBridge(manifest)`.
2. Call `bridge.prepare()`.
3. Call `bridge.launch()`.
4. Call `LogVerifier(game_dir).verify(expected_map_id=manifest.map_id, pid=bridge.process_id)` after Task 8 adds PID support.

- [ ] **Step 6: Run contract test**

Run:

```powershell
python -m pytest tests\test_game_bridge_contract.py -v
```

Expected:

- `1 passed`.

---

## Task 8: Unify Log Verification And Classify Current Failures

**Files:**

- Modify: `src/launcher/log_verifier.py`
- Modify: `src/launcher/game_launcher.py`
- Test: `tests/test_log_verifier.py`

- [ ] **Step 1: Write tests for log classifications**

Create `tests/test_log_verifier.py`:

```python
# -*- coding: utf-8 -*-

from pathlib import Path

from src.launcher.log_verifier import LogVerifier


def make_log(game_dir: Path, pid: int, init_text: str, error_text: str = "") -> Path:
    log_dir = game_dir / f"log{pid}-2026.05.15-00.00.00"
    log_dir.mkdir(parents=True)
    (log_dir / "init.log").write_text(init_text, encoding="gbk")
    if error_text:
        (log_dir / "error.log").write_text(error_text, encoding="gbk")
    return log_dir


def test_verify_detects_tab_interface_failure(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "设置读取地图名[10002]\n读取地图表格, 加载地图相关脚本!\n",
        "scripts\\game_init.lua:104: attempt to index global 'tab_interface' (a nil value)\n",
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10002, log_dir=log_dir)

    assert result["ok"] is False
    assert result["failure_kind"] == "ui_init_failed"


def test_verify_detects_map_read_failure(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "设置读取地图名[10005]\n[0] begin load map[10005]\n",
        "读取地图[10005]失败, 游戏退出!\n",
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10005, log_dir=log_dir)

    assert result["ok"] is False
    assert result["failure_kind"] == "map_read_failed"


def test_verify_success_requires_loop_after_map_load(tmp_path: Path):
    game_dir = tmp_path / "data"
    game_dir.mkdir()
    log_dir = make_log(
        game_dir,
        1234,
        "\n".join([
            "设置读取地图名[10002]",
            "do [core/gpi.o] ok!",
            "do [map/sanguo/sanguo.o] ok!",
            "[0] begin load map[10002]",
            "enter:AfterRunGameLogic",
            "enter:AfterRunGameLogic",
            "enter:AfterRunGameLogic",
            "enter:Render",
            "enter:Render",
            "enter:Render",
        ]),
    )

    result = LogVerifier(game_dir).verify(expected_map_id=10002, log_dir=log_dir)

    assert result["ok"] is True
    assert result["failure_kind"] is None
```

- [ ] **Step 2: Add `failure_kind` to verifier result**

Result dictionary must include:

```python
"failure_kind": None,
"error_log_tail": "",
```

Set:

- `ui_init_failed` when `error.log` contains `tab_interface` and `nil`.
- `map_read_failed` when `error.log` or `init.log` contains `读取地图[` and `失败`.
- `map_id_mismatch` when expected ID is not seen.
- `map_script_not_loaded` when `do [map/sanguo/sanguo.o] ok!` is missing after `begin load map`.
- `not_enough_runtime_frames` when map load appears but loop/render counts are too low.

- [ ] **Step 3: Read `error.log` inside verifier**

`LogVerifier.verify()` must read both `init.log` and `error.log`.

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests\test_log_verifier.py -v
```

Expected:

- `3 passed`.

---

## Task 9: Wire UI To ResourceControlService And Manifest Launch

**Files:**

- Modify: `src/ui/main_window.py`
- Modify: `src/launcher/game_launcher.py`

- [ ] **Step 1: Update imports**

In `src/ui/main_window.py`, import:

```python
from ..core.resource_control_service import ResourceControlService
from ..launcher.game_launcher import launch_game
```

- [ ] **Step 2: Replace direct launch parameter call**

In `_launch_game()`, replace the call pattern:

```python
bridge, diag_msg = launch_game(
    game_dir=game_dir,
    map_id=map_id,
    options=options,
    resolution_index=self.resolution_combo.currentIndex(),
)
```

with:

```python
service = ResourceControlService(game_dir)
manifest = service.prepare_launch_manifest(
    map_id=map_id,
    options=options,
    resolution_index=self.resolution_combo.currentIndex(),
)

if not manifest.is_valid():
    self._show_diag(
        "资源准备失败",
        "\n".join(manifest.errors),
        QMessageBox.Icon.Critical,
    )
    return

bridge, diag_msg = launch_game(manifest)
```

- [ ] **Step 3: Show manifest summary in diagnostics**

Before launch, build:

```python
manifest_summary = (
    f"地图ID: {manifest.map_id}\n"
    f"策略: {manifest.strategy}\n"
    f"源SL: {manifest.sl_path}\n"
    f"解包缓存: {manifest.unpacked_path}\n"
    f"挂载点:\n" + "\n".join(f"  - {p}" for p in manifest.mount_points)
)
```

Append this to `diag_msg` when showing launch diagnostics.

- [ ] **Step 4: Manual UI check**

Run:

```powershell
python main.py
```

Expected:

- Selecting a map and launching shows a diagnostic with manifest source, cache, mount points, and strategy.
- If launch fails, the failure is classified as resource prep, UI init, map read, map ID mismatch, or runtime frame failure.

---

## Task 10: Fix `tab_interface nil` As A Separate Launch-Context Defect

**Files:**

- Modify: `src/launcher/game_launcher.py`
- Modify: `docs/game_launch_contract.md`
- Test: manual launch verification

This task is intentionally separate from resource mounting. Do not change map package code while working this task.

- [ ] **Step 1: Reproduce and capture manifest**

Run launcher from source:

```powershell
python main.py
```

Launch map `10002`.

Expected:

- A `data/launcher_logs/launch_10002_*.json` exists.
- A game log exists under `data/log{pid}-...`.
- If failure is `ui_init_failed`, continue this task.

- [ ] **Step 2: Compare launch context fields**

Record in `docs/game_launch_contract.md`:

- `cwd`
- process command line
- whether game is launched with visible window
- whether stdout/stderr are redirected to `NUL`
- whether stdin pipe is inherited
- shared memory names and sizes
- pipe payload bytes
- whether `core/sl/map.map` exists
- whether `sl/map.map` exists

- [ ] **Step 3: Validate GameSetting baseline**

Add a pre-launch check in `GameBridge.prepare()`:

```python
setting_path = self.game_dir / "GameSetting.inf"
lines = setting_path.read_text(encoding="gbk", errors="ignore").splitlines()
if len(lines) < 21:
    self._prepare_errors.append("GameSetting.inf 少于 21 行")
    return False
```

Do not silently swallow `GameSetting.inf` write failures.

- [ ] **Step 4: Make stdout/stderr and stdin behavior explicit**

Current implementation uses:

- stdin: anonymous pipe read handle
- stdout/stderr: `NUL`

Keep this for first pass. If `tab_interface nil` persists, add a single controlled experiment flag in `GameBridge.launch()`:

```python
use_suspended_start = False
```

Do not add multiple experiments in one change.

- [ ] **Step 5: Verify with logs**

After each experiment, record:

- whether `tab_interface nil` appears
- whether `begin load map[...]` appears
- whether `do [map/sanguo/sanguo.o] ok!` appears

Stop after 3 failed launch-context experiments and update `docs/game_launch_contract.md` with all results before attempting more.

---

## Task 11: Validate Mount Strategy With Fresh Logs

**Files:**

- Modify: `docs/map_mounting_decisions.md`
- Modify: `src/core/resource_mount_manager.py` only if evidence supports change

- [ ] **Step 1: Confirm dual file mount**

After Task 4 and Task 9, launch `10002`.

Verify:

```powershell
Get-Item data\sl\map.map,data\core\sl\map.map | Select-Object FullName,Length,LastWriteTime
```

Expected:

- Both files exist.
- Both lengths equal manifest decompressed package length.

- [ ] **Step 2: Confirm selected map ID**

Inspect latest `init.log`:

```powershell
Get-Content data\log*\init.log | Select-String "设置读取地图名|begin load map"
```

Expected:

- The map ID is the selected map ID, not a stale ID.

- [ ] **Step 3: Try one non-10002 map**

Launch a map such as `10005`.

Expected:

- `launch_manifest.json` says `map_id = 10005`.
- mounted package hash equals `MapPackageAnalyzer.analyze(data/map/10005.sl)["dec_sha256"]`.
- log says `设置读取地图名[10005]` or a confirmed engine alias.

- [ ] **Step 4: Update decisions doc**

Add this table row to `docs/map_mounting_decisions.md` after the experiment, replacing only the `Result` value with the exact observed log summary:

```markdown
| Strategy | Evidence | Result | Decision |
|---|---|---|---|
| file_dual_mount | Both `sl/map.map` and `core/sl/map.map` written from manifest cache; logs reviewed on 10002 and 10005 | 10002: record `failure_kind` and final 5 log lines; 10005: record `failure_kind` and final 5 log lines | Use as default only if both maps reach `begin load map[...]` with matching IDs and no `map_read_failed`; otherwise keep as experimental |
```

---

## Task 12: Clean Build Script And Package Data Expectations

**Files:**

- Modify: `build_launcher.py`
- Modify: `神龙地图启动器.spec`

- [ ] **Step 1: Remove stale hidden import**

Remove:

```python
"--hidden-import", "src.core.sl_handler",
```

from `build_launcher.py` unless a real `src/core/sl_handler.py` is created.

- [ ] **Step 2: Add hidden imports for real modules**

Ensure these are present:

```python
"--hidden-import", "src.core.map_catalog",
"--hidden-import", "src.core.map_package_analyzer",
"--hidden-import", "src.core.map_launch_manifest",
"--hidden-import", "src.core.resource_mount_manager",
"--hidden-import", "src.core.resource_workspace",
"--hidden-import", "src.core.resource_control_service",
"--hidden-import", "src.launcher.log_verifier",
```

- [ ] **Step 3: Verify build command**

Run:

```powershell
python build_launcher.py
```

Expected:

- Build completes.
- No hidden import error for `src.core.sl_handler`.

---

## Task 13: Full Verification Checklist

Run these after implementation:

- [ ] Compile all source files:

```powershell
python -m py_compile src\core\*.py src\launcher\*.py src\ui\*.py
```

Expected:

- Exit code `0`.

- [ ] Run all tests:

```powershell
python -m pytest tests -v
```

Expected:

- All tests pass.

- [ ] Run resource dry run for 10 maps:

```powershell
@'
from pathlib import Path
from src.core.map_catalog import MapCatalog
from src.core.map_package_analyzer import MapPackageAnalyzer

game_dir = Path("data")
catalog = MapCatalog(game_dir)
ids = catalog.list_maps()[:10]
for mid in ids:
    rec = catalog.get_info(mid)
    report = MapPackageAnalyzer.analyze(rec["sl_path"])
    print(mid, report["ok"], report["decompressed_size"], report["dec_sha256"][:12])
'@ | python -
```

Expected:

- At least 10 lines.
- No `False` unless the map is documented as abnormal.

- [ ] Launch `10002` from UI.

Expected:

- `launch_manifest.json` created.
- selected map ID appears in logs.
- no `tab_interface nil`.
- no `读取地图[10002]失败`.

- [ ] Launch a non-10002 map from UI.

Expected:

- `launch_manifest.json` map ID equals selected map.
- mounted package hash equals selected map `.sl` decompressed hash.
- log map ID equals selected map or documented alias.

- [ ] Verify original resource immutability.

Expected:

- Files in `data/map/*.sl` and `data/map/*.map` unchanged by launch.
- Launch-generated files are under `cache/launch`, `data/sl`, `data/core/sl`, or `data/launcher_logs`.

---

## Completion Criteria

The implementation is complete only when all of these are true:

- Resource preparation is manifest-driven.
- Original map and game assets are preserved as read-only inputs.
- `ResourceControlService` is the only UI-facing resource preparation API.
- `GameBridge` consumes a manifest and does not unpack resources.
- Each launch writes `launch_manifest.json`.
- `LogVerifier` classifies `ui_init_failed`, `map_read_failed`, `map_id_mismatch`, and success.
- The UI no longer treats process creation as successful map launch.
- At least one map can complete import -> analyze -> unpack -> mount -> launch verification.
- At least one non-10002 map can be launched far enough that logs prove the selected ID and package are being used.

---

## Known Follow-Up After Stable Launch

Do not begin these until launch and map loading are stable:

- Parse `LuaRDGTM` internal segment table.
- Extract editable Lua scripts and resource references into workspace.
- Implement diff/rollback for workspace edits.
- Implement repack from workspace to `LuaRDGTM`.
- Implement `.sl` recompression/export if the game requires compressed package input.
- Implement public resource mod overlay mounting.
- Add UI editor for scripts, options, icons, textures, and model references.
