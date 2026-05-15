import pathlib

def get_latest_log(base_dir):
    d = pathlib.Path(base_dir)
    logs = [x for x in d.glob('log*') if x.is_dir()]
    if not logs: return None
    return max(logs, key=lambda x: x.stat().st_mtime)

def read_log(p):
    if not p: return ""
    log_file = p / "init.log"
    if not log_file.exists(): return ""
    return log_file.read_text('gbk', 'ignore')

orig_dir = get_latest_log(r'E:\玩家原创\神龙地图启动器\data')
new_dir = get_latest_log(r'E:\玩家原创\神龙地图启动器5.2\data')

print(f"Original Log: {orig_dir}")
print(f"New Log:      {new_dir}")

orig_lines = read_log(orig_dir).splitlines()
new_lines = read_log(new_dir).splitlines()

max_lines = max(len(orig_lines), len(new_lines))
for i in range(max_lines):
    orig_l = orig_lines[i] if i < len(orig_lines) else "[[EOF]]"
    new_l = new_lines[i] if i < len(new_lines) else "[[EOF]]"
    
    # 过滤掉包含 PID 的行，因为 PID 每次都不同
    if "PID:" in orig_l and "PID:" in new_l:
        continue
    
    if orig_l != new_l:
        print(f"\n[DIFF at Line {i+1}]")
        print(f"ORIG: {orig_l}")
        print(f"NEW : {new_l}")
        
        # 打印接下来 5 行看看上下文
        print("--- Context ---")
        for j in range(i+1, min(i+6, max_lines)):
            ol = orig_lines[j] if j < len(orig_lines) else "[[EOF]]"
            nl = new_lines[j] if j < len(new_lines) else "[[EOF]]"
            print(f"L{j+1} ORIG: {ol}")
            print(f"L{j+1} NEW : {nl}")
        break
