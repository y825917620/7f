import ctypes, time
from ctypes import wintypes
def check():
    kernel32 = ctypes.windll.kernel32
    SHM_NAME = b"7fgame_game_client_start_info"
    SHM_SIZE = 512
    print(f"Monitoring {SHM_NAME.decode()}...")
    while True:
        hMap = kernel32.OpenFileMappingA(0x0004, False, SHM_NAME)
        if hMap:
            ptr = kernel32.MapViewOfFile(hMap, 0x0004, 0, 0, SHM_SIZE)
            if ptr:
                data = ctypes.string_at(ptr, SHM_SIZE)
                print(f"Found SHM! Data (hex): {data[:64].hex()}")
                val = ctypes.c_uint32.from_address(ptr).value
                print(f"Integer at offset 0: {val}")
                # Use a safer way to print string without backslash in f-string
                s_part = data.split(b"\x00")[0]
                print("String at offset 0: " + str(s_part))
                kernel32.UnmapViewOfFile(ptr)
            kernel32.CloseHandle(hMap)
            break
        time.sleep(0.1)
if __name__ == "__main__":
    check()
