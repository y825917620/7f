import pathlib
import re

def get_latest_log(base_dir):
    d = pathlib.Path(base_dir)
    logs = [x for x in d.glob('log*') if x.is_dir()]
    if not logs: return None
    return max(logs, key=lambda x: x.stat().st_mtime) / "init.log"

def clean_line(line):
    # 移除 PID, 时间戳, 内存地址等干扰项
    line = re.sub(r'pid \d+', 'pid [PID]', line)
    line = re.sub(r'PID:\d+', 'PID:[PID]', line)
    line = re.sub(r'time="\d+"', 'time="[TIME]"', line)
    line = re.sub(r'0x[0-9A-Fa-f]+', '[ADDR]', line)
    return line.strip()

orig_path = get_latest_log(r'E:\玩家原创\神龙地图启动器\data')
new_path = get_latest_log(r'E:\玩家原创\神龙地图启动器5.2\data')

print(f"Comparing:\n  {orig_path}\n  {new_path}\n")

orig_lines = orig_path.read_text('gbk', 'ignore').splitlines()
new_lines = new_path.read_text('gbk', 'ignore').splitlines()

for i in range(min(len(orig_lines), len(new_lines))):
    c1 = clean_line(orig_lines[i])
    c2 = clean_line(new_lines[i])
    
    if c1 != c2:
        print(f"--- FIRST DIFF AT LINE {i+1} ---")
        print(f"ORIG: {orig_lines[i]}")
        print(f"NEW : {new_lines[i]}")
        
        print("\n--- NEXT 10 LINES ---")
        for j in range(i+1, min(i+11, len(orig_lines), len(new_lines))):
            print(f"L{j+1} ORIG: {orig_lines[j]}")
            print(f"L{j+1} NEW : {new_lines[j]}")
        break
else:
    print("No functional difference found in the overlap.")
