# -*- coding: utf-8 -*-
exe = open(r'E:\玩家原创\神龙地图启动器\data\core\game.exe', 'rb').read()
pipe_str = b'\\\\.\\pipe\\'
idx = exe.find(pipe_str)
print('Found at', idx)
start = max(0, idx - 200)
end = min(len(exe), idx + 500)
data = exe[start:end]
result = ''
for b in data:
    if 32 <= b < 127:
        result += chr(b)
    else:
        if len(result) > 3:
            print(result)
        result = ''
if len(result) > 3:
    print(result)
