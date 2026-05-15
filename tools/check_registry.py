# -*- coding: utf-8 -*-
import winreg

def enum_keys(key_path, hive=winreg.HKEY_CURRENT_USER):
    try:
        with winreg.OpenKey(hive, key_path) as key:
            i = 0
            while True:
                try:
                    name = winreg.EnumKey(key, i)
                    print(f'  {name}')
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass

print('HKCU\\Software:')
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software') as key:
    for i in range(100):
        try:
            name = winreg.EnumKey(key, i)
            if '7f' in name.lower() or 'game' in name.lower() or 'dragon' in name.lower() or '神龙' in name:
                print(f'  {name}')
        except OSError:
            break

print('\nHKLM\\Software:')
with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software') as key:
    for i in range(100):
        try:
            name = winreg.EnumKey(key, i)
            if '7f' in name.lower() or 'game' in name.lower() or 'dragon' in name.lower() or '神龙' in name:
                print(f'  {name}')
        except OSError:
            break
