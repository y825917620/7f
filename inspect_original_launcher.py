# -*- coding: utf-8 -*-
"""检查原启动器的窗口结构和控件标识."""

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

    # 通过进程ID连接
    app = Application(backend="uia").connect(process=proc.pid)
    print(f"[INFO] 已连接应用")

    # 列出所有顶层窗口
    windows = app.windows()
    print(f"[INFO] 窗口数量: {len(windows)}")
    for w in windows:
        print(f"  - 标题: '{w.window_text()}' 类名: '{w.class_name()}' 句柄: {w.handle}")

    # 获取主窗口（通常第一个就是）
    if windows:
        dlg = app.window(handle=windows[0].handle)
        print(f"\n[INFO] 主窗口控件树:")
        try:
            dlg.print_control_identifiers(depth=3)
        except Exception as e:
            print(f"[WARN] print_control_identifiers failed: {e}")
            # 手动列出直接子控件
            for child in dlg.children():
                try:
                    print(f"  - {child.control_type()}: '{child.window_text()}' auto_id={child.automation_id()}")
                except:
                    pass

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n[INFO] 等待 5 秒后关闭...")
    time.sleep(5)
    proc.terminate()
    print("[INFO] 已终止")
    sys.exit(0)
