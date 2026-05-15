import sys, time, ctypes, os, struct
from ctypes import wintypes
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import QTimer

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器\data")
MAP_ID = 10002

app = QApplication(sys.argv)
# 最小窗口 — 模仿原启动器
label = QLabel("神龙地图启动器")
label.setWindowTitle("神龙地图启动器")
label.show()
app.processEvents()

# SHM + Mutex
kernel32 = ctypes.windll.kernel32
kernel32.CreateFileMappingA.restype = wintypes.HANDLE
kernel32.MapViewOfFile.restype = ctypes.c_void_p
kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
kernel32.UnmapViewOfFile.restype = wintypes.BOOL
kernel32.CreateMutexA.restype = wintypes.HANDLE
kernel32.CreateMutexA(None, False, b"7fxx_dgtm")

for name, size, val in [(b"7fgame_game_client_start_info", 512, MAP_ID), (b"7fgame_game_client_login", 256, None)]:
    hMap = kernel32.CreateFileMappingA(wintypes.HANDLE(-1), None, 0x04, 0, size, name)
    if hMap:
        ptr = kernel32.MapViewOfFile(hMap, 0xF001F, 0, 0, size)
        if ptr:
            ctypes.memset(ptr, 0, size)
            if val is not None:
                ctypes.c_uint32.from_address(ptr).value = val
            else:
                buf = (ctypes.c_char * size).from_address(ptr)
                buf.value = b"localplayer"
            kernel32.UnmapViewOfFile(ptr)

# Pipe + NUL + CreateProcess
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

game_path = GAME_DIR / "core" / "game.exe"
cmdline = f'"{game_path}" {MAP_ID}'
os.environ["PATH"] = str(GAME_DIR / "core") + os.pathsep + os.environ.get("PATH", "")

pi = PROCESS_INFORMATION()
ok = kernel32.CreateProcessA(
    str(game_path).encode("mbcs"), cmdline.encode("mbcs"),
    None, None, True, 0, None,
    str(GAME_DIR).encode("mbcs"),
    ctypes.byref(si), ctypes.byref(pi)
)

pid = pi.dwProcessId
pipe_data = struct.pack("<4I", pid, pi.dwThreadId, MAP_ID, 0)
written = wintypes.DWORD(0)
kernel32.WriteFile(hWrite, pipe_data, len(pipe_data), ctypes.byref(written), None)

kernel32.CloseHandle(hRead)
kernel32.CloseHandle(hWrite)
kernel32.CloseHandle(hNul)
kernel32.CloseHandle(pi.hThread)

# 写入结果文件
result_file = Path(r"E:\玩家原创\神龙地图启动器5.2\qt_launch_result.txt")

# 用 QTimer 延迟检查
def check():
    time.sleep(12)
    sys.path.insert(0, r"E:\玩家原创\神龙地图启动器5.2")
    from src.launcher.game_launcher import diagnose_launch
    d = diagnose_launch(GAME_DIR, pid, MAP_ID)
    result_file.write_text(
        f"PID={pid}\nfailure_kind={d.get('failure_kind')}\n"
        f"errors={d.get('errors', [])[:3]}\n"
        f"has_sanguo_o={d.get('has_sanguo_o')}\n"
        f"after_run={d.get('after_run_count')}\n",
        encoding="utf-8"
    )
    app.quit()

QTimer.singleShot(500, check)  # 等事件循环启动后再检查
app.exec()

