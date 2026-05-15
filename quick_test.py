# -*- coding: utf-8 -*-
"""直接使用原版 map.o/edt2.o/config.lua/GameSetting.inf，跳过生成，只做必要准备并启动."""

import sys, os, time
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from src.core.resource_control_service import ResourceControlService
from src.launcher.game_launcher import GameBridge, diagnose_launch

def main():
    game_dir = project_root / "data"
    map_id = 10002
    res_idx = 1  # 窗口模式

    # 验证原版文件存在
    for f in ["map.o", "config.lua", "core/edt2.o", "GameSetting.inf"]:
        assert (game_dir / f).exists(), f"缺原版文件: {f}"

    # 准备 manifest（只做 SL 解压到 sl/map.map）
    svc = ResourceControlService(game_dir)
    manifest = svc.prepare_launch_manifest(map_id=map_id, options=[-1]*10+[0], resolution_index=res_idx)
    if not manifest.is_valid():
        print(f"[失败] manifest:\n" + "\n".join(manifest.errors))
        return 1

    # 启动（不调 prepare()，直接调 bridge.launch()）
    bridge = GameBridge(manifest)
    ok, err = bridge.launch()
    if not ok:
        print(f"[失败] 启动: {err}")
        return 1

    pid = bridge.process_id
    print(f"[启动] PID={pid}")

    time.sleep(3)
    diag = diagnose_launch(game_dir, pid, map_id, timeout_seconds=15)

    print(f"\n诊断:")
    print(f"  sanguo.o: {diag.get('has_sanguo_o')}")
    print(f"  失败类型: {diag.get('failure_kind')}")
    print(f"  错误: {'; '.join(diag['errors']) if diag['errors'] else '无'}")
    print(f"  AfterRun: {diag.get('after_run_count')}")
    print(f"  Render: {diag.get('render_count')}")

    if diag.get("ok"):
        print("\n✅ 成功！")
        return 0

    # 打印 init.log 关键行
    dir_path = diag.get("log_dir")
    if dir_path:
        ip = Path(dir_path) / "init.log"
        if ip.exists():
            content = ip.read_text(encoding="gbk", errors="ignore")
            for line in content.splitlines():
                if any(k in line for k in ["sanguo", "gpi.o", "map_init", "AfterRun", "Render", "读取地图", "设置读取"]):
                    print(f"  LOG: {line.strip()}")
    return 1 if not diag.get("ok") else 0

if __name__ == "__main__":
    sys.exit(main())
