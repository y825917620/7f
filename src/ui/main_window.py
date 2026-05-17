# -*- coding: utf-8 -*-
"""神龙地图启动器 — 局域网联机版 UI"""

import sys
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QGroupBox, QLineEdit,
    QMessageBox, QStatusBar, QFileDialog, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGridLayout, QRadioButton, QButtonGroup, QFrame,
    QPlainTextEdit, QSpinBox,
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QPixmap

from ..data.map_data import MAP_CATEGORIES, MAP_INFO, RESOLUTION_OPTIONS
from ..core.map_parser import MapOptionParser
from ..launcher.game_launcher import launch_game
from ..launcher.host_service import HostService

# ─── 暗色终端工业风 ───
CSS = """
QMainWindow, QDialog { background: #0d1117; color: #c9d1d9; }
QWidget { font-family: "Microsoft YaHei", "Consolas", monospace; font-size: 13px; }
QGroupBox { border: 1px solid #21262d; border-radius: 4px; margin-top: 14px; padding: 12px; font-weight: bold; color: #58a6ff; background: #0d1117; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; color: #58a6ff; }
QPushButton { background: #161b22; color: #8b949e; border: 1px solid #30363d; border-radius: 4px; padding: 6px 16px; }
QPushButton:hover { background: #1c2128; border-color: #58a6ff; color: #c9d1d9; }
QPushButton:checked { background: #13233a; color: #58a6ff; border: 2px solid #1f6feb; }
QPushButton#launchBtn { background: #1a3a1a; color: #3fb950; border: 1px solid #2d5a2d; padding: 12px 40px; font-size: 16px; font-weight: bold; }
QPushButton#launchBtn:hover { background: #1f4a1f; }
QPushButton#launchBtn:disabled { background: #161b22; color: #3a3a3a; border-color: #21262d; }
QPushButton#createBtn { background: #1a2a3a; color: #58a6ff; border: 1px solid #1f6feb; }
QPushButton#joinBtn { background: #1a3a2a; color: #3fb950; border: 1px solid #238636; }
QComboBox, QSpinBox { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 3px; padding: 4px 8px; }
QComboBox:hover, QSpinBox:hover { border-color: #1f6feb; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background: #161b22; color: #c9d1d9; selection-background-color: #13233a; border: 1px solid #30363d; }
QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 3px; padding: 5px 8px; }
QLineEdit:focus { border-color: #1f6feb; }
QLineEdit:disabled { background: #060a10; color: #484f58; }
QTableWidget { background: #0d1117; gridline-color: #161b22; border: 1px solid #21262d; selection-background-color: #13233a; color: #c9d1d9; }
QTableWidget::item { padding: 3px 8px; }
QTableWidget::item:selected { background: #1f3a5f; color: #e6edf3; }
QHeaderView::section { background: #161b22; color: #58a6ff; border: none; padding: 6px; font-weight: bold; font-size: 11px; }
QStatusBar { background: #060a10; color: #484f58; border-top: 1px solid #161b22; }
QFrame#sep { background: #21262d; max-height: 1px; }
QPlainTextEdit { background: #0d1117; color: #8b949e; border: 1px solid #21262d; font-family: "Consolas", "Courier New", monospace; font-size: 11px; }
QScrollBar:vertical { background: #0d1117; width: 6px; }
QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QLabel#statusLabel { color: #58a6ff; font-size: 14px; font-weight: bold; padding: 8px; border: 1px solid #1f3a5f; border-radius: 4px; background: #0d1520; }
QLabel#roomLabel { color: #3fb950; font-size: 12px; }
"""


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("神龙地图启动器 — LAN")
        self.setMinimumSize(1000, 650)

        # 状态
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            self.game_dir = exe_dir if (exe_dir / "map").exists() else exe_dir / "data"
        else:
            self.game_dir = Path(__file__).parent.parent.parent / "data"

        self.selected_map = None
        self._parsed_map_options = []
        self._parsed_player_num = 1
        self._opt_widgets = []

        # 房间系统
        self._room_mode = "single"  # single | host | client
        self._host_service = None
        self._room_host_ip = "127.0.0.1"

        self._setup_ui()
        self._load_map_list("全部地图")
        self._status("READY")

    # ═══ UI ═══

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(6, 6, 6, 0)
        root.setSpacing(6)

        # ── 左侧 ──
        left = QVBoxLayout(); left.setSpacing(4)

        # 分类
        cat_row = QHBoxLayout()
        self._cat_group = QButtonGroup(self); self._cat_group.setExclusive(True)
        for i, cat in enumerate(MAP_CATEGORIES[:5]):
            btn = QPushButton(cat); btn.setCheckable(True); btn.setChecked(i == 0)
            btn.clicked.connect(lambda _, c=cat: self._load_map_list(c))
            self._cat_group.addButton(btn); cat_row.addWidget(btn)
        left.addLayout(cat_row)

        # 搜索 + 目录
        sr = QHBoxLayout()
        self._search = QLineEdit(); self._search.setPlaceholderText("搜索...")
        self._search.textChanged.connect(self._filter_maps); sr.addWidget(self._search)
        b = QPushButton("DIR"); b.clicked.connect(self._choose_game_dir); sr.addWidget(b)
        left.addLayout(sr)
        self._dir_label = QLabel(str(self.game_dir)); self._dir_label.setStyleSheet("color:#484f58;font-size:10px;"); left.addWidget(self._dir_label)

        # 地图表格 — 只有2列（名称 + 作者）
        self._map_table = QTableWidget()
        self._map_table.setColumnCount(2)
        self._map_table.setHorizontalHeaderLabels(["地图名称", "作者"])
        self._map_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._map_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._map_table.setColumnWidth(1, 90)
        self._map_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._map_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._map_table.itemSelectionChanged.connect(self._on_map_selected)
        self._map_table.verticalHeader().setVisible(False)
        left.addWidget(self._map_table, 1)
        root.addLayout(left, 3)

        # ── 分隔 ──
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine); sep.setStyleSheet("background:#161b22;max-width:1px;"); root.addWidget(sep)

        # ── 右侧 ──
        right = QVBoxLayout(); right.setSpacing(6)

        # 房间系统
        room_gb = QGroupBox("房间模式")
        room_l = QVBoxLayout(room_gb)

        self._mode_group = QButtonGroup(self); self._current_mode = "single"
        mr = QHBoxLayout()
        modes = [("single", "单机"), ("host", "创建房间"), ("client", "加入房间")]
        for mid, mlabel in modes:
            btn = QPushButton(mlabel); btn.setCheckable(True); btn.setChecked(mid == "single")
            btn.setObjectName("createBtn" if mid == "host" else ("joinBtn" if mid == "client" else ""))
            btn.clicked.connect(lambda _, m=mid: self._on_mode_changed(m))
            self._mode_group.addButton(btn); mr.addWidget(btn)
        room_l.addLayout(mr)

        # LAN 设置行
        self._lan_row = QHBoxLayout()
        self._lan_row.addWidget(QLabel("房间IP"))
        self._host_ip = QLineEdit("127.0.0.1"); self._host_ip.setMaximumWidth(130); self._host_ip.setEnabled(False)
        self._lan_row.addWidget(self._host_ip)
        self._lan_row.addWidget(QLabel("端口"))
        self._host_port = QLineEdit("29002"); self._host_port.setMaximumWidth(60); self._host_port.setEnabled(False)
        self._lan_row.addWidget(self._host_port)
        self._lan_row.addWidget(QLabel("玩家名"))
        self._player_name = QLineEdit("Player1"); self._player_name.setMaximumWidth(100)
        self._lan_row.addWidget(self._player_name)
        self._lan_row.addWidget(QLabel("槽位"))
        self._player_slot = QSpinBox(); self._player_slot.setRange(1, 24); self._player_slot.setValue(1); self._player_slot.setMaximumWidth(55)
        self._lan_row.addWidget(self._player_slot)
        self._lan_row.addStretch()
        room_l.addLayout(self._lan_row)

        # 房间状态
        self._room_status = QLabel("单机模式 — 地图设置由本地控制")
        self._room_status.setObjectName("roomLabel"); room_l.addWidget(self._room_status)
        right.addWidget(room_gb)

        # 地图详情
        info_gb = QGroupBox("地图详情")
        il = QHBoxLayout(info_gb)
        self._thumb = QLabel(); self._thumb.setFixedSize(80, 80); self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb.setStyleSheet("border:1px solid #21262d; background:#060a10; color:#30363d;"); self._thumb.setText("N/A")
        il.addWidget(self._thumb)
        self._info_text = QLabel("选择地图"); self._info_text.setWordWrap(True); self._info_text.setStyleSheet("color:#8b949e;font-size:12px;")
        il.addWidget(self._info_text, 1)
        right.addWidget(info_gb)

        # 选项
        opt_gb = QGroupBox("游戏选项"); self._opt_grid = QGridLayout(); opt_gb.setLayout(self._opt_grid); right.addWidget(opt_gb)

        # 分辨率 + 玩家
        br = QHBoxLayout()
        br.addWidget(QLabel("分辨率")); self._res_combo = QComboBox()
        for name, _, _ in RESOLUTION_OPTIONS: self._res_combo.addItem(name)
        br.addWidget(self._res_combo); br.addStretch()
        br.addWidget(QLabel("总玩家")); self._player_num_combo = QComboBox(); br.addWidget(self._player_num_combo)
        right.addLayout(br)

        right.addStretch()

        # 启动按钮（主机/单机可用，客户端加入后锁定）
        lr = QHBoxLayout(); lr.addStretch()
        self._launch_btn = QPushButton("启动游戏")
        self._launch_btn.setObjectName("launchBtn"); self._launch_btn.setEnabled(False)
        self._launch_btn.setMinimumHeight(48); self._launch_btn.clicked.connect(self._launch_game)
        lr.addWidget(self._launch_btn); lr.addStretch()
        right.addLayout(lr)
        root.addLayout(right, 2)

        self._statusbar = QStatusBar(); self.setStatusBar(self._statusbar)

    # ═══ 逻辑 ═══

    def _status(self, msg): self._statusbar.showMessage(msg)

    def _on_mode_changed(self, mode):
        self._current_mode = mode
        is_client = mode == "client"
        is_host = mode == "host"
        self._host_ip.setEnabled(is_client)
        self._host_port.setEnabled(is_client)
        self._launch_btn.setEnabled(not is_client)  # client can't launch
        if is_host:
            self._room_status.setText("创建房间模式 — 由你选择地图和设置，他人可加入")
        elif is_client:
            self._room_status.setText(f"客户端模式 — 加入 {self._host_ip.text()}:{self._host_port.text()} 后等待主机启动")
        else:
            self._room_status.setText("单机模式 — 地图设置由本地控制")

    def _load_map_list(self, category="全部地图"):
        self._map_table.setRowCount(0); self._all_map_ids = []
        for mid in sorted(MAP_INFO.keys()):
            if category != "全部地图" and MAP_INFO[mid].get("category") != category: continue
            self._all_map_ids.append(mid)
        self._fill_table(self._all_map_ids)

    def _filter_maps(self, text):
        if not text: self._fill_table(self._all_map_ids); return
        self._fill_table([mid for mid in self._all_map_ids if text.lower() in MAP_INFO.get(mid, {}).get("name", "").lower()])

    def _fill_table(self, ids):
        self._map_table.setRowCount(0)
        for row, mid in enumerate(ids):
            self._map_table.insertRow(row)
            info = MAP_INFO[mid]
            item = QTableWidgetItem(info["name"]); item.setData(Qt.ItemDataRole.UserRole, mid)
            self._map_table.setItem(row, 0, item)
            self._map_table.setItem(row, 1, QTableWidgetItem(info.get("author", "")))

    def _on_map_selected(self):
        sel = self._map_table.selectedItems()
        if not sel: return
        mid = self._map_table.item(sel[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        self.selected_map = mid
        self._launch_btn.setEnabled(self._current_mode != "client")

        map_path = self.game_dir / "map" / f"{mid}.map"
        parsed = MapOptionParser.parse(map_path)
        game_opts = MapOptionParser.get_game_options(parsed) if parsed else []
        self._parsed_map_options = game_opts
        self._parsed_player_num = parsed["player_num"] if parsed else 1

        # 缩略图
        thumb = MapOptionParser.extract_thumbnail(map_path)
        if thumb:
            pix = QPixmap(); pix.loadFromData(thumb, "BMP")
            if not pix.isNull(): self._thumb.setPixmap(pix.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
            else: self._thumb.setText("ERR")
        else: self._thumb.setText("N/A")

        # 信息
        parts = [f"ID: {mid}"]
        if MAP_INFO.get(mid, {}).get("name"): parts.append(MAP_INFO[mid]["name"])
        if parsed and parsed.get("chn_name"): parts.append(parsed["chn_name"])
        if parsed and parsed.get("info"): parts.append(parsed["info"])
        self._info_text.setText("\n".join(parts))

        # 重建选项 — 每个地图独立生成
        while self._opt_grid.count():
            w = self._opt_grid.takeAt(0)
            if w.widget(): w.widget().deleteLater()
        self._opt_widgets = []
        for i, opt in enumerate(game_opts[:10]):
            r, c = divmod(i, 2)
            lbl = QLabel(f"{opt['name']}:"); cmb = QComboBox()
            for vi, vname in enumerate(opt["values"]):
                try: av = int(vname)
                except ValueError: av = vi
                cmb.addItem(vname, av)
            cmb.setCurrentIndex(opt["default_index"])
            self._opt_grid.addWidget(lbl, r, c*2); self._opt_grid.addWidget(cmb, r, c*2+1)
            self._opt_widgets.append(cmb)

        self._player_num_combo.clear()
        for i in range(1, self._parsed_player_num + 1): self._player_num_combo.addItem(f"玩家{i}", i-1)

        self._status(f"{MAP_INFO.get(mid, {}).get('name', mid)} ({mid})")

    def _choose_game_dir(self):
        p = QFileDialog.getExistingDirectory(self, "选择游戏目录", str(self.game_dir))
        if p: self.game_dir = Path(p); self._dir_label.setText(str(self.game_dir))

    def _get_options_from_ui(self):
        opts = []
        for cmb in getattr(self, "_opt_widgets", [])[:10]:
            d = cmb.currentData(); opts.append(d if d is not None else -1)
        while len(opts) < 10: opts.append(-1)
        opts.append(self._player_num_combo.currentData() or 0)
        return opts

    def _launch_game(self):
        if not self.selected_map: return
        mid = int(self.selected_map)
        gd = Path(self.game_dir).absolute()
        if not (gd / "core" / "game.exe").exists() and not (gd / "game.exe").exists():
            QMessageBox.critical(self, "启动错误", f"找不到 game.exe"); return

        options = self._get_options_from_ui()
        mode = getattr(self, "_current_mode", "single")

        try:
            bridge, msg = launch_game(gd, mid, options, self._res_combo.currentIndex(),
                mode=mode, host_ip=self._host_ip.text().strip() or "127.0.0.1",
                host_port=int(self._host_port.text().strip() or "29002"),
                player_name=self._player_name.text().strip() or "Player1",
                player_slot=self._player_slot.value())
            if bridge:
                nm = MAP_INFO.get(mid, {}).get("name", mid)
                self._status(f"PID={bridge.process_id} | {nm}")
            else:
                self._show_err("启动失败", msg)
        except Exception as e:
            import traceback; self._show_err("异常", f"{e}\n\n{traceback.format_exc()}")

    def _show_err(self, title, msg):
        dlg = QDialog(self); dlg.setWindowTitle(title); dlg.setMinimumSize(500, 300)
        l = QVBoxLayout(dlg); l.addWidget(QLabel(f"<b style='color:#f85149;'>{title}</b>"))
        t = QPlainTextEdit(); t.setReadOnly(True); t.setPlainText(msg); l.addWidget(t)
        b = QPushButton("确定"); b.clicked.connect(dlg.accept); l.addWidget(b); dlg.exec()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft YaHei", 10))
    app.setStyleSheet(CSS)
    LauncherWindow().show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
