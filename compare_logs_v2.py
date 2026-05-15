import pathlib

def read_log(p):
    path = pathlib.Path(p) / "init.log"
    if not path.exists(): return []
    return path.read_text('gbk', 'ignore').splitlines()

orig = read_log(r'E:\玩家原创\神龙地图启动器\data\log34620-2026.05.15-01.33.44')
new = read_log(r'E:\玩家原创\神龙地图启动器5.2\data\log38900-2026.05.15-01.41.17')

def find_first_sanguo(lines):
    for i, l in enumerate(lines):
        if 'sanguo' in l: return i
    return -1

idx_orig = find_first_sanguo(orig)
idx_new = find_first_sanguo(new)

print(f"Original 'sanguo' index: {idx_orig}")
print(f"New 'sanguo' index:      {idx_new}")

if idx_orig != -1:
    print("\n--- Original Context ---")
    for i in range(max(0, idx_orig-10), min(len(orig), idx_orig+20)):
        print(f"L{i+1}: {orig[i]}")

if idx_new != -1:
    print("\n--- New Context ---")
    for i in range(max(0, idx_new-10), min(len(new), idx_new+20)):
        print(f"L{i+1}: {new[i]}")
