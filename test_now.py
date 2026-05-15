# -*- coding: utf-8 -*-
"""无 GUI 测试 — 直接走 ResourceControlService → GameBridge 启动地图 10002."""

import sys, time, os, glob
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from src.core.resource_control_service import ResourceControlService
from src.launcher.game_launcher import launch_game, diagnose_launch


def main():
    game_dir = project_root / "data"
    map_id = 10002
    options = [-1] * 10 + [0]
    res_idx = 1  # 窗口模式

    print(f"[测试] 地图: {map_id}, 分辨率: {res_idx}, game_dir: {game_dir}")

    # 1. 准备 manifest
    svc = ResourceControlService(game_dir)
    manifest = svc.prepare_launch_manifest(map_id=map_id, options=options, resolution_index=res_idx)

    if not manifest.is_valid():
        print(f"[失败] manifest 无效:\n" + "\n".join(manifest.errors))
        return 1

    print(f"[准备] 挂载点: {[str(p) for p in manifest.mount_points]}")

    # 2. 启动
    print("[启动] 调用 launch_game...")
    bridge, diag = launch_game(manifest)

    if bridge is None:
        print(f"[失败] 启动失败:\n{diag}")
        return 1

    pid = bridge.process_id
    print(f"[启动] 进程 PID={pid}")

    # 3. 等待并诊断
    print("[等待] 15 秒...")
    time.sleep(3)

    diag = diagnose_launch(game_dir, pid, map_id, timeout_seconds=15)

    # 4. 输出结果
    print("\n" + "=" * 60)
    print("[诊断]")
    print(f"  日志目录: {diag.get('log_dir')}")
    print(f"  失败类型: {diag.get('failure_kind')}")
    print(f"  成功标志: {diag.get('ok')}")
    print(f"  sanguo.o: {diag.get('has_sanguo_o')}")
    print(f"  地图ID匹配: {diag.get('map_id_match')}")
    print(f"  AfterRun帧数: {diag.get('after_run_count')}")
    print(f"  Render帧数: {diag.get('render_count')}")
    if diag["errors"]:
        print(f"  错误:\n    " + "\n    ".join(diag["errors"]))
    if diag.get("failure_kind") is None and diag.get("ok"):
        print("\n✅ 启动成功！游戏正常初始化。")
        return 0
    else:
        print(f"\n❌ 启动异常: {diag.get('failure_kind')}")
        # 额外输出 init.log 尾和 error.log
        dir_path = diag.get("log_dir")
        if dir_path:
            for log_name in ["error.log", "init.log"]:
                p = Path(dir_path) / log_name
                if p.exists():
                    content = p.read_text(encoding="gbk", errors="ignore")
                    print(f"\n--- {log_name} (tail 80) ---")
                    print(content[-1500:] if len(content) > 1500 else content)
        return 1


if __name__ == "__main__":
    sys.exit(main())
