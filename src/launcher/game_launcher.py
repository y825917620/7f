# -*- coding: utf-8 -*-
"""GameBridge — 移植自原启动器的完整启动逻辑 + 启动后诊断."""

import ctypes
from ctypes import wintypes
import lzma
import os
import struct
import subprocess
import time
from pathlib import Path
from typing import Optional

from ..core.config_generator import generate_config_lua, generate_edt2_lua, generate_map_opt_lua
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
                   current_options: dict, selected_map: int) -> tuple[bool, str]:
    """从当前选项动态编译 map.o.

    Returns:
        (成功, 错误信息)
    """
    try:
        g_map_display = 0
        g_map_opt = {}
        for offset, values in DEFAULT_MAP_OPTIONS.items():
            if current_options and offset in current_options:
                g_map_opt[offset] = list(current_options[offset])
            else:
                g_map_opt[offset] = list(values)

        lua_src = generate_map_opt_lua(g_map_display, g_map_opt)
        tmp_path = game_dir / "map_tmp.lua"
        tmp_path.write_text(lua_src, encoding="utf-8")

        map_o_path = game_dir / "map.o"
        result = subprocess.run(
            [str(luac_path), "-o", str(map_o_path), str(tmp_path)],
            capture_output=True, text=True, timeout=10
        )
        tmp_path.unlink(missing_ok=True)

        if result.returncode != 0:
            return False, f"luac 编译 map.o 失败:\n{result.stderr[:500]}"
        if not map_o_path.exists() or map_o_path.stat().st_size == 0:
            return False, "map.o 编译产物为空"
        return True, ""
    except FileNotFoundError:
        return False, f"找不到 luac 编译器: {luac_path}"
    except Exception as e:
        return False, f"编译 map.o 异常: {e}"


def _ensure_sl_map(game_dir: Path, map_id: int) -> tuple[bool, str]:
    """从 map/{map_id}.sl 解压生成 sl/map.map (虚拟文件系统).

    Returns:
        (成功, 错误信息)
    """
    try:
        sl_dir = game_dir / "sl"
        sl_dir.mkdir(exist_ok=True)
        map_map = sl_dir / "map.map"

        sl_file = game_dir / "map" / f"{map_id}.sl"
        if not sl_file.exists():
            return False, f"地图文件不存在:\n  {sl_file}"

        data = sl_file.read_bytes()
        decompressed = lzma.decompress(data)
        map_map.write_bytes(decompressed)
        return True, ""
    except Exception as e:
        return False, f"解压 sl/map.map 失败:\n  {e}"


# === 启动后诊断 ===

def diagnose_launch(game_dir: Path, pid: int, map_id: int,
                    timeout_seconds: int = 15) -> dict:
    """启动后读取游戏日志，返回诊断结果.

    轮询等待日志生成，然后分析 init.log 和 error.log，
    返回结构化的诊断报告，可直接展示给用户。
    """
    result = {
        "ok": False,
        "pid": pid,
        "map_id": map_id,
        "log_dir": None,
        "init_log_lines": 0,
        "stages": [],
        "errors": [],
        "error_log_tail": "",
        "init_log_tail": "",
        "summary": "",
    }

    log_dir = None
    for _ in range(timeout_seconds):
        for d in game_dir.glob("log*"):
            if d.is_dir() and str(pid) in d.name:
                log_dir = d
                break
        if log_dir:
            break
        time.sleep(1)

    if log_dir is None:
        result["errors"].append("未找到游戏日志目录 — 游戏可能在初始化前就崩溃了")
        result["summary"] = "游戏进程未能生成日志"
        return result

    result["log_dir"] = str(log_dir)

    # 读 init.log
    init_log = log_dir / "init.log"
    if init_log.exists():
        try:
            content = init_log.read_text("gbk", errors="ignore")
            lines = content.splitlines()
            result["init_log_lines"] = len(lines)

            for l in lines:
                if "设置读取地图名" in l:
                    result["stages"].append(f"识别地图: {l.strip()}")
                if "do [core/gpi.o]" in l and "ok!" in l:
                    result["stages"].append("游戏平台初始化成功")
                if "读取地图表格" in l:
                    result["stages"].append("加载地图脚本...")
                if "do [map/sanguo" in l:
                    result["stages"].append(f"地图包加载: {l.strip()}")
                if "map_init" in l and "成功" in l:
                    result["stages"].append("地图初始化成功")
                if "begin load map" in l:
                    result["stages"].append(f"开始加载地图: {l.strip()}")

            result["init_log_tail"] = "\n".join(
                l.strip() for l in lines[-15:] if l.strip()
            )

            run_count = content.count("AfterRunGameLogic")
            if run_count > 3:
                result["stages"].append(f"游戏运行中 (已执行 {run_count} 帧)")
        except Exception as e:
            result["errors"].append(f"读取 init.log 失败: {e}")

    # 读 error.log
    error_log = log_dir / "error.log"
    if error_log.exists():
        try:
            err_content = error_log.read_text("gbk", errors="ignore")
            err_lines = [l.strip() for l in err_content.splitlines() if l.strip()]
            result["error_log_tail"] = "\n".join(err_lines[-20:])

            for l in err_lines:
                if "tab_interface" in l and "nil" in l:
                    result["errors"].append(
                        "游戏 UI 初始化失败 (tab_interface nil)\n"
                        "→ 这通常是因为启动器进程没有 GUI 窗口上下文\n"
                        "→ 打包为 exe 后直接运行即可解决"
                    )
                if "读取地图" in l and "失败" in l:
                    result["errors"].append(f"地图加载失败: {l[:200]}")
                if "Lua" in l and ("error" in l.lower() or "失败" in l):
                    if not any("tab_interface" in e for e in result["errors"]):
                        result["errors"].append(f"Lua 脚本错误: {l[:200]}")
        except Exception as e:
            result["errors"].append(f"读取 error.log 失败: {e}")

    # 综合判定
    result["ok"] = len(result["errors"]) == 0

    if result["ok"]:
        result["summary"] = "游戏已成功启动，地图加载正常"
    else:
        result["summary"] = "\n".join(result["errors"])

    return result


# === GameBridge ===

class GameBridge:
    """接收地图参数，执行完整启动流程."""

    def __init__(self, game_dir: Path, map_id: int,
                 options: list, resolution_index: int = 0):
        self.game_dir = Path(game_dir)
        self.map_id = int(map_id)
        self.options = list(options)
        self.resolution_index = resolution_index
        self._handles = {}
        self._process_info = None
        self._prepare_errors = []

    def prepare(self) -> bool:
        """准备所有资源（config.lua, map.o, GameSetting.inf, sl/map.map）."""
        game_dir = self.game_dir

        # 1. 生成并写入 config.lua
        try:
            config_lua = generate_config_lua(self.map_id, self.options, game_dir=game_dir)
            (game_dir / "config.lua").write_text(config_lua, encoding="gbk")
        except Exception as e:
            self._prepare_errors.append(f"写入 config.lua 失败: {e}")
            return False

        # 2. 找到 lua 编译器
        luac_path = _find_luac(game_dir)

        # 3. 编译 map.o
        if luac_path:
            map_offset = self.map_id - 10000
            current_options = {map_offset: self.options} if self.options else {}
            ok, err = _compile_map_o(game_dir, luac_path, current_options, self.map_id)
            if not ok:
                self._prepare_errors.append(f"编译 map.o 失败:\n{err}")
        else:
            self._prepare_errors.append("未找到 luac5.1.exe — map.o 将使用已有版本")

        # 4. 更新 GameSetting.inf
        try:
            from .game_settings import update_game_setting
            update_game_setting(game_dir, self.resolution_index)
        except Exception as e:
            self._prepare_errors.append(f"更新 GameSetting.inf 失败: {e}")

        # 5. 解压 sl/map.map
        ok, err = _ensure_sl_map(game_dir, self.map_id)
        if not ok:
            self._prepare_errors.append(err)
            return False

        return True

    def launch(self) -> tuple[bool, str]:
        """创建游戏进程.

        Returns:
            (成功, 错误信息)
        """
        kernel32 = ctypes.windll.kernel32

        # 互斥体
        kernel32.CreateMutexA.restype = wintypes.HANDLE
        self._handles["mutex"] = kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

        # 共享内存: start_info
        kernel32.CreateFileMappingA.restype = wintypes.HANDLE
        kernel32.MapViewOfFile.restype = ctypes.c_void_p
        kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        kernel32.UnmapViewOfFile.restype = wintypes.BOOL

        hStart = kernel32.CreateFileMappingA(
            wintypes.HANDLE(-1), None, 0x04, 0, 512,
            b"7fgame_game_client_start_info"
        )
        if hStart:
            ptr = kernel32.MapViewOfFile(hStart, 0xF001F, 0, 0, 512)
            if ptr:
                ctypes.memset(ptr, 0, 512)
                ctypes.c_uint32.from_address(ptr).value = self.map_id
                kernel32.UnmapViewOfFile(ptr)
        self._handles["shm_start"] = hStart

        # 共享内存: login
        hLogin = kernel32.CreateFileMappingA(
            wintypes.HANDLE(-1), None, 0x04, 0, 256,
            b"7fgame_game_client_login"
        )
        if hLogin:
            ptr = kernel32.MapViewOfFile(hLogin, 0xF001F, 0, 0, 256)
            if ptr:
                ctypes.memset(ptr, 0, 256)
                buf = (ctypes.c_char * 256).from_address(ptr)
                buf.value = b"localplayer"
                kernel32.UnmapViewOfFile(ptr)
        self._handles["shm_login"] = hLogin

        # 管道
        class SECURITY_ATTRIBUTES(ctypes.Structure):
            _fields_ = [
                ("nLength", wintypes.DWORD),
                ("lpSecurityDescriptor", wintypes.LPVOID),
                ("bInheritHandle", wintypes.BOOL)
            ]

        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(sa)
        sa.bInheritHandle = True

        hRead = wintypes.HANDLE()
        hWrite = wintypes.HANDLE()
        kernel32.CreatePipe(ctypes.byref(hRead), ctypes.byref(hWrite), ctypes.byref(sa), 0)

        GENERIC_WRITE = 0x40000000
        OPEN_EXISTING = 3
        hNul = kernel32.CreateFileA(b"NUL", GENERIC_WRITE, 3, None, OPEN_EXISTING, 0x80, None)

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
            _fields_ = [
                ("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
                ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)
            ]

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
        work_dir = str(self.game_dir)
        cmdline = f'"{game_path}" {self.map_id}'

        os.environ["PATH"] = str(self.game_dir / "core") + os.pathsep + os.environ.get("PATH", "")

        pi = PROCESS_INFORMATION()
        ok = kernel32.CreateProcessA(
            str(game_path).encode("mbcs"),
            cmdline.encode("mbcs"),
            None, None, True, 0, None,
            work_dir.encode("mbcs"),
            ctypes.byref(si), ctypes.byref(pi)
        )

        if not ok:
            err = kernel32.GetLastError()
            kernel32.CloseHandle(hRead)
            kernel32.CloseHandle(hWrite)
            if hNul:
                kernel32.CloseHandle(hNul)
            return False, f"CreateProcessA 失败 (错误码: {err})\n游戏路径: {game_path}\n工作目录: {work_dir}"

        kernel32.CloseHandle(hRead)

        pipe_data = struct.pack("<4I", pi.dwProcessId, pi.dwThreadId, self.map_id, 0)
        written = wintypes.DWORD(0)
        kernel32.WriteFile(hWrite, pipe_data, len(pipe_data), ctypes.byref(written), None)
        kernel32.CloseHandle(hWrite)
        if hNul:
            kernel32.CloseHandle(hNul)

        self._process_info = {
            "pid": pi.dwProcessId,
            "tid": pi.dwThreadId,
            "hProcess": pi.hProcess,
        }
        kernel32.CloseHandle(pi.hThread)
        return True, ""

    @property
    def process_id(self) -> Optional[int]:
        if self._process_info:
            return self._process_info["pid"]
        return None

    @property
    def process_handle(self):
        if self._process_info:
            return self._process_info["hProcess"]
        return None


def launch_game(game_dir: Path, map_id: int, options: list,
                resolution_index: int = 0) -> tuple[Optional[GameBridge], str]:
    """启动游戏的便捷入口.

    Returns:
        (GameBridge 或 None, 诊断信息)
    """
    messages = []
    bridge = GameBridge(game_dir, map_id, options, resolution_index)

    # 准备阶段
    if not bridge.prepare():
        for err in bridge._prepare_errors:
            messages.append(f"[准备错误] {err}")
        return None, "\n\n".join(messages)

    # 启动阶段
    ok, err = bridge.launch()
    if not ok:
        messages.append(f"[启动错误] {err}")
        return None, "\n\n".join(messages)

    # 诊断阶段 — 等待日志并分析
    diag = diagnose_launch(game_dir, bridge.process_id, map_id)

    if diag["stages"]:
        messages.append("[游戏初始化阶段]\n" + "\n".join(f"  [OK] {s}" for s in diag["stages"]))

    if diag["errors"]:
        messages.append("[诊断发现问题]\n" + "\n".join(f"  [ERR] {e}" for e in diag["errors"]))

    if diag["error_log_tail"]:
        messages.append(f"[游戏错误日志尾部]\n{diag['error_log_tail'][:1000]}")

    diag["user_message"] = "\n\n".join(messages)
    return bridge, diag["user_message"]
