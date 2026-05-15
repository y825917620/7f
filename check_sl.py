import os, time, pathlib
def check():
    path = pathlib.Path(r"E:\玩家原创\神龙地图启动器\data\sl\map.map")
    while True:
        if path.exists():
            data = path.read_bytes()
            print(f"Found sl/map.map! Size: {len(data)}")
            print(f"Header: {data[:10]}")
            break
        time.sleep(0.1)
if __name__ == "__main__":
    check()
