# -*- coding: utf-8 -*-
launcher = r'E:\玩家原创\神龙地图启动器\data\神龙地图启动器.exe'
with open(launcher, 'rb') as f:
    data = f.read()

keywords = [b'gpigame', b'SetWinHandle', b'SetHOOK', b'SetPID', b'HOOKMsgProc', b'LoadLibraryA', b'GetProcAddress']
for kw in keywords:
    count = data.count(kw)
    if count > 0:
        print(f'{kw!r}: count={count}')

if b'core/' in data:
    print('Found core/')
if b'core\\\\' in data:
    print('Found core\\\\')
