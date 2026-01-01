"""
主窗口 - Fluent Design 风格
"""

import os
import sys

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QPoint, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QProgressBar, QFileDialog,
    QMessageBox, QScrollArea, QFrame, QComboBox, QSlider, QSpinBox,
    QTabWidget,
)
from PyQt6.QtGui import QPixmap, QMouseEvent, QIcon

from .styles import (
    get_stylesheet, get_card_style, COLORS, COLORS_LIGHT, COLORS_DARK,
    PRIMARY_BTN, SECONDARY_BTN, TITLEBAR_BTN, CLOSE_BTN,
    SUBTITLE_STYLE, CAPTION_STYLE, get_button_styles, set_dark_mode,
    get_subtitle_style, get_caption_style, get_toggle_style,
)
from .win_effects import enable_acrylic, enable_rounded_corners

from core.engine import ClassificationEngine
from core.advanced_engine import AdvancedClassificationEngine
from core.preview_generator import PreviewGenerator
from core.models import AdvancedClassificationResult, FeatureWeights


class Worker(QThread):
    """分类工作线程"""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, engine, source, target=None, n_clusters=None, advanced=False):
        super().__init__()
        self.engine, self.source, self.target = engine, source, target
        self.n_clusters, self.advanced = n_clusters, advanced
    
    def run(self):
        try:
            cb = lambda c, t, f: self.progress.emit(c, t, f)
            if self.advanced:
                r = self.engine.classify(self.source, self.target, n_clusters=self.n_clusters, progress_callback=cb)
            else:
                r = self.engine.classify(self.source, self.target, progress_callback=cb)
            self.finished.emit(r)
        except Exception as e:
            self.error.emit(str(e))


class TitleBar(QFrame):
    """自定义标题栏 - 使用 QFrame 确保有背景可以接收鼠标事件"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self._drag_pos = None
        self._dragging = False
        self.setFixedHeight(40)
        self.setObjectName("titlebar")
        # 使用半透明背景，保持亚克力效果可见
        self.setStyleSheet("""
            QFrame#titlebar {
                background-color: rgba(255, 255, 255, 0.3);
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题
        self.title = QLabel("图片颜色分类器")
        self.title.setStyleSheet(f"font-size: 13px; color: {COLORS['text']}; background: transparent;")
        layout.addWidget(self.title)
        layout.addStretch()
        
        # 窗口控制按钮
        self._min_btn = QPushButton("─")
        self._min_btn.setObjectName("minBtn")
        self._min_btn.setFixedSize(46, 40)
        self._min_btn.clicked.connect(self._on_minimize)
        layout.addWidget(self._min_btn)
        
        self._max_btn = QPushButton("□")
        self._max_btn.setObjectName("maxBtn")
        self._max_btn.setFixedSize(46, 40)
        self._max_btn.clicked.connect(self._on_maximize)
        layout.addWidget(self._max_btn)
        
        self._close_btn = QPushButton("✕")
        self._close_btn.setObjectName("closeBtn")
        self._close_btn.setFixedSize(46, 40)
        self._close_btn.clicked.connect(self._on_close)
        layout.addWidget(self._close_btn)
        
        # 按钮样式
        btn_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS['text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(0, 0, 0, 0.08);
            }}
            QPushButton:pressed {{
                background: rgba(0, 0, 0, 0.15);
            }}
        """
        close_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS['text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: #E81123;
                color: white;
            }}
            QPushButton:pressed {{
                background: #F1707A;
                color: white;
            }}
        """
        self._min_btn.setStyleSheet(btn_style)
        self._max_btn.setStyleSheet(btn_style)
        self._close_btn.setStyleSheet(close_style)
    
    def _on_minimize(self):
        self.parent_window.showMinimized()
    
    def _on_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self._max_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self._max_btn.setText("❐")
    
    def _on_close(self):
        self.parent_window.close()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在按钮上
            click_pos = event.position().toPoint()
            for btn in [self._min_btn, self._max_btn, self._close_btn]:
                if btn.geometry().contains(click_pos):
                    # 点击在按钮上，不处理拖拽
                    super().mousePressEvent(event)
                    return
            
            # 开始拖拽
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_pos is not None:
            # 如果窗口是最大化状态，先还原
            if self.parent_window.isMaximized():
                # 计算鼠标在标题栏中的相对位置比例
                ratio = event.position().x() / self.width()
                self.parent_window.showNormal()
                self._max_btn.setText("□")
                # 根据比例重新计算拖拽位置
                new_width = self.parent_window.width()
                new_x = int(new_width * ratio)
                self._drag_pos.setX(new_x)
                self._drag_pos.setY(20)  # 标题栏中间位置
            
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.parent_window.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._drag_pos = None
        event.accept()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否双击在按钮上
            click_pos = event.position().toPoint()
            for btn in [self._min_btn, self._max_btn, self._close_btn]:
                if btn.geometry().contains(click_pos):
                    super().mouseDoubleClickEvent(event)
                    return
            # 双击标题栏切换最大化
            self._on_maximize()
            event.accept()


class AnimatedToggle(QWidget):
    """带动画的胶囊形 Toggle 开关"""
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 22)
        self._checked = False
        self._dark_mode = False
        
        # 背景
        self._bg = QFrame(self)
        self._bg.setGeometry(0, 0, 44, 22)
        self._bg.setStyleSheet(self._get_bg_style())
        
        # 滑块
        self._knob = QFrame(self)
        self._knob.setFixedSize(18, 18)
        self._knob.move(2, 2)
        self._knob.setStyleSheet("background: white; border-radius: 9px;")
        
        # 滑块动画 - 使用 OutBack 缓动曲线实现阻尼/回弹效果
        self._knob_anim = QPropertyAnimation(self._knob, b"geometry")
        self._knob_anim.setDuration(300)  # 稍长的动画时间
        self._knob_anim.setEasingCurve(QEasingCurve.Type.OutBack)  # 带回弹的阻尼效果
    
    def _get_bg_style(self):
        c = COLORS_DARK if self._dark_mode else COLORS_LIGHT
        if self._checked:
            return f"background: {c['accent']}; border: none; border-radius: 11px;"
        else:
            return f"background: {c['border_strong']}; border: none; border-radius: 11px;"
    
    def setChecked(self, checked: bool):
        self._checked = checked
        self._update_position(animate=False)
        self._bg.setStyleSheet(self._get_bg_style())
    
    def isChecked(self) -> bool:
        return self._checked
    
    def setDarkMode(self, dark: bool):
        self._dark_mode = dark
        self._bg.setStyleSheet(self._get_bg_style())
    
    def _update_position(self, animate: bool = True):
        start = QRect(2, 2, 18, 18)
        end = QRect(24, 2, 18, 18)
        
        if self._checked:
            target = end
        else:
            target = start
        
        if animate:
            self._knob_anim.setStartValue(self._knob.geometry())
            self._knob_anim.setEndValue(target)
            self._knob_anim.start()
        else:
            self._knob.setGeometry(target)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            self._update_position(animate=True)
            self._bg.setStyleSheet(self._get_bg_style())
            self.toggled.emit(self._checked)
            event.accept()


class Card(QFrame):
    """卡片组件"""
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 20)
        self._layout.setSpacing(16)  # 增加间距
        self._title_label = None
        if title:
            self._title_label = QLabel(title)
            self._title_label.setStyleSheet(SUBTITLE_STYLE)
            self._layout.addWidget(self._title_label)
    
    def addWidget(self, w): self._layout.addWidget(w)
    def addLayout(self, l): self._layout.addLayout(l)
    
    def update_title_style(self, dark_mode: bool):
        """更新标题样式"""
        if self._title_label:
            self._title_label.setStyleSheet(get_subtitle_style(dark_mode))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self._engine = ClassificationEngine()
        self._adv_engine = AdvancedClassificationEngine()
        self._preview_gen = PreviewGenerator()
        self._worker = None
        self._advanced = False
        
        
        self._settings = QSettings("ColorClassifier", "Settings")
        self._opacity = self._settings.value("opacity", 120, int)
        self._blur_color = self._settings.value("blur_color", 0xE8E8E8, int)
        self._dark_mode = self._settings.value("dark_mode", False, bool)
        
        # 应用主题
        set_dark_mode(self._dark_mode)
        
        self._init_window()
        self._init_ui()
        QTimer.singleShot(100, self._apply_effects)
    
    def _init_window(self):
        self.setWindowTitle("图片颜色分类器")
        self.setMinimumSize(950, 720)
        self.resize(1000, 780)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(get_stylesheet(self._dark_mode))
        
        # 设置 Windows AppUserModelID（让任务栏正确显示图标）
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('ColorClassifier.App')
        except:
            pass
        
        # 设置窗口图标（任务栏显示）
        if getattr(sys, 'frozen', False):
            # 打包后的路径 - 图标在 _internal 目录
            base_path = os.path.dirname(sys.executable)
            icon_path = os.path.join(base_path, '_internal', 'app.ico')
        else:
            # 开发环境
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app.ico')
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def _apply_effects(self):
        enable_rounded_corners(self)
        color = (self._opacity << 24) | (self._blur_color & 0x00FFFFFF)
        if not enable_acrylic(self, color):
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            fallback = "#202020" if self._dark_mode else "#F0F0F0"
            self.setStyleSheet(get_stylesheet(self._dark_mode) + f"QMainWindow{{background:{fallback};}}")
        
        # 更新标题栏和内容区域的透明度
        self._update_theme_styles()
    
    def _update_theme_styles(self):
        """更新主题相关的样式"""
        c = COLORS_DARK if self._dark_mode else COLORS_LIGHT
        
        # 计算基于透明度的 alpha 值 (opacity 30-200 映射到 0.2-0.6)
        alpha = 0.2 + (self._opacity - 30) / 170 * 0.4
        
        # 更新标题栏样式
        if self._dark_mode:
            titlebar_bg = f"rgba(30, 30, 30, {alpha})"
            content_bg = f"rgba(40, 40, 40, {alpha + 0.1})"
        else:
            titlebar_bg = f"rgba(255, 255, 255, {alpha})"
            content_bg = f"rgba(255, 255, 255, {alpha + 0.1})"
        
        self._titlebar.setStyleSheet(f"""
            QFrame#titlebar {{
                background-color: {titlebar_bg};
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)
        self._titlebar.title.setStyleSheet(f"font-size: 13px; color: {c['text']}; background: transparent;")
        
        # 更新标题栏按钮样式
        btn_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {c['text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {c['titlebar_hover']};
            }}
            QPushButton:pressed {{
                background: {c['border_strong']};
            }}
        """
        close_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {c['text']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: #E81123;
                color: white;
            }}
            QPushButton:pressed {{
                background: #F1707A;
                color: white;
            }}
        """
        self._titlebar._min_btn.setStyleSheet(btn_style)
        self._titlebar._max_btn.setStyleSheet(btn_style)
        self._titlebar._close_btn.setStyleSheet(close_style)
        
        # 更新内容区域样式
        self._content_frame.setStyleSheet(f"""
            QFrame#contentFrame {{
                background-color: {content_bg};
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)
    
    def _init_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        self._titlebar = TitleBar(self)
        main_layout.addWidget(self._titlebar)
        
        # 内容区域 - 使用半透明背景保持亚克力效果
        self._content_frame = QFrame()
        self._content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(self._content_frame)
        content_layout.setContentsMargins(24, 16, 24, 24)
        content_layout.setSpacing(0)
        
        self._tabs = QTabWidget()
        self._tabs.addTab(self._create_main_page(), "分类")
        self._tabs.addTab(self._create_settings_page(), "设置")
        content_layout.addWidget(self._tabs)
        
        main_layout.addWidget(self._content_frame, 1)
        self._update_states()

    
    def _create_main_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 8, 0)
        content_layout.setSpacing(16)
        
        self._setup_folder_card(content_layout)
        self._setup_settings_card(content_layout)
        self._setup_progress_card(content_layout)
        self._setup_preview_card(content_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        return page
    
    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)
        
        self._settings_card = Card("外观设置")
        
        # 夜间模式切换 - 带动画的胶囊形 Toggle
        row0 = QHBoxLayout()
        row0.setContentsMargins(0, 4, 0, 4)
        row0.addWidget(QLabel("夜间模式"))
        row0.addStretch()
        
        self._dark_mode_toggle = AnimatedToggle()
        self._dark_mode_toggle.setChecked(self._dark_mode)
        self._dark_mode_toggle.setDarkMode(self._dark_mode)
        self._dark_mode_toggle.toggled.connect(self._on_dark_mode_change)
        row0.addWidget(self._dark_mode_toggle)
        self._settings_card.addLayout(row0)
        
        # 透明度滑块 - 增加行高
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 4, 0, 4)
        row1.addWidget(QLabel("亚克力透明度"))
        row1.addStretch()
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(30, 200)  # 更大范围
        self._opacity_slider.setValue(self._opacity)
        self._opacity_slider.setMinimumWidth(200)
        self._opacity_slider.setMinimumHeight(24)
        self._opacity_slider.valueChanged.connect(self._on_opacity_change)
        row1.addWidget(self._opacity_slider)
        self._opacity_label = QLabel(f"{self._opacity}")
        self._opacity_label.setMinimumWidth(35)
        row1.addWidget(self._opacity_label)
        self._settings_card.addLayout(row1)
        
        # 颜色预设 - 增加行高
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 4, 0, 4)
        row2.addWidget(QLabel("背景色调"))
        row2.addStretch()
        colors = [("浅灰", 0xE8E8E8), ("浅蓝", 0xF0E8D8), ("浅绿", 0xD8F0D8), ("浅紫", 0xE8D8F0)]
        for name, color in colors:
            btn = QPushButton(name)
            btn.setStyleSheet(SECONDARY_BTN)
            btn.setFixedSize(60, 32)
            btn.clicked.connect(lambda _, c=color: self._set_blur_color(c))
            row2.addWidget(btn)
        self._settings_card.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addStretch()
        reset_btn = QPushButton("恢复默认")
        reset_btn.setStyleSheet(SECONDARY_BTN)
        reset_btn.clicked.connect(self._reset_settings)
        row3.addWidget(reset_btn)
        self._settings_card.addLayout(row3)
        
        layout.addWidget(self._settings_card)
        layout.addStretch()
        return page
    
    def _on_opacity_change(self, value):
        self._opacity = value
        self._opacity_label.setText(str(value))
        self._settings.setValue("opacity", value)
        self._apply_effects()
    
    def _on_dark_mode_change(self, checked: bool = None):
        if checked is not None:
            self._dark_mode = checked
        else:
            self._dark_mode = self._dark_mode_toggle.isChecked()
        self._settings.setValue("dark_mode", self._dark_mode)
        
        # 更新 Toggle 样式
        self._dark_mode_toggle.setDarkMode(self._dark_mode)
        
        # 更新全局颜色配置
        set_dark_mode(self._dark_mode)
        
        # 更新全局样式表
        self.setStyleSheet(get_stylesheet(self._dark_mode))
        
        # 更新主题相关样式
        self._update_theme_styles()
        
        # 更新所有卡片标题样式
        self._update_card_styles()
        
        # 重新应用亚克力效果
        self._apply_effects()
    
    def _update_card_styles(self):
        """更新所有卡片的标题样式"""
        # 设置页面的卡片
        if hasattr(self, '_settings_card'):
            self._settings_card.update_title_style(self._dark_mode)
        
        # 遍历主页面的所有卡片
        for card in self.findChildren(Card):
            card.update_title_style(self._dark_mode)
    
    def _set_blur_color(self, color):
        self._blur_color = color
        self._settings.setValue("blur_color", color)
        self._apply_effects()
    
    def _reset_settings(self):
        self._opacity = 120
        self._blur_color = 0xE8E8E8
        self._dark_mode = False
        self._opacity_slider.setValue(120)
        self._dark_mode_toggle.setChecked(False)
        self._dark_mode_toggle.setDarkMode(False)
        self._settings.setValue("opacity", 120)
        self._settings.setValue("blur_color", 0xE8E8E8)
        self._settings.setValue("dark_mode", False)
        set_dark_mode(False)
        self.setStyleSheet(get_stylesheet(False))
        self._update_theme_styles()
        self._update_card_styles()
        self._apply_effects()

    
    def _setup_folder_card(self, layout):
        card = Card("选择文件夹")
        
        row = QHBoxLayout()
        row.setSpacing(12)
        
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("点击浏览选择图片文件夹...")
        self._path_edit.setReadOnly(True)
        self._path_edit.setMinimumHeight(38)
        row.addWidget(self._path_edit, 1)
        
        self._browse_btn = QPushButton("浏览")
        self._browse_btn.setStyleSheet(SECONDARY_BTN)
        self._browse_btn.setMinimumSize(80, 38)
        self._browse_btn.clicked.connect(self._on_browse)
        row.addWidget(self._browse_btn)
        
        card.addLayout(row)
        
        # 按钮放在卡片内部
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self._start_btn = QPushButton("开始分类")
        self._start_btn.setStyleSheet(PRIMARY_BTN)
        self._start_btn.setMinimumSize(120, 40)
        self._start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self._start_btn)
        
        self._rollback_btn = QPushButton("撤销")
        self._rollback_btn.setStyleSheet(SECONDARY_BTN)
        self._rollback_btn.setMinimumSize(80, 40)
        self._rollback_btn.clicked.connect(self._on_rollback)
        btn_row.addWidget(self._rollback_btn)
        
        btn_row.addStretch()
        card.addLayout(btn_row)
        
        layout.addWidget(card)
    
    def _setup_settings_card(self, layout):
        card = Card("分类设置")
        
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(QLabel("分类模式"))
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("简单模式 - 按主色调分类", False)
        self._mode_combo.addItem("高级模式 - 多维度特征分析", True)
        self._mode_combo.setMinimumSize(260, 38)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_change)
        row.addWidget(self._mode_combo)
        row.addStretch()
        card.addLayout(row)
        
        # 高级面板
        self._adv_panel = QWidget()
        self._adv_panel.setVisible(False)
        adv = QVBoxLayout(self._adv_panel)
        adv.setContentsMargins(0, 12, 0, 0)
        adv.setSpacing(12)
        
        cr = QHBoxLayout()
        cr.addWidget(QLabel("聚类数量"))
        self._auto_btn = QPushButton("自动")
        self._auto_btn.setCheckable(True)
        self._auto_btn.setChecked(True)
        self._auto_btn.setStyleSheet(SECONDARY_BTN)
        self._auto_btn.setMinimumSize(70, 34)
        self._auto_btn.clicked.connect(self._on_auto_toggle)
        cr.addWidget(self._auto_btn)
        self._cluster_spin = QSpinBox()
        self._cluster_spin.setRange(2, 20)
        self._cluster_spin.setValue(5)
        self._cluster_spin.setEnabled(False)
        self._cluster_spin.setMinimumSize(80, 34)
        cr.addWidget(self._cluster_spin)
        cr.addStretch()
        adv.addLayout(cr)
        
        wl = QLabel("特征权重")
        wl.setStyleSheet(CAPTION_STYLE)
        adv.addWidget(wl)
        
        grid = QGridLayout()
        grid.setSpacing(12)
        self._feature_sliders = {}
        slider_names = [("hue", "色调", 40), ("lightness", "明度", 35), ("saturation", "饱和度", 25)]
        for i, (key, name, default) in enumerate(slider_names):
            grid.addWidget(QLabel(name), i, 0)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(default)
            slider.setMinimumWidth(150)
            grid.addWidget(slider, i, 1)
            lbl = QLabel(f"{default}%")
            lbl.setMinimumWidth(40)
            grid.addWidget(lbl, i, 2)
            slider.valueChanged.connect(lambda v, l=lbl: l.setText(f"{v}%"))
            self._feature_sliders[key] = slider
        
        self._hue_slider = self._feature_sliders["hue"]
        self._light_slider = self._feature_sliders["lightness"]
        self._sat_slider = self._feature_sliders["saturation"]
        adv.addLayout(grid)
        
        card.addWidget(self._adv_panel)
        layout.addWidget(card)

    
    def _setup_progress_card(self, layout):
        card = Card("处理进度")
        
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(4)
        card.addWidget(self._progress)
        
        row = QHBoxLayout()
        self._status_lbl = QLabel("就绪")
        self._status_lbl.setStyleSheet(CAPTION_STYLE)
        row.addWidget(self._status_lbl)
        row.addStretch()
        self._file_lbl = QLabel("")
        self._file_lbl.setStyleSheet(CAPTION_STYLE)
        row.addWidget(self._file_lbl)
        card.addLayout(row)
        layout.addWidget(card)
    
    def _setup_preview_card(self, layout):
        card = Card("分类预览")
        
        self._preview_scroll = QScrollArea()
        self._preview_scroll.setWidgetResizable(True)
        self._preview_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._preview_scroll.setMinimumHeight(160)
        
        self._preview_widget = QWidget()
        self._preview_layout = QVBoxLayout(self._preview_widget)
        self._preview_layout.setContentsMargins(0, 0, 0, 0)
        self._preview_layout.setSpacing(12)
        self._preview_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self._empty_lbl = QLabel("分类完成后将在此显示预览")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setStyleSheet(CAPTION_STYLE)
        self._preview_layout.addWidget(self._empty_lbl)
        
        self._preview_scroll.setWidget(self._preview_widget)
        card.addWidget(self._preview_scroll)
        layout.addWidget(card, 1)
    
    # ========== 事件 ==========
    
    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            self._path_edit.setText(folder)
            self._update_states()
    
    def _on_mode_change(self, idx):
        self._advanced = self._mode_combo.currentData()
        self._adv_panel.setVisible(self._advanced)
    
    def _on_auto_toggle(self):
        auto = self._auto_btn.isChecked()
        self._cluster_spin.setEnabled(not auto)
        self._auto_btn.setText("自动" if auto else "手动")
    
    def _on_start(self):
        src = self._path_edit.text()
        if not src or not os.path.isdir(src):
            QMessageBox.warning(self, "提示", "请先选择有效的文件夹")
            return
        
        self._set_enabled(False)
        self._progress.setValue(0)
        self._status_lbl.setText("正在扫描...")
        self._file_lbl.setText("")
        
        if self._advanced:
            weights = FeatureWeights(
                hue=self._hue_slider.value() / 100.0,
                lightness=self._light_slider.value() / 100.0,
                saturation=self._sat_slider.value() / 100.0
            )
            self._adv_engine.set_feature_weights(weights)
            n = None if self._auto_btn.isChecked() else self._cluster_spin.value()
            self._worker = Worker(self._adv_engine, src, src, n, True)
        else:
            self._worker = Worker(self._engine, src, advanced=False)
        
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_progress(self, cur, total, fname):
        if total > 0:
            self._progress.setValue(int(cur / total * 100))
            self._status_lbl.setText(f"处理中: {cur}/{total}")
            self._file_lbl.setText(fname)
    
    def _on_finished(self, result):
        self._set_enabled(True)
        self._update_states()
        
        if isinstance(result, AdvancedClassificationResult):
            self._status_lbl.setText(f"完成: {result.total_images}张, {result.n_clusters}类")
            msg = f"分类完成\n{result.total_images}张图片分为{result.n_clusters}类"
        else:
            self._status_lbl.setText(f"完成: 成功{result.total_processed}张")
            msg = f"分类完成\n成功{result.total_processed}张, 失败{result.total_failed}张"
        
        self._file_lbl.setText("")
        if result.total_processed > 0:
            self._show_preview(result)
        QMessageBox.information(self, "完成", msg)
    
    def _on_error(self, err):
        self._set_enabled(True)
        self._update_states()
        self._status_lbl.setText("分类失败")
        QMessageBox.critical(self, "错误", f"分类出错:\n{err}")
    
    def _on_rollback(self):
        can_s = self._engine.can_rollback()
        can_a = self._adv_engine.can_rollback()
        
        if not can_s and not can_a:
            QMessageBox.information(self, "提示", "没有可撤销的操作")
            return
        
        engine = self._adv_engine if can_a else self._engine
        cnt = engine.get_rollback_count()
        
        if QMessageBox.question(
            self, "确认", f"确定撤销? 将恢复{cnt}个文件",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            result = engine.rollback()
            self._update_states()
            self._clear_preview()
            QMessageBox.information(self, "完成", f"恢复{result.success_count}个, 失败{result.failed_count}个")

    
    # ========== 预览 ==========
    
    def _show_preview(self, result):
        self._clear_preview()
        src = self._path_edit.text()
        for cat, cnt in sorted(result.category_counts.items(), key=lambda x: -x[1]):
            path = os.path.join(src, cat)
            if os.path.isdir(path):
                self._add_preview_item(cat, cnt, path)
    
    def _add_preview_item(self, cat, cnt, path):
        frame = QFrame()
        frame.setStyleSheet("background: rgba(255,255,255,0.5); border: none; border-radius: 6px;")
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)
        
        header = QHBoxLayout()
        lbl = QLabel(f"{cat} ({cnt}张)")
        lbl.setStyleSheet("font-weight: 600;")
        header.addWidget(lbl)
        header.addStretch()
        
        btn = QPushButton("展开")
        btn.setStyleSheet(SECONDARY_BTN)
        btn.setFixedSize(60, 28)
        btn.clicked.connect(lambda: self._toggle_preview(frame, path, btn))
        header.addWidget(btn)
        layout.addLayout(header)
        
        thumbs = QWidget()
        thumbs.setVisible(False)
        thumbs_layout = QGridLayout(thumbs)
        thumbs_layout.setSpacing(6)
        thumbs_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(thumbs)
        
        frame._thumbs = thumbs
        frame._thumbs_layout = thumbs_layout
        frame._expanded = False
        
        self._preview_layout.addWidget(frame)
    
    def _toggle_preview(self, frame, path, btn):
        if frame._expanded:
            frame._thumbs.setVisible(False)
            btn.setText("展开")
            frame._expanded = False
        else:
            if frame._thumbs_layout.count() == 0:
                self._load_thumbs(frame, path)
            frame._thumbs.setVisible(True)
            btn.setText("收起")
            frame._expanded = True
    
    def _load_thumbs(self, frame, path):
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'))]
            files = files[:8]
            for i, fname in enumerate(files):
                fpath = os.path.join(path, fname)
                try:
                    pixmap = QPixmap(fpath)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        lbl = QLabel()
                        lbl.setPixmap(pixmap)
                        lbl.setStyleSheet("border: 1px solid rgba(0,0,0,0.1); border-radius: 4px; padding: 2px;")
                        frame._thumbs_layout.addWidget(lbl, i // 4, i % 4)
                except:
                    pass
        except:
            pass
    
    def _clear_preview(self):
        while self._preview_layout.count() > 0:
            item = self._preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self._empty_lbl = QLabel("分类完成后将在此显示预览")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setStyleSheet(CAPTION_STYLE)
        self._preview_layout.addWidget(self._empty_lbl)
    
    def _set_enabled(self, enabled: bool):
        self._browse_btn.setEnabled(enabled)
        self._start_btn.setEnabled(enabled)
        self._rollback_btn.setEnabled(enabled)
        self._mode_combo.setEnabled(enabled)
    
    def _update_states(self):
        has_path = bool(self._path_edit.text()) and os.path.isdir(self._path_edit.text())
        can_rollback = self._engine.can_rollback() or self._adv_engine.can_rollback()
        self._start_btn.setEnabled(has_path)
        self._rollback_btn.setEnabled(can_rollback)
