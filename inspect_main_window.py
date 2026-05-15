# -*- coding: utf-8 -*-
import subprocess
import sys
import time
from pathlib import Path

launcher_exe = Path(r"E:\玩家原创\神龙地图启动器\data\神龙地图启动器.exe")

proc = subprocess.Popen([str(launcher_exe)], cwd=str(launcher_exe.parent))
print(f"[INFO] 启动器 PID={proc.pid}")
time.sleep(5)

try:
    from pywinauto import Application

    app = Application(backend="win32").connect(process=proc.pid)
    windows = app.windows()
    print(f"[INFO] 所有窗口:")
    for w in windows:
        print(f"  - 标题: '{w.window_text()}' 类名: '{w.class_name()}' 句柄: {w.handle}")

    # Find the main launcher window
    main = None
    for w in windows:
        if w.window_text() == '神龙地图启动器' and w.class_name() == '#32770':
            main = w
            break

    if main:
        print(f"\n[INFO] 检查主窗口 (handle={main.handle}):")
        dlg = app.window(handle=main.handle)
        try:
            dlg.print_control_identifiers(depth=3)
        except Exception as e:
            print(f"[WARN] {e}")
    else:
        print("[WARN] 未找到主窗口")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

finally:
    time.sleep(3)
    proc.terminate()
    sys.exit(0)
