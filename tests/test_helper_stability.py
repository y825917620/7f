# -*- coding: utf-8 -*-
"""测试原始 launcher 生成的 helper_get004 是否稳定."""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

launcher_exe = Path(r"E:\玩家原创\神龙地图启动器\data\神龙地图启动器.exe")
game_dir = launcher_exe.parent
edt2_path = game_dir / "core" / "edt2.o"


def run_launcher_and_extract():
    proc = subprocess.Popen([str(launcher_exe)], cwd=str(game_dir))
    time.sleep(5)

    try:
        from pywinauto import Application
        app = Application(backend="uia").connect(process=proc.pid)
        windows = app.windows()
        if not windows:
            return None
        dlg = app.window(handle=windows[0].handle)

        # Fill login
        try:
            dlg.child_window(auto_id="1048", control_type="Edit").set_text("test")
            dlg.child_window(auto_id="1049", control_type="Edit").set_text("test")
        except:
            pass

        # Click login
        try:
            dlg.child_window(auto_id="1029", control_type="Button").click()
        except:
            pass

        time.sleep(8)  # wait for game to start
    except Exception as e:
        print(f"[WARN] {e}")
    finally:
        proc.terminate()
        time.sleep(1)

    # Extract helper_get004 from edt2.o
    if edt2_path.exists():
        import subprocess as sp
        r = sp.run([r'E:\玩家原创\神龙地图启动器5.2\lua51_bin\luac5.1.exe', '-l', str(edt2_path)],
                   capture_output=True, text=True)
        lines = r.stdout.split('\n')
        for i, line in enumerate(lines):
            if 'function' in line and '8 instructions' in line:
                vals = []
                for j in range(i+1, min(i+10, len(lines))):
                    if 'LOADK' in lines[j] and ';' in lines[j]:
                        val = lines[j].split(';')[1].strip()
                        vals.append(val)
                return vals
    return None


def main():
    results = []
    for run in range(3):
        print(f"\n=== Run {run+1} ===")
        vals = run_launcher_and_extract()
        print(f"helper_get004: {vals}")
        if vals:
            results.append(vals)
        time.sleep(2)

    print("\n=== Summary ===")
    for i, vals in enumerate(results):
        print(f"Run {i+1}: {vals}")

    if len(results) > 1:
        same = all(v == results[0] for v in results[1:])
        print(f"All same: {same}")


if __name__ == "__main__":
    main()
