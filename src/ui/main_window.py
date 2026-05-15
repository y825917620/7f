# -*- coding: utf-8 -*-
"""启动器主窗口"""

import sys
import time
import webbrowser
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTabWidget, QGroupBox, QGridLayout,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QFileDialog, QDialog,
    QRadioButton, QButtonGroup, QLineEdit, QTextBrowser, QCheckBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QPlainTextEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction

from ..data.map_data import (
    MAP_CATEGORIES, MAP_INFO, DEFAULT_MAP_OPTIONS,
    RESOLUTION_OPTIONS
)
from ..core.config_generator import generate_config_lua
from ..core.map_parser import MapOptionParser
from .sponsor_widgets import (
    SPONSOR_URLS, QQ_GROUP, VIP_PRODUCTS,
    VersionCheckThread, SponsorSettingsDialog,
)
from ..launcher.game_launcher import GameBridge, launch_game, diagnose_launch
from ..launcher.game_settings import update_game_setting
from ..launcher.log_verifier import LogVerifier


class LauncherWindow(QMainWindow):
    """启动器主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("神龙地图启动器 - www.7F555.com")
        self.setMinimumSize(1000, 700)

        # 内部状态
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            # 检测 exe 是否直接放在游戏目录里（包含 map/、core/ 等）
            if (exe_dir / "map").exists() and (exe_dir / "core").exists():
                self.game_dir = exe_dir
            else:
                # exe 在根目录，游戏文件在 data/ 子目录
                self.game_dir = exe_dir / "data"
        else:
            # 开发模式：从 src/ui/main_window.py 回溯到项目根目录，再找 data/
            self.game_dir = Path(__file__).parent.parent.parent / "data"

        self.selected_map = None
        self.current_options = {}
        self.vip_settings = {}
        self.g_map_display = 0
        self._launcher_mutex = None  # 互斥锁句柄，必须保持存活

        # 加载默认选项
        for k, v in DEFAULT_MAP_OPTIONS.items():
            self.current_options[k] = list(v)

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._load_map_list("全部地图")
        self._check_version()

    # =====================================================================
    # UI 构建
    # =====================================================================

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # 主分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ---- 左侧面板：分类 + 地图列表 ----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 分类按钮
        left_layout.addWidget(QLabel("<b>地图分类</b>"))
        cat_widget = QWidget()
        cat_layout = QVBoxLayout(cat_widget)
        cat_layout.setSpacing(4)
        cat_layout.setContentsMargins(0, 0, 0, 0)

        self.category_group = QButtonGroup(self)
        self.category_group.setExclusive(True)

        for cat in MAP_CATEGORIES:
            btn = QPushButton(cat)
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setStyleSheet(
                "QPushButton { text-align: left; padding: 5px 10px; border: 1px solid #ccc; }"
                "QPushButton:hover { background-color: #e0e0e0; }"
                "QPushButton:checked { background-color: #4CAF50; color: white; font-weight: bold; border: 1px solid #4CAF50; }"
            )
            self.category_group.addButton(btn)
            cat_layout.addWidget(btn)
            btn.clicked.connect(lambda checked, c=cat: self._load_map_list(c))

        # 默认选中"全部地图"
        self.category_group.buttons()[0].setChecked(True)
        cat_layout.addStretch()
        left_layout.addWidget(cat_widget)

        # 地图表格
        left_layout.addWidget(QLabel("<b>地图列表</b>"))
        self.map_table = QTableWidget()
        self.map_table.setColumnCount(4)
        self.map_table.setHorizontalHeaderLabels(["地图名字", "地图作者", "地图热度", "地图状态"])
        self.map_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.map_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.map_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.map_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.map_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.map_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.map_table.itemSelectionChanged.connect(self._on_map_selected)
        left_layout.addWidget(self.map_table, 1)

        # 游戏目录选择
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(f"目录: {self.game_dir}")
        self.dir_label.setWordWrap(True)
        btn_dir = QPushButton("浏览...")
        btn_dir.clicked.connect(self._choose_game_dir)
        dir_layout.addWidget(self.dir_label, 1)
        dir_layout.addWidget(btn_dir)
        left_layout.addLayout(dir_layout)

        splitter.addWidget(left_panel)

        # ---- 右侧面板：选项 + 赞助 + 关于 ----
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.tabs = QTabWidget()

        self.tab_options = self._build_options_tab()
        self.tabs.addTab(self.tab_options, "地图选项")

        self.tab_sponsor = self._build_sponsor_tab()
        self.tabs.addTab(self.tab_sponsor, "赞助设置")

        self.tab_about = self._build_about_tab()
        self.tabs.addTab(self.tab_about, "关于 & 赞助")

        right_layout.addWidget(self.tabs)

        # 启动按钮
        launch_layout = QHBoxLayout()
        launch_layout.addStretch()
        self.btn_launch = QPushButton("启动游戏")
        self.btn_launch.setStyleSheet(
            "QPushButton { font-size: 16px; padding: 10px 30px; }"
            "QPushButton:enabled { background-color: #4CAF50; color: white; }"
            "QPushButton:disabled { background-color: #cccccc; }"
        )
        self.btn_launch.setEnabled(False)
        self.btn_launch.clicked.connect(self._launch_game)
        launch_layout.addWidget(self.btn_launch)
        right_layout.addLayout(launch_layout)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 620])

        # ---- 底部操作按钮 ----
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        btn_qq = QPushButton("加入QQ群")
        btn_qq.clicked.connect(self._join_qq_group)
        bottom_layout.addWidget(btn_qq)

        btn_update = QPushButton("更新内容")
        btn_update.clicked.connect(lambda: webbrowser.open(SPONSOR_URLS["版本更新"]))
        bottom_layout.addWidget(btn_update)

        btn_live = QPushButton("看直播")
        btn_live.clicked.connect(lambda: webbrowser.open(SPONSOR_URLS["直播"]))
        bottom_layout.addWidget(btn_live)

        btn_sponsor = QPushButton("赞助大使")
        btn_sponsor.clicked.connect(self._open_sponsor_dialog)
        bottom_layout.addWidget(btn_sponsor)

        btn_single = QPushButton("单机启动")
        btn_single.setStyleSheet("font-weight: bold;")
        btn_single.clicked.connect(self._launch_game)
        bottom_layout.addWidget(btn_single)

        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

    def _build_options_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 缩略图 + 地图信息
        info_layout = QHBoxLayout()
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(140, 140)
        self.thumbnail_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setText("无预览")
        info_layout.addWidget(self.thumbnail_label)

        self.map_detail_label = QLabel("请选择地图")
        self.map_detail_label.setWordWrap(True)
        self.map_detail_label.setStyleSheet("padding: 5px;")
        info_layout.addWidget(self.map_detail_label, 1)
        layout.addLayout(info_layout)

        # 分辨率设置
        res_group = QGroupBox("游戏分辨率")
        res_layout = QHBoxLayout(res_group)
        self.resolution_combo = QComboBox()
        for name, w, h in RESOLUTION_OPTIONS:
            self.resolution_combo.addItem(name, (w, h))
        res_layout.addWidget(self.resolution_combo)
        res_layout.addStretch()
        layout.addWidget(res_group)

        # 动态选项区域 - 地图选择后填充
        self.options_grid = QGridLayout()
        layout.addLayout(self.options_grid)

        # 玩家选项（固定在最后）
        self.player_combo = QComboBox()
        self.player_combo.currentIndexChanged.connect(self._on_player_changed)
        layout.addWidget(QLabel("玩家:"))
        layout.addWidget(self.player_combo)

        layout.addStretch()
        return widget

    def _on_player_changed(self, index):
        map_offset = self.selected_map - 10000 if self.selected_map else 0
        if map_offset in self.current_options and len(self.current_options[map_offset]) == 11:
            self.current_options[map_offset][10] = self.player_combo.currentData()

    def _build_sponsor_tab(self):
        """赞助设置标签页 - 对应原启动器的VIP购买界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 顶部提示
        hint = QLabel(
            "<h3>赞助大使设置</h3>"
            "<p style='color:red;'>购买的赞助大使，启动地图后自动生效</p>"
            "<p>请勾选要启用的赞助项目（无需实际支付）：</p>"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # VIP 商品列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.vip_checkboxes = {}
        self.vip_type_combos = {}

        for prod in VIP_PRODUCTS:
            group = QGroupBox(prod["name"])
            g_layout = QHBoxLayout(group)

            cb = QCheckBox("启用赞助")
            self.vip_checkboxes[prod["name"]] = cb
            g_layout.addWidget(cb)

            combo = QComboBox()
            combo.addItem(f"永久 - {prod['permanent']}元", "permanent")
            combo.addItem(f"月卡 - {prod['monthly']}元", "monthly")
            combo.setEnabled(False)
            self.vip_type_combos[prod["name"]] = combo
            g_layout.addWidget(combo)

            # 联动：启用时才可选类型
            cb.toggled.connect(combo.setEnabled)

            g_layout.addStretch()
            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 账号信息（兼容原界面）
        acct_group = QGroupBox("账号信息（可选，兼容原启动器格式）")
        acct_layout = QGridLayout(acct_group)
        acct_layout.addWidget(QLabel("账号:"), 0, 0)
        self.sponsor_account = QLineEdit()
        acct_layout.addWidget(self.sponsor_account, 0, 1)
        acct_layout.addWidget(QLabel("确认账号:"), 1, 0)
        self.sponsor_account2 = QLineEdit()
        acct_layout.addWidget(self.sponsor_account2, 1, 1)
        layout.addWidget(acct_group)

        return widget

    def _build_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setHtml(f"""
        <h2>神龙地图启动器 5.2</h2>
        <p>基于原启动器功能完整重写的独立版本。</p>
        <hr>
        <h3>赞助 & 联系方式</h3>
        <ul>
            <li><b>QQ群:</b> {QQ_GROUP}</li>
            <li><b>官网:</b> <a href="{SPONSOR_URLS['官网']}">{SPONSOR_URLS['官网']}</a></li>
            <li><b>下载地址:</b> www.7F555.com</li>
        </ul>
        <h3>功能链接</h3>
        <ul>
            <li><a href="{SPONSOR_URLS['QQ联系']}">QQ联系页面</a></li>
            <li><a href="{SPONSOR_URLS['排行榜']}">排行榜</a></li>
            <li><a href="{SPONSOR_URLS['直播']}">直播</a></li>
            <li><a href="{SPONSOR_URLS['版本更新']}">版本更新</a></li>
        </ul>
        <hr>
        <p style="color:gray; font-size:12px;">
        版本: 8.6.8 (新版独立实现)<br>
        原项目: 玩家原创 - 神龙地图启动器
        </p>
        """)
        layout.addWidget(about_text)
        layout.addStretch()
        return widget

    def _setup_menu(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction("选择游戏目录", self._choose_game_dir)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        tools_menu.addAction("赞助设置...", self._open_sponsor_dialog)
        tools_menu.addSeparator()
        tools_menu.addAction("生成 config.lua", self._preview_config)

        # 赞助菜单
        sponsor_menu = menubar.addMenu("赞助(&S)")
        for name, url in SPONSOR_URLS.items():
            sponsor_menu.addAction(name, lambda u=url: webbrowser.open(u))

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction("QQ群: " + QQ_GROUP, lambda: QMessageBox.information(self, "QQ群", f"请加QQ群: {QQ_GROUP}"))
        help_menu.addAction("检查更新", self._check_version)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(f"QQ群: {QQ_GROUP} | 官网: www.7F555.com")

    # =====================================================================
    # 逻辑处理
    # =====================================================================

    def _load_map_list(self, category="全部地图"):
        self.map_table.setRowCount(0)
        row = 0
        for map_id in sorted(MAP_INFO.keys()):
            info = MAP_INFO[map_id]
            if category != "全部地图" and info.get("category") != category:
                continue

            self.map_table.insertRow(row)

            item_name = QTableWidgetItem(info["name"])
            item_name.setData(Qt.ItemDataRole.UserRole, map_id)
            self.map_table.setItem(row, 0, item_name)

            self.map_table.setItem(row, 1, QTableWidgetItem(info.get("author", "未知")))

            heat = info.get("heat", 0)
            item_heat = QTableWidgetItem(str(heat))
            item_heat.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.map_table.setItem(row, 2, item_heat)

            self.map_table.setItem(row, 3, QTableWidgetItem(info.get("status", "正常")))

            row += 1

        self.selected_map = None
        self.btn_launch.setEnabled(False)

    def _on_map_selected(self):
        selected = self.map_table.selectedItems()
        if not selected:
            self.selected_map = None
            self.btn_launch.setEnabled(False)
            return

        row = selected[0].row()
        map_id = self.map_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.selected_map = map_id
        self.btn_launch.setEnabled(True)

        map_offset = map_id - 10000

        # 解析 .map 文件获取动态选项和详细信息
        map_path = self.game_dir / "map" / f"{map_id}.map"
        parsed = MapOptionParser.parse(map_path)
        game_opts = MapOptionParser.get_game_options(parsed) if parsed else []
        player_num = parsed["player_num"] if parsed else 1

        # 缓存解析结果
        self._parsed_map_options = game_opts
        self._parsed_player_num = player_num

        # 更新缩略图
        thumb_data = MapOptionParser.extract_thumbnail(map_path)
        if thumb_data:
            pixmap = QPixmap()
            pixmap.loadFromData(thumb_data, "BMP")
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.thumbnail_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled)
            else:
                self.thumbnail_label.setText("预览加载失败")
        else:
            self.thumbnail_label.setText("无预览")

        # 更新地图详细信息
        info_text_parts = [f"<b>地图ID:</b> {map_id}"]
        map_name = MAP_INFO.get(map_id, {}).get("name", "未知")
        info_text_parts.append(f"<b>名称:</b> {map_name}")
        if parsed:
            if parsed.get("chn_name"):
                info_text_parts.append(f"<b>中文名:</b> {parsed['chn_name']}")
            if parsed.get("info"):
                info_text_parts.append(f"<b>描述:</b> {parsed['info']}")
            if parsed.get("player_num"):
                info_text_parts.append(f"<b>玩家数:</b> {parsed['player_num']}")
            if parsed.get("player_mode"):
                info_text_parts.append(f"<b>模式:</b> {parsed['player_mode']}")
            vip = parsed.get("vip_info", {})
            if vip.get("sponsor"):
                info_text_parts.append(f"<b>赞助:</b> {vip['sponsor']}")
            if vip.get("author"):
                info_text_parts.append(f"<b>作者:</b> {vip['author']}")
            if vip.get("qq_group"):
                info_text_parts.append(f"<b>QQ群:</b> {vip['qq_group']}")
        self.map_detail_label.setText("<br>".join(info_text_parts))

        # 清除旧选项控件
        while self.options_grid.count():
            item = self.options_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 动态创建选项下拉框
        self.option_controls = []
        for i, opt in enumerate(game_opts):
            row, col = divmod(i, 2)
            lbl = QLabel(f"{opt['name']}:")
            combo = QComboBox()
            for idx, val in enumerate(opt["values"]):
                combo.addItem(val, idx)
            combo.setCurrentIndex(opt["default_index"])
            combo.currentIndexChanged.connect(lambda idx, idx_opt=i: self._on_option_changed(idx_opt))
            self.options_grid.addWidget(lbl, row, col * 2)
            self.options_grid.addWidget(combo, row, col * 2 + 1)
            self.option_controls.append(combo)

        # 更新玩家选项
        self.player_combo.clear()
        for i in range(1, player_num + 1):
            self.player_combo.addItem(f"玩家{i}", i - 1)
        self.player_combo.setCurrentIndex(0)

        # 确保 current_options 包含该地图设置
        default_vals = [opt["default_index"] for opt in game_opts] + [-1] * (10 - len(game_opts)) + [0]
        if map_offset not in self.current_options:
            self.current_options[map_offset] = default_vals
        else:
            # 如果已有设置但选项数量不匹配，重新初始化
            if len(self.current_options[map_offset]) != 11:
                self.current_options[map_offset] = default_vals

        info = MAP_INFO.get(map_id, {})
        self.statusbar.showMessage(f"已选择: {info.get('name', '地图')} ({map_id})")

    def _on_option_changed(self, index):
        map_offset = self.selected_map - 10000 if self.selected_map else 0
        if map_offset not in self.current_options:
            game_opts = getattr(self, '_parsed_map_options', [])
            default_vals = [opt["default_index"] for opt in game_opts] + [-1] * (10 - len(game_opts)) + [0]
            self.current_options[map_offset] = default_vals

        combo = self.option_controls[index]
        self.current_options[map_offset][index] = combo.currentData()

    def _choose_game_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择游戏目录", str(self.game_dir))
        if path:
            self.game_dir = Path(path)
            self.dir_label.setText(f"目录: {self.game_dir}")

    def _join_qq_group(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(QQ_GROUP)
        try:
            webbrowser.open(f"tencent://groupwpa/?subcmd=all&param={QQ_GROUP}")
        except Exception:
            pass
        QMessageBox.information(self, "加入QQ群", f"QQ群号: {QQ_GROUP}\n已复制到剪贴板，请手动添加。")

    def _open_sponsor_dialog(self):
        dlg = SponsorSettingsDialog(self, self.vip_settings)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.vip_settings = dlg.get_vip_settings()
            enabled = sum(1 for v in self.vip_settings.values() if v > 0)
            self.statusbar.showMessage(f"赞助设置已保存: 已启用 {enabled} 项")
            # 同步到主界面的 checkbox/combo
            for name, setting in self.vip_settings.items():
                cb = self.vip_checkboxes.get(name)
                combo = self.vip_type_combos.get(name)
                if cb and combo:
                    cb.blockSignals(True)
                    combo.blockSignals(True)
                    cb.setChecked(setting > 0)
                    if setting == 1:
                        idx = combo.findData("permanent")
                        if idx >= 0:
                            combo.setCurrentIndex(idx)
                    elif setting == 2:
                        idx = combo.findData("monthly")
                        if idx >= 0:
                            combo.setCurrentIndex(idx)
                    combo.blockSignals(False)
                    cb.blockSignals(False)

    def _get_current_options(self):
        """获取当前地图的11个选项值 [opt0..opt9, player]"""
        map_offset = self.selected_map - 10000 if self.selected_map else 0
        stored = self.current_options.get(map_offset)
        if stored and len(stored) == 11:
            return stored
        # 使用解析后的默认值
        game_opts = getattr(self, '_parsed_map_options', [])
        player_idx = self.player_combo.currentData() if hasattr(self, 'player_combo') else 0
        opts = [opt["default_index"] for opt in game_opts] + [-1] * (10 - len(game_opts)) + [player_idx]
        return opts

    def _preview_config(self):
        if self.selected_map is None:
            QMessageBox.warning(self, "提示", "请先选择一张地图")
            return
        options = self._get_current_options()
        lua = generate_config_lua(self.selected_map, options, game_dir=self.game_dir)
        QMessageBox.information(self, "config.lua 预览", f"<pre>{lua}</pre>")

    def _launch_game(self):
        """启动游戏 — 完整诊断信息弹窗."""
        if self.selected_map is None:
            QMessageBox.warning(self, "提示", "请先选择一张地图")
            return

        map_id = int(self.selected_map)
        game_dir = Path(self.game_dir).absolute()

        # 检查 game.exe 存在
        game_exe = game_dir / "core" / "game.exe"
        if not game_exe.exists():
            game_exe = game_dir / "game.exe"
        if not game_exe.exists():
            QMessageBox.critical(self, "启动错误", f"找不到游戏文件:\n{game_exe}")
            return

        options = self._get_current_options()

        try:
            bridge, diag_msg = launch_game(
                game_dir=game_dir,
                map_id=map_id,
                options=options,
                resolution_index=self.resolution_combo.currentIndex(),
            )

            if bridge is None:
                self._show_diag("启动失败", diag_msg, QMessageBox.Icon.Critical)
                return

            self._last_launch_pid = bridge.process_id
            self._game_process_handle = bridge.process_handle

            info = MAP_INFO.get(self.selected_map, {})
            map_name = info.get("name", str(map_id))
            self.statusbar.showMessage(
                f"游戏已启动: {map_name} ({map_id}) | PID={bridge.process_id}"
            )

            # 弹出诊断结果
            if diag_msg:
                self._show_diag(f"启动诊断 — {map_name} ({map_id})", diag_msg,
                               QMessageBox.Icon.Information)

        except Exception as e:
            import traceback
            detail = traceback.format_exc()
            self._show_diag("启动异常", f"{e}\n\n详细信息:\n{detail}",
                           QMessageBox.Icon.Critical)

    def _show_diag(self, title: str, message: str, icon):
        """在可滚动对话框中展示诊断信息."""
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setMinimumSize(550, 400)

        layout = QVBoxLayout(dlg)

        if icon == QMessageBox.Icon.Critical:
            layout.addWidget(QLabel("<b style='color:red;'>启动失败</b>"))
        elif "失败" in message or "错误" in message:
            layout.addWidget(QLabel("<b style='color:orange;'>诊断发现问题</b>"))
        else:
            layout.addWidget(QLabel("<b>启动诊断报告</b>"))

        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(message)
        text.setStyleSheet("font-family: Microsoft YaHei, Consolas, monospace; font-size: 12px;")
        layout.addWidget(text)

        btn = QPushButton("确定")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)

        dlg.exec()

    def verify_launch(self):
        """手动触发启动验证."""
        pid = getattr(self, "_last_launch_pid", None)
        if pid is None:
            QMessageBox.information(self, "验证", "没有可验证的启动记录")
            return

        diag = diagnose_launch(self.game_dir, pid, self.selected_map, timeout_seconds=5)
        self._show_diag("启动验证结果", diag.get("user_message", str(diag)),
                       QMessageBox.Icon.Information)

    def _check_version(self):
        self.statusbar.showMessage("正在检查版本更新...")
        self.version_thread = VersionCheckThread()
        self.version_thread.result.connect(self._on_version_result)
        self.version_thread.start()

    def _on_version_result(self, success, data):
        if success:
            self.statusbar.showMessage("版本检查完成")
            if "version" in data.lower() or "更新" in data:
                pass
        else:
            self.statusbar.showMessage(f"版本检查失败: {data}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 设置中文字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
