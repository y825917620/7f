# -*- coding: utf-8 -*-
"""检查原启动器的窗口结构和控件标识 (win32 backend)."""

import subprocess
import sys
import time
from pathlib import Path

launcher_exe = Path(r"E:\玩家原创\神龙地图启动器\data\神龙地图启动器.exe")

proc = subprocess.Popen([str(launcher_exe)], cwd=str(launcher_exe.parent))
print(f"[INFO] 启动器 PID={proc.pid}")
print("[INFO] 等待 5 秒让窗口加载...")
time.sleep(5)

try:
    from pywinauto import Application

    app = Application(backend="win32").connect(process=proc.pid)
    windows = app.windows()
    print(f"[INFO] 窗口数量: {len(windows)}")
    for w in windows:
        print(f"  - 标题: '{w.window_text()}' 类名: '{w.class_name()}' 句柄: {w.handle}")

    if windows:
        dlg = app.window(handle=windows[0].handle)
        print(f"\n[INFO] 主窗口控件树:")
        try:
            dlg.print_control_identifiers(depth=3)
        except Exception as e:
            print(f"[WARN] print_control_identifiers failed: {e}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n[INFO] 等待 3 秒后关闭...")
    time.sleep(3)
    proc.terminate()
    print("[INFO] 已终止")
    sys.exit(0)
