# -*- coding: utf-8 -*-
"""神龙地图启动器 — 局域网联机版 UI"""

import sys
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QGroupBox, QLineEdit,
    QMessageBox, QStatusBar, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QGridLayout, QRadioButton, QButtonGroup, QFrame,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap

from ..data.map_data import MAP_CATEGORIES, MAP_INFO, RESOLUTION_OPTIONS
from ..core.map_parser import MapOptionParser
from ..launcher.game_launcher import launch_game

# ─── 暗色工业风调色板 ───
CSS = """
/* 全局 */
QMainWindow, QDialog {
    background-color: #121418;
    color: #bcc4cc;
}
QWidget {
    font-family: "Microsoft YaHei", "Consolas", monospace;
    font-size: 13px;
}

/* 分组框 */
QGroupBox {
    border: 1px solid #2a2e34;
    border-radius: 4px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: bold;
    color: #6a9fd8;
    background: #181c20;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #6a9fd8;
}

/* 按钮 — 主按钮 */
QPushButton#launchBtn {
    background: #1a5c2a;
    color: #4ae04a;
    border: 1px solid #2a8a3a;
    border-radius: 4px;
    padding: 12px 40px;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
}
QPushButton#launchBtn:hover {
    background: #1e7032;
    border-color: #3ab04a;
}
QPushButton#launchBtn:disabled {
    background: #1a1e22;
    color: #3a3a3a;
    border-color: #2a2e34;
}

/* 普通按钮 */
QPushButton {
    background: #1a1e24;
    color: #8899aa;
    border: 1px solid #2a2e34;
    border-radius: 3px;
    padding: 6px 16px;
}
QPushButton:hover {
    background: #222830;
    border-color: #4a6a8a;
}
QPushButton:checked {
    background: #1a2e3e;
    color: #6a9fd8;
    border-color: #3a6080;
}

/* 模式选择按钮 */
QPushButton#modeBtn {
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
}
QPushButton#modeBtn:checked {
    background: #1a3040;
    color: #60c0ff;
    border: 2px solid #4090d0;
}

/* ComboBox */
QComboBox {
    background: #1a1e24;
    color: #bcc4cc;
    border: 1px solid #2a2e34;
    border-radius: 3px;
    padding: 4px 8px;
}
QComboBox:hover { border-color: #3a4a5a; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #181c20;
    color: #bcc4cc;
    selection-background-color: #1a3a50;
    border: 1px solid #2a2e34;
}

/* LineEdit */
QLineEdit {
    background: #1a1e24;
    color: #dde4ec;
    border: 1px solid #2a2e34;
    border-radius: 3px;
    padding: 4px 8px;
}
QLineEdit:focus { border-color: #4090d0; }

/* 表格 */
QTableWidget {
    background: #14181c;
    gridline-color: #1e2228;
    border: 1px solid #2a2e34;
    selection-background-color: #1a3040;
    color: #bcc4cc;
}
QTableWidget::item { padding: 4px 8px; }
QTableWidget::item:selected { background: #1a3a50; color: #eef4fa; }
QHeaderView::section {
    background: #181c20;
    color: #6a9fd8;
    border: none;
    padding: 6px 8px;
    font-weight: bold;
    font-size: 11px;
    letter-spacing: 1px;
}

/* StatusBar */
QStatusBar {
    background: #0e1014;
    color: #5a6a7a;
    border-top: 1px solid #1e2228;
}

/* 分隔线 */
QFrame#sep {
    background: #2a2e34;
    max-height: 1px;
}

/* 滚动条 */
QScrollBar:vertical {
    background: #121418;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #2a3040;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("神龙地图启动器 — LAN")
        self.setMinimumSize(960, 640)

        # 状态
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            if (exe_dir / "map").exists() and (exe_dir / "core").exists():
                self.game_dir = exe_dir
            else:
                self.game_dir = exe_dir / "data"
        else:
            self.game_dir = Path(__file__).parent.parent.parent / "data"

        self.selected_map = None
        self._parsed_map_options = []
        self._parsed_player_num = 1

        self._setup_ui()
        self._load_map_list("全部地图")
        self._status("READY — 选择地图并启动")

    # ═══════════════════════════════════════════
    # UI 构建
    # ═══════════════════════════════════════════

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 0)
        root.setSpacing(8)

        # ── 左侧: 地图列表 ──
        left = QVBoxLayout()
        left.setSpacing(6)

        # 分类选择
        cat_row = QHBoxLayout()
        self._cat_group = QButtonGroup(self)
        self._cat_group.setExclusive(True)
        for i, cat in enumerate(MAP_CATEGORIES[:6]):
            btn = QPushButton(cat)
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.clicked.connect(lambda checked, c=cat: self._load_map_list(c))
            self._cat_group.addButton(btn)
            cat_row.addWidget(btn)
        left.addLayout(cat_row)

        # 搜索栏
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("搜索地图名...")
        self._search.textChanged.connect(self._filter_maps)
        search_row.addWidget(self._search)

        # 游戏目录
        self._dir_label = QLabel(str(self.game_dir))
        self._dir_label.setStyleSheet("color: #4a6a7a; font-size: 10px;")
        btn_browse = QPushButton("DIR")
        btn_browse.clicked.connect(self._choose_game_dir)
        search_row.addWidget(btn_browse)
        left.addLayout(search_row)
        left.addWidget(self._dir_label)

        # 地图表格
        self._map_table = QTableWidget()
        self._map_table.setColumnCount(3)
        self._map_table.setHorizontalHeaderLabels(["地图", "作者", "热度"])
        self._map_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._map_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._map_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._map_table.setColumnWidth(1, 80)
        self._map_table.setColumnWidth(2, 60)
        self._map_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._map_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._map_table.itemSelectionChanged.connect(self._on_map_selected)
        self._map_table.verticalHeader().setVisible(False)
        left.addWidget(self._map_table, 1)

        root.addLayout(left, 3)

        # ── 分隔线 ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background: #1e2228; max-width: 1px;")
        root.addWidget(sep)

        # ── 右侧: 模式 + 选项 + 启动 ──
        right = QVBoxLayout()
        right.setSpacing(8)

        # 模式选择
        mode_gb = QGroupBox("网络模式")
        mode_layout = QVBoxLayout(mode_gb)

        self._mode_group = QButtonGroup(self)
        mode_row = QHBoxLayout()
        modes = [
            ("single", "单机本地"),
            ("host", "局域网主机"),
            ("client", "局域网客户端"),
        ]
        for i, (mode_id, label) in enumerate(modes):
            btn = QPushButton(label)
            btn.setObjectName("modeBtn")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.clicked.connect(lambda checked, m=mode_id: self._on_mode_changed(m))
            self._mode_group.addButton(btn)
            mode_row.addWidget(btn)
        mode_layout.addLayout(mode_row)

        # LAN 设置行
        lan_row = QHBoxLayout()
        lan_row.addWidget(QLabel("主机IP"))
        self._host_ip = QLineEdit("127.0.0.1")
        self._host_ip.setMaximumWidth(140)
        self._host_ip.setEnabled(False)
        lan_row.addWidget(self._host_ip)

        lan_row.addWidget(QLabel("端口"))
        self._host_port = QLineEdit("29002")
        self._host_port.setMaximumWidth(70)
        self._host_port.setEnabled(False)
        lan_row.addWidget(self._host_port)

        lan_row.addWidget(QLabel("玩家名"))
        self._player_name = QLineEdit("Player1")
        self._player_name.setMaximumWidth(120)
        lan_row.addWidget(self._player_name)

        lan_row.addWidget(QLabel("槽位"))
        self._player_slot = QComboBox()
        for i in range(1, 25):
            self._player_slot.addItem(str(i), i)
        self._player_slot.setMaximumWidth(60)
        lan_row.addWidget(self._player_slot)
        lan_row.addStretch()
        mode_layout.addLayout(lan_row)
        right.addWidget(mode_gb)

        # 地图预览 + 信息
        info_gb = QGroupBox("地图详情")
        info_layout = QHBoxLayout(info_gb)
        self._thumb = QLabel()
        self._thumb.setFixedSize(100, 100)
        self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb.setStyleSheet("border: 1px solid #20242a; background: #101418; color: #3a4a5a;")
        self._thumb.setText("N/A")
        info_layout.addWidget(self._thumb)

        self._info_text = QLabel("选择地图")
        self._info_text.setWordWrap(True)
        self._info_text.setStyleSheet("color: #6a7a8a; font-size: 12px;")
        info_layout.addWidget(self._info_text, 1)
        right.addWidget(info_gb)

        # 选项区
        opt_gb = QGroupBox("游戏选项")
        self._opt_grid = QGridLayout()
        opt_gb.setLayout(self._opt_grid)
        right.addWidget(opt_gb)

        # 分辨率
        res_row = QHBoxLayout()
        res_row.addWidget(QLabel("分辨率"))
        self._res_combo = QComboBox()
        for name, _, _ in RESOLUTION_OPTIONS:
            self._res_combo.addItem(name)
        res_row.addWidget(self._res_combo)
        res_row.addStretch()

        # 玩家数
        res_row.addWidget(QLabel("玩家"))
        self._player_num_combo = QComboBox()
        self._player_num_combo.currentIndexChanged.connect(self._on_player_changed)
        res_row.addWidget(self._player_num_combo)
        right.addLayout(res_row)

        right.addStretch()

        # 启动按钮
        launch_row = QHBoxLayout()
        launch_row.addStretch()
        self._launch_btn = QPushButton("启动游戏")
        self._launch_btn.setObjectName("launchBtn")
        self._launch_btn.setEnabled(False)
        self._launch_btn.clicked.connect(self._launch_game)
        self._launch_btn.setMinimumHeight(48)
        launch_row.addWidget(self._launch_btn)
        launch_row.addStretch()
        right.addLayout(launch_row)

        root.addLayout(right, 2)

        # 状态栏
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

    # ═══════════════════════════════════════════
    # 逻辑
    # ═══════════════════════════════════════════

    def _status(self, msg: str):
        self._statusbar.showMessage(msg)

    def _on_mode_changed(self, mode: str):
        is_client = (mode == "client")
        self._host_ip.setEnabled(is_client)
        self._host_port.setEnabled(is_client)

    def _load_map_list(self, category="全部地图"):
        self._map_table.setRowCount(0)
        self._all_map_ids = []
        for map_id in sorted(MAP_INFO.keys()):
            info = MAP_INFO[map_id]
            if category != "全部地图" and info.get("category") != category:
                continue
            self._all_map_ids.append(map_id)
        self._fill_table(self._all_map_ids)

    def _filter_maps(self, text: str):
        if not text:
            self._fill_table(self._all_map_ids)
            return
        filtered = [mid for mid in self._all_map_ids
                    if text.lower() in MAP_INFO.get(mid, {}).get("name", "").lower()]
        self._fill_table(filtered)

    def _fill_table(self, ids):
        self._map_table.setRowCount(0)
        for row, map_id in enumerate(ids):
            self._map_table.insertRow(row)
            info = MAP_INFO[map_id]
            item = QTableWidgetItem(info["name"])
            item.setData(Qt.ItemDataRole.UserRole, map_id)
            self._map_table.setItem(row, 0, item)
            self._map_table.setItem(row, 1, QTableWidgetItem(info.get("author", "")))
            heat = QTableWidgetItem(str(info.get("heat", 0)))
            heat.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._map_table.setItem(row, 2, heat)

    def _on_map_selected(self):
        sel = self._map_table.selectedItems()
        if not sel:
            return
        row = sel[0].row()
        map_id = self._map_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.selected_map = map_id
        self._launch_btn.setEnabled(True)

        # 解析 .map
        map_path = self.game_dir / "map" / f"{map_id}.map"
        parsed = MapOptionParser.parse(map_path)
        game_opts = MapOptionParser.get_game_options(parsed) if parsed else []
        player_num = parsed["player_num"] if parsed else 1
        self._parsed_map_options = game_opts
        self._parsed_player_num = player_num

        # 缩略图
        thumb = MapOptionParser.extract_thumbnail(map_path)
        if thumb:
            pix = QPixmap()
            pix.loadFromData(thumb, "BMP")
            if not pix.isNull():
                self._thumb.setPixmap(pix.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self._thumb.setText("ERR")
        else:
            self._thumb.setText("N/A")

        # 信息
        parts = [f"ID: {map_id}"]
        if MAP_INFO.get(map_id, {}).get("name"):
            parts.append(f"名称: {MAP_INFO[map_id]['name']}")
        if parsed and parsed.get("chn_name"):
            parts.append(f"中文: {parsed['chn_name']}")
        if parsed and parsed.get("info"):
            parts.append(f"描述: {parsed['info']}")
        self._info_text.setText("\n".join(parts))

        # 重建选项
        while self._opt_grid.count():
            item = self._opt_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._opt_widgets = []
        for i, opt in enumerate(game_opts[:6]):
            r, c = divmod(i, 2)
            lbl = QLabel(f"{opt['name']}:")
            cmb = QComboBox()
            for idx, val in enumerate(opt["values"]):
                cmb.addItem(val, idx)
            cmb.setCurrentIndex(opt["default_index"])
            cmb.currentIndexChanged.connect(lambda idx, i=i: self._on_opt_changed(i))
            self._opt_grid.addWidget(lbl, r, c * 2)
            self._opt_grid.addWidget(cmb, r, c * 2 + 1)
            self._opt_widgets.append(cmb)

        # 玩家数
        self._player_num_combo.clear()
        for i in range(1, player_num + 1):
            self._player_num_combo.addItem(f"玩家{i}", i - 1)

        self._status(f"已选择: {MAP_INFO.get(map_id, {}).get('name', map_id)} ({map_id})")

    def _on_opt_changed(self, index: int):
        pass  # options stored in combo widgets directly

    def _on_player_changed(self, index: int):
        pass

    def _choose_game_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择游戏目录", str(self.game_dir))
        if path:
            self.game_dir = Path(path)
            self._dir_label.setText(str(self.game_dir))

    def _get_options_from_ui(self):
        opts = []
        for cmb in self._opt_widgets:
            opts.append(cmb.currentData() if cmb.currentData() is not None else -1)
        while len(opts) < 10:
            opts.append(-1)
        opts.append(self._player_num_combo.currentData() or 0)
        return opts

    def _launch_game(self):
        if not self.selected_map:
            return

        map_id = int(self.selected_map)
        game_dir = Path(self.game_dir).absolute()

        if not (game_dir / "core" / "game.exe").exists() and not (game_dir / "game.exe").exists():
            QMessageBox.critical(self, "启动错误", f"找不到 game.exe:\n{game_dir}")
            return

        options = self._get_options_from_ui()

        try:
            # 读取 LAN 设置
            mode_btn = self._mode_group.checkedButton()
            mode_map = {"单机本地": "single", "局域网主机": "host", "局域网客户端": "client"}
            mode = "single"
            for btn_text, mode_val in mode_map.items():
                if mode_btn and btn_text in mode_btn.text():
                    mode = mode_val

            bridge, msg = launch_game(
                game_dir, map_id, options,
                self._res_combo.currentIndex(),
                mode=mode,
                host_ip=self._host_ip.text().strip() or "127.0.0.1",
                host_port=int(self._host_port.text().strip() or "29002"),
                player_name=self._player_name.text().strip() or "Player1",
                player_slot=self._player_slot.currentData() or 1,
            )
            if bridge:
                self._status(f"PID={bridge.process_id} | {MAP_INFO.get(map_id, {}).get('name', map_id)}")
            else:
                self._show_err("启动失败", msg)
        except Exception as e:
            import traceback
            self._show_err("异常", f"{e}\n\n{traceback.format_exc()}")

    def _show_err(self, title: str, msg: str):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setMinimumSize(500, 300)
        dlg.setStyleSheet("background: #121418; color: #e04040;")
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(f"<b style='color:#e04040;'>{title}</b>"))
        from PyQt6.QtWidgets import QPlainTextEdit
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(msg)
        layout.addWidget(text)
        btn = QPushButton("确定")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft YaHei", 10))
    app.setStyleSheet(CSS)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
