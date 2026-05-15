# -*- coding: utf-8 -*-
"""赞助/推广组件"""

import webbrowser
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QScrollArea, QWidget, QRadioButton,
    QButtonGroup, QLineEdit, QCheckBox, QComboBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import urllib.request


SPONSOR_URLS = {
    "官网": "http://www.7f555.com/",
    "QQ联系": "http://www.7f555.com/qq123.html",
    "排行榜": "http://sl0.70games.com/00/index.php/r144",
    "版本更新": "http://sl0.70games.com/00/release_info.html",
    "直播": "http://sl0.70games.com/00/index.php/live",
}

QQ_GROUP = "736895281"

VIP_PRODUCTS = [
    {"name": "星雨阁2", "permanent": 800, "monthly": 80},
    {"name": "真三国乱舞", "permanent": 500, "monthly": 50},
    {"name": "黑暗三国", "permanent": 300, "monthly": 30},
    {"name": "神魔英雄传", "permanent": 300, "monthly": 30},
    {"name": "星雨阁1", "permanent": 300, "monthly": 30},
    {"name": "三国英魂", "permanent": 300, "monthly": 30},
]


class VersionCheckThread(QThread):
    """版本检查后台线程"""
    result = pyqtSignal(bool, str)

    def run(self):
        try:
            req = urllib.request.Request(
                SPONSOR_URLS["版本更新"],
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=5
            )
            with urllib.request.urlopen(req) as resp:
                data = resp.read().decode("utf-8", errors="replace")
            self.result.emit(True, data[:200])
        except Exception as e:
            self.result.emit(False, str(e))


class SponsorSettingsDialog(QDialog):
    """赞助/VIP 设置对话框"""

    def __init__(self, parent=None, current_vip=None):
        super().__init__(parent)
        self.setWindowTitle("赞助大使设置")
        self.setMinimumSize(500, 600)
        self.current_vip = current_vip or {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 说明文本
        info = QLabel(
            "<p style='color:red; font-weight:bold;'>"
            "购买的赞助大使，启动地图后自动生效"
            "</p>"
            "<p>请直接勾选要启用的赞助项目：</p>"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # 账号输入（兼容原界面）
        account_group = QGroupBox("账号信息（可选）")
        acct_layout = QGridLayout(account_group)
        acct_layout.addWidget(QLabel("账号:"), 0, 0)
        self.account_input = QLineEdit()
        acct_layout.addWidget(self.account_input, 0, 1)
        acct_layout.addWidget(QLabel("确认账号:"), 1, 0)
        self.account_confirm = QLineEdit()
        acct_layout.addWidget(self.account_confirm, 1, 1)
        layout.addWidget(account_group)

        # VIP 商品列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.vip_groups = {}
        for prod in VIP_PRODUCTS:
            group = QGroupBox(prod["name"])
            g_layout = QVBoxLayout(group)

            # 单选按钮组
            btn_group = QButtonGroup(self)
            btn_group.setExclusive(True)

            rb_none = QRadioButton("不启用")
            rb_perm = QRadioButton(f"永久 ({prod['permanent']}元)")
            rb_month = QRadioButton(f"月卡 ({prod['monthly']}元)")

            btn_group.addButton(rb_none, 0)
            btn_group.addButton(rb_perm, 1)
            btn_group.addButton(rb_month, 2)

            g_layout.addWidget(rb_none)
            g_layout.addWidget(rb_perm)
            g_layout.addWidget(rb_month)

            # 默认选中
            current = self.current_vip.get(prod["name"], 0)
            if current == 1:
                rb_perm.setChecked(True)
            elif current == 2:
                rb_month.setChecked(True)
            else:
                rb_none.setChecked(True)

            self.vip_groups[prod["name"]] = btn_group
            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 保存按钮
        pay_layout = QHBoxLayout()
        pay_layout.addStretch()
        btn_save = QPushButton("保存设置")
        btn_save.setStyleSheet("font-size: 14px; padding: 8px 20px;")
        btn_save.clicked.connect(self.accept)
        pay_layout.addWidget(btn_save)
        layout.addLayout(pay_layout)

    def get_vip_settings(self):
        """返回当前VIP设置 dict {name: 0/1/2}"""
        result = {}
        for name, btn_group in self.vip_groups.items():
            result[name] = btn_group.checkedId()
        return result
