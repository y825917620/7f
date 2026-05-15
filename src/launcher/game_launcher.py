# -*- coding: utf-8 -*-
"""GameBridge — 消费 MapLaunchManifest，只负责进程创建和 Win32 注入."""

import ctypes
from ctypes import wintypes
import lzma
import os
import struct
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.config_generator import generate_config_lua, generate_map_opt_lua
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

    # 使用 LogVerifier 验证
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

    def __init__(self, game_dir: Path, map_id: int, options: list,
                 resolution_index: int = 0):
        self.game_dir = Path(game_dir)
        self.map_id = int(map_id)
        self.options = list(options) if options else [-1] * 10 + [0]
        self.resolution_index = resolution_index
        self._handles = {}
        self._process_info = None
        self._prepare_errors = []

    @staticmethod
    def _process_safe_timestamp() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def prepare(self) -> bool:
        """准备 map.o + 分辨率设置 — 与原版 exe 行为一致."""
        game_dir = self.game_dir

        # 1. 编译 map.o — 只含当前选中地图的选项
        luac_path = _find_luac(game_dir)
        if luac_path:
            map_offset = self.map_id - 10000
            current_options = {map_offset: self.options}
            ok, err = _compile_map_o(game_dir, luac_path, current_options, self.map_id)
            if not ok:
                self._prepare_errors.append(f"编译 map.o 失败:\n{err}")

        # 2. 分辨率/窗口模式设置
        try:
            from .game_settings import update_game_setting
            update_game_setting(game_dir, self.resolution_index)
        except Exception as e:
            self._prepare_errors.append(f"分辨率设置失败: {e}")

        return len(self._prepare_errors) == 0

    def launch(self) -> tuple:
        """创建游戏进程."""
        kernel32 = ctypes.windll.kernel32

        kernel32.CreateMutexA.restype = wintypes.HANDLE
        self._handles["mutex"] = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

        kernel32.CreateFileMappingA.restype = wintypes.HANDLE
        kernel32.MapViewOfFile.restype = ctypes.c_void_p
        kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        kernel32.UnmapViewOfFile.restype = wintypes.BOOL

        # SHM start_info
        hStart = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 512, b"7fgame_game_client_start_info")
        if hStart:
            ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
            if ptr:
                ctypes.memset(ptr, 0, 512)
                ctypes.c_uint32.from_address(ptr).value = self.map_id
                kernel32.UnmapViewOfFile(ptr)

        # SHM login
        hLogin = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, 256, b"7fgame_game_client_login")
        if hLogin:
            ptr = kernel32.MapViewOfFile(hLogin, 0xF001F, 0, 0, 256)
            if ptr:
                ctypes.memset(ptr, 0, 256)
                buf = (ctypes.c_char * 256).from_address(ptr)
                buf.value = b"localplayer"
                kernel32.UnmapViewOfFile(ptr)

        class SECURITY_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", wintypes.LPVOID), ("bInheritHandle", wintypes.BOOL)]

        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(sa)
        sa.bInheritHandle = True

        hRead = wintypes.HANDLE()
        hWrite = wintypes.HANDLE()
        kernel32.CreatePipe(ctypes.byref(hRead), ctypes.byref(hWrite), ctypes.byref(sa), 0)
        hNul = kernel32.CreateFileA(b"NUL", 0x40000000, 3, None, 3, 0x80, None)

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
        si.dwFlags = 0x101
        si.wShowWindow = 1
        si.hStdInput = hRead
        si.hStdOutput = hNul
        si.hStdError = hNul

        game_path = self.game_dir / "core" / "game.exe"
        if not game_path.exists():
            game_path = self.game_dir / "game.exe"
        cmdline = f'"{game_path}" {self.map_id}'
        os.environ["PATH"] = str(self.game_dir / "core") + os.pathsep + os.environ.get("PATH", "")

        pi = PROCESS_INFORMATION()
        ok = kernel32.CreateProcessA(
            str(game_path).encode("mbcs"), cmdline.encode("mbcs"),
            None, None, True, 0, None,
            str(self.game_dir).encode("mbcs"),
            ctypes.byref(si), ctypes.byref(pi)
        )

        if not ok:
            err = kernel32.GetLastError()
            for h in [hRead, hWrite, hNul]:
                if h:
                    kernel32.CloseHandle(h)
            return False, f"CreateProcessA 失败 (错误码: {err})"

        kernel32.CloseHandle(hRead)
        pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, self.map_id, 0)
        written = wintypes.DWORD(0)
        kernel32.WriteFile(hWrite, pipe_data, len(pipe_data), ctypes.byref(written), None)
        kernel32.CloseHandle(hWrite)
        if hNul:
            kernel32.CloseHandle(hNul)

        self._process_info = {"pid": pi.dwProcessId, "tid": pi.dwThreadId, "hProcess": pi.hProcess}
        kernel32.CloseHandle(pi.hThread)
        return True, ""

    @property
    def process_id(self) -> Optional[int]:
        return self._process_info["pid"] if self._process_info else None

    @property
    def process_handle(self):
        return self._process_info["hProcess"] if self._process_info else None


def launch_game(game_dir: Path, map_id: int, options: list,
                resolution_index: int = 0) -> tuple:
    """简洁启动入口 — 匹配原版 exe 行为.

    原版流程: config.lua + map.o + CreateProcess.
    不创建 sl/map.map，不修改 GameSetting.inf.
    """
    bridge = GameBridge(game_dir, map_id, options, resolution_index)

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
    if diag["error_log_tail"]:
        messages.append(f"[错误日志]\n{diag['error_log_tail'][:1000]}")

    return bridge, "\n\n".join(messages)
