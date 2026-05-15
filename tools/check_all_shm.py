import ctypes, time
from ctypes import wintypes
def check():
    kernel32 = ctypes.windll.kernel32
    NAMES = [
        b"7fgame_game_client_start_info",
        b"7fgame_game_client_login",
        b"7fgame_gameinfo",
        b"7fxx_dgtm"
    ]
    SHM_SIZE = 512
    print("Monitoring all 7f* SHM objects...")
    captured = set()
    while True:
        for name in NAMES:
            hMap = kernel32.OpenFileMappingA(0x0004, False, name)
            if hMap:
                if name not in captured:
                    ptr = kernel32.MapViewOfFile(hMap, 0x0004, 0, 0, SHM_SIZE)
                    if ptr:
                        data = ctypes.string_at(ptr, SHM_SIZE)
                        print(f"\n[FOUND] {name.decode()}")
                        print(f"Data (hex): {data[:64].hex()}")
                        val = ctypes.c_uint32.from_address(ptr).value
                        print(f"Int at offset 0: {val}")
                        s_part = data.split(b"\x00")[0]
                        print("String at offset 0: " + str(s_part))
                        kernel32.UnmapViewOfFile(ptr)
                        captured.add(name)
                kernel32.CloseHandle(hMap)
        time.sleep(0.1)
if __name__ == "__main__":
    check()
