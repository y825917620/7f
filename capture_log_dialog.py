# -*- coding: utf-8 -*-
"""捕获 LOG 对话框的内容."""

import ctypes
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Callback for EnumChildWindows
ENUM_CHILD_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

def get_window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def enum_child_texts(hwnd_parent):
    texts = []
    def callback(hwnd, _):
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        text = get_window_text(hwnd)
        if text:
            texts.append((cls.value, text))
        return True
    proc = ENUM_CHILD_PROC(callback)
    user32.EnumChildWindows(hwnd_parent, proc, 0)
    return texts


print("[INFO] 等待 LOG 对话框出现...")
for _ in range(60):
    hwnd = user32.FindWindowA(b"#32770", b"LOG")
    if hwnd:
        print(f"[FOUND] LOG dialog handle={hwnd}")
        print(f"[TITLE] {get_window_text(hwnd)}")
        children = enum_child_texts(hwnd)
        for cls, text in children:
            print(f"  [{cls}] {text}")
        print("[INFO] 对话框内容已打印，现在关闭它")
        user32.PostMessageA(hwnd, 0x10, 0, 0)
        break
    time.sleep(0.5)
else:
    print("[INFO] 未找到 LOG 对话框")
