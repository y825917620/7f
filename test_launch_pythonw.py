import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.core.resource_control_service import ResourceControlService
from src.launcher.game_launcher import launch_game, diagnose_launch

GAME_DIR = Path(r"E:\玩家原创\神龙地图启动器\data")
MAP_ID = 10002

service = ResourceControlService(GAME_DIR)
manifest = service.prepare_launch_manifest(MAP_ID, [-1]*10+[0], 0)

bridge, diag = launch_game(manifest)
if bridge:
    pid = bridge.process_id
    time.sleep(12)
    result = diagnose_launch(GAME_DIR, pid, MAP_ID)
    out = Path(r"E:\玩家原创\神龙地图启动器5.2\launch_result.txt")
    out.write_text(
        f"PID={pid}\n"
        f"failure_kind={result.get('failure_kind')}\n"
        f"errors={result.get('errors', [])}\n"
        f"has_sanguo_o={result.get('has_sanguo_o')}\n"
        f"after_run_count={result.get('after_run_count')}\n"
        f"tab_interface_in_err={'tab_interface' in result.get('error_log_tail', '')}\n",
        encoding="utf-8"
    )
