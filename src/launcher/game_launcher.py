# -*- coding: utf-8 -*-
"""GameBridge — 消费 MapLaunchManifest，只负责进程创建和 Win32 注入."""

import ctypes
from ctypes import wintypes
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.config_generator import generate_config_lua, generate_edt2_lua, generate_map_opt_lua
from ..core.map_launch_manifest import MapLaunchManifest
from ..data.map_data import DEFAULT_MAP_OPTIONS


# === Lua 编译器 ===

def _find_luac(game_dir: Path) -> Optional[Path]:
    """找到 luac5.1.exe 编译器."""
    candidates = [
        game_dir.parent / "lua51_bin" / "luac5.1.exe",
        Path(__file__).parent.parent.parent / "lua51_bin" / "luac5.1.exe",
    ]
    for c in candidates:
        if c and c.exists():
            return c.resolve()
    return None


def _compile_lua(luac_path: Path, output_path: Path, lua_src: str) -> tuple:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = output_path.with_suffix(".lua.tmp")
        tmp_path.write_text(lua_src, encoding="gbk")
        result = subprocess.run(
            [str(luac_path), "-s", "-o", str(output_path), str(tmp_path)],
            capture_output=True, text=True, timeout=10
        )
        tmp_path.unlink(missing_ok=True)
        if result.returncode != 0:
            return False, result.stderr[:500]
        return True, ""
    except Exception as e:
        return False, str(e)


def _write_config_lua(game_dir: Path, map_id: int, options: list) -> tuple:
    try:
        lua_src = generate_config_lua(map_id, options, game_dir=game_dir)
        for target in [game_dir / "config.lua", game_dir / "core" / "config.lua"]:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(lua_src, encoding="gbk")
        return True, ""
    except Exception as e:
        return False, f"写入 config.lua 失败: {e}"


def _compile_edt2(game_dir: Path, luac_path: Path, map_id: int, options: list) -> tuple:
    lua_src = generate_edt2_lua(map_id, options, game_dir=game_dir)
    for target in [game_dir / "core" / "edt2.o", game_dir / "edt2.o"]:
        ok, err = _compile_lua(luac_path, target, lua_src)
        if not ok:
            return False, f"编译 {target.name} 失败:\n{err}"
    return True, ""


def _compile_map_o(game_dir: Path, luac_path: Path,
                   current_options: dict, selected_map: int) -> tuple:
    """编译 map.o — 只包含当前选中地图的选项（与原版 exe 产物一致）.

    原版 map.o (202 bytes):
      g_map_display = 0
      g_map_opt = {offset: [11 values]}  # 只有 1 个条目
    """
    try:
        g_map_display = 0  # 原版产物确认为 0

        # 只包含当前选中地图的选项
        map_offset = selected_map - 10000
        g_map_opt = {}
        if current_options and map_offset in current_options:
            values = current_options[map_offset]
            if len(values) == 11:
                g_map_opt[map_offset] = list(values)

        # 如果没找到选项，用默认值
        if not g_map_opt:
            default = DEFAULT_MAP_OPTIONS.get(map_offset, [-1]*10 + [0])
            g_map_opt[map_offset] = list(default)

        lua_src = generate_map_opt_lua(g_map_display, g_map_opt)

        map_o_path = game_dir / "map.o"
        tmp_path = map_o_path.with_suffix(".lua.tmp")
        tmp_path.write_text(lua_src, encoding="gbk")

        result = subprocess.run(
            [str(luac_path), "-s", "-o", str(map_o_path), str(tmp_path)],
            capture_output=True, text=True, timeout=10
        )
        tmp_path.unlink(missing_ok=True)

        if result.returncode != 0:
            return False, f"luac 编译 map.o 失败:\n{result.stderr[:500]}"
        return True, ""
    except Exception as e:
        return False, f"编译 map.o 异常: {e}"


# === 启动后诊断 (通过 LogVerifier) ===

def diagnose_launch(game_dir: Path, pid: int, map_id: int,
                    timeout_seconds: int = 15) -> dict:
    """启动后读取游戏日志，返回诊断结果."""
    from .log_verifier import LogVerifier

    verifier = LogVerifier(game_dir)

    # 等待日志目录出现
    log_dir = None
    for _ in range(timeout_seconds):
        log_dir = verifier.find_latest_log_dir()
        if log_dir is not None and str(pid) in str(log_dir):
            break
        time.sleep(1)

    result = {
        "ok": False,
        "pid": pid,
        "map_id": map_id,
        "log_dir": str(log_dir) if log_dir else None,
        "stages": [],
        "errors": [],
        "failure_kind": None,
        "error_log_tail": "",
        "init_log_tail": "",
        "summary": "",
    }

    if log_dir is None:
        result["errors"].append("未找到游戏日志目录")
        result["summary"] = "游戏进程未能生成日志"
        return result

    # 使用 LogVerifier 验证。日志目录出现不代表初始化完成，继续轮询，
    # 避免把“还在启动”误判成地图脚本未加载。
    transient_failures = {
        None,
        "map_id_mismatch",
        "map_script_not_loaded",
        "not_enough_runtime_frames",
    }
    verification = None
    end_at = time.time() + timeout_seconds
    while time.time() < end_at:
        verification = verifier.verify(expected_map_id=map_id, log_dir=log_dir)
        if verification.get("ok"):
            break
        failure_kind = verification.get("failure_kind")
        if failure_kind not in transient_failures:
            break
        time.sleep(1)

    if verification is None:
        verification = verifier.verify(expected_map_id=map_id, log_dir=log_dir)
    result.update(verification)

    if verification.get("ok"):
        result["summary"] = "游戏已成功启动，地图加载正常"
    else:
        result["summary"] = "\n".join(verification.get("errors", []))

    return result


# === GameBridge ===

class GameBridge:
    """消费 MapLaunchManifest，执行进程创建和 Win32 注入.

    不允许自行解压资源 — 资源准备由 ResourceMountManager 完成。
    """

    def __init__(self, manifest: MapLaunchManifest):
        if not isinstance(manifest, MapLaunchManifest):
            raise TypeError("GameBridge 需要 MapLaunchManifest")
        if not manifest.is_valid():
            raise ValueError("Manifest 无效: " + "; ".join(manifest.errors or ["资源未准备完成"]))

        missing_mounts = [str(p) for p in manifest.mount_points if not Path(p).exists()]
        if missing_mounts:
            raise ValueError("Manifest 无效: 挂载文件不存在: " + "; ".join(missing_mounts))

        self.manifest = manifest
        self.game_dir = Path(manifest.game_dir)
        self.map_id = int(manifest.map_id)
        self.options = list(manifest.options) if manifest.options else [-1] * 10 + [0]
        self.resolution_index = manifest.resolution_index
        self._handles = {}
        self._process_info = None
        self._prepare_errors = []

    @staticmethod
    def _process_safe_timestamp() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _build_cmdline(self, game_path: Path) -> str:
        # 默认只交给游戏地图 ID。地图包已经由 ResourceMountManager 写入
        # sl/map.map 与 core/sl/map.map；编辑器参数会触发网络/重连链路。
        return f'"{game_path}" {self.map_id}'

    def _create_live_map_mapping(self, kernel32) -> Optional[str]:
        map_file = self.manifest.mount_points[0] if self.manifest.mount_points else self.manifest.unpacked_path
        if not map_file:
            return "没有可写入内存映射的地图包"

        try:
            data = Path(map_file).read_bytes()
        except Exception as e:
            return f"读取地图包失败，无法创建内存映射: {e}"

        size = len(data)
        high = (size >> 32) & 0xFFFFFFFF
        low = size & 0xFFFFFFFF
        h_map = kernel32.CreateFileMappingA(
            wintypes.HANDLE(-1), None, 0x04, high, low, b"sanguo"
        )
        if not h_map:
            return f"创建 MemoryMapName=sanguo 失败，错误码 {kernel32.GetLastError()}"

        ptr = kernel32.MapViewOfFile(h_map, 0xF001F, 0, 0, size)
        if not ptr:
            err = kernel32.GetLastError()
            kernel32.CloseHandle(h_map)
            return f"写入 MemoryMapName=sanguo 失败，错误码 {err}"

        ctypes.memmove(ptr, data, size)
        kernel32.UnmapViewOfFile(ptr)
        self._handles["live_map"] = h_map
        return None

    def prepare(self) -> bool:
        """准备 map.o + 分辨率设置 — 与原版 exe 行为一致."""
        game_dir = self.game_dir

        for mount_point in self.manifest.mount_points:
            if not Path(mount_point).exists():
                self._prepare_errors.append(f"地图挂载文件不存在: {mount_point}")

        if self._prepare_errors:
            return False

        # 1. 编译 map.o — 只含当前选中地图的选项
        ok, err = _write_config_lua(game_dir, self.map_id, self.options)
        if not ok:
            self._prepare_errors.append(err)

        luac_path = _find_luac(game_dir)
        if luac_path:
            map_offset = self.map_id - 10000
            current_options = {map_offset: self.options}
            ok, err = _compile_map_o(game_dir, luac_path, current_options, self.map_id)
            if not ok:
                self._prepare_errors.append(f"编译 map.o 失败:\n{err}")
            ok, err = _compile_edt2(game_dir, luac_path, self.map_id, self.options)
            if not ok:
                self._prepare_errors.append(err)
        else:
            self._prepare_errors.append("未找到 luac5.1.exe，无法编译 edt2.o/map.o")

        # 2. 分辨率/窗口模式设置
        try:
            from .game_settings import update_game_setting
            update_game_setting(game_dir, self.resolution_index)
        except Exception as e:
            self._prepare_errors.append(f"分辨率设置失败: {e}")

        try:
            manifest_path = game_dir / "launcher_logs" / f"launch_{self.map_id}_{self._process_safe_timestamp()}.json"
            self.manifest.save(manifest_path)
        except Exception as e:
            self._prepare_errors.append(f"保存启动清单失败: {e}")

        return len(self._prepare_errors) == 0

    def launch(self) -> tuple:
        """创建游戏进程."""
        kernel32 = ctypes.windll.kernel32

        kernel32.CreateMutexA.restype = wintypes.HANDLE
        self._handles["mutex"] = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

        class STARTUPINFOA(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("lpReserved", wintypes.LPSTR),
                ("lpDesktop", wintypes.LPSTR), ("lpTitle", wintypes.LPSTR),
                ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
                ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
                ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
                ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
                ("lpReserved2", wintypes.LPBYTE), ("hStdInput", wintypes.HANDLE),
                ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE),
            ]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
                        ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

        si = STARTUPINFOA()
        si.cb = ctypes.sizeof(si)
        si.dwFlags = 0x1
        si.wShowWindow = 1

        game_path = self.game_dir / "core" / "game.exe"
        if not game_path.exists():
            game_path = self.game_dir / "game.exe"
        cmdline = self._build_cmdline(game_path)
        os.environ["PATH"] = str(self.game_dir / "core") + os.pathsep + os.environ.get("PATH", "")

        pi = PROCESS_INFORMATION()
        ok = kernel32.CreateProcessA(
            str(game_path).encode("mbcs"), cmdline.encode("mbcs"),
            None, None, False, 0, None,
            str(self.game_dir).encode("mbcs"),
            ctypes.byref(si), ctypes.byref(pi)
        )

        if not ok:
            err = kernel32.GetLastError()
            return False, f"CreateProcessA 失败 (错误码: {err})"

        self._process_info = {"pid": pi.dwProcessId, "tid": pi.dwThreadId, "hProcess": pi.hProcess}
        kernel32.CloseHandle(pi.hThread)
        return True, ""

    @property
    def process_id(self) -> Optional[int]:
        return self._process_info["pid"] if self._process_info else None

    @property
    def process_handle(self):
        return self._process_info["hProcess"] if self._process_info else None


def launch_game(manifest: MapLaunchManifest) -> tuple:
    """从 MapLaunchManifest 启动游戏，资源准备必须已经完成."""
    try:
        bridge = GameBridge(manifest)
    except Exception as e:
        return None, f"启动清单无效:\n{e}"

    if not bridge.prepare():
        return None, "准备失败:\n" + "\n".join(bridge._prepare_errors)

    ok, err = bridge.launch()
    if not ok:
        return None, f"启动失败:\n{err}"

    diag = diagnose_launch(bridge.game_dir, bridge.process_id, bridge.map_id)
    messages = []

    if diag["stages"]:
        messages.append("[游戏初始化]\n" + "\n".join(f"  [OK] {s}" for s in diag["stages"]))
    if diag["errors"]:
        messages.append("[诊断问题]\n" + "\n".join(f"  [ERR] {e}" for e in diag["errors"]))
    if diag.get("failure_kind"):
        messages.append(f"[失败类型] {diag['failure_kind']}")
    if diag.get("log_dir"):
        messages.append(f"[日志目录]\n{diag['log_dir']}")
    for name, content in diag.get("diagnostic_logs", {}).items():
        if content:
            messages.append(f"[日志: {name}]\n{content}")

    return bridge, "\n\n".join(messages)
