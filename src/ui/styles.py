"""
扁平简约风格样式表
Flat minimalist style definitions for the Image Color Classifier UI
"""

# 主色调定义
COLORS = {
    'background': '#F5F5F5',      # 浅灰背景
    'surface': '#FFFFFF',          # 白色表面
    'primary': '#607D8B',          # 蓝灰主色
    'primary_hover': '#546E7A',    # 主色悬停
    'primary_pressed': '#455A64',  # 主色按下
    'secondary': '#90A4AE',        # 次要色
    'text_primary': '#37474F',     # 主要文字
    'text_secondary': '#78909C',   # 次要文字
    'border': '#E0E0E0',           # 边框色
    'success': '#66BB6A',          # 成功色
    'warning': '#FFA726',          # 警告色
    'error': '#EF5350',            # 错误色
    'progress_bg': '#E0E0E0',      # 进度条背景
    'progress_fill': '#607D8B',    # 进度条填充
}

# 主窗口样式
MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QWidget {{
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {COLORS['text_primary']};
}}
"""

# 按钮样式
BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_pressed']};
}}

QPushButton:disabled {{
    background-color: {COLORS['secondary']};
    color: {COLORS['background']};
}}
"""

# 次要按钮样式
SECONDARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['surface']};
    color: {COLORS['primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {COLORS['background']};
    border-color: {COLORS['primary']};
}}

QPushButton:pressed {{
    background-color: {COLORS['border']};
}}

QPushButton:disabled {{
    color: {COLORS['secondary']};
    border-color: {COLORS['border']};
}}
"""

# 进度条样式
PROGRESS_BAR_STYLE = f"""
QProgressBar {{
    background-color: {COLORS['progress_bg']};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['progress_fill']};
    border-radius: 4px;
}}
"""

# 标签样式
LABEL_STYLE = f"""
QLabel {{
    color: {COLORS['text_primary']};
    font-size: 13px;
}}
"""

# 标题标签样式
TITLE_LABEL_STYLE = f"""
QLabel {{
    color: {COLORS['text_primary']};
    font-size: 18px;
    font-weight: 600;
}}
"""

# 次要标签样式
SECONDARY_LABEL_STYLE = f"""
QLabel {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
}}
"""

# 输入框样式
LINE_EDIT_STYLE = f"""
QLineEdit {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
    color: {COLORS['text_primary']};
}}

QLineEdit:focus {{
    border-color: {COLORS['primary']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['background']};
    color: {COLORS['text_secondary']};
}}
"""

# 分组框样式
GROUP_BOX_STYLE = f"""
QGroupBox {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    margin-top: 12px;
    padding: 16px;
    font-size: 13px;
    font-weight: 500;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: {COLORS['text_primary']};
}}
"""

# 滚动区域样式
SCROLL_AREA_STYLE = f"""
QScrollArea {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
}}

QScrollArea > QWidget > QWidget {{
    background-color: {COLORS['surface']};
}}

QScrollBar:vertical {{
    background-color: {COLORS['background']};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['secondary']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['primary']};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['background']};
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['secondary']};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['primary']};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""

# 预览卡片样式
PREVIEW_CARD_STYLE = f"""
QFrame {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
}}

QFrame:hover {{
    border-color: {COLORS['primary']};
}}
"""

# 管理员模式标识样式
ADMIN_BADGE_STYLE = f"""
QLabel {{
    background-color: {COLORS['warning']};
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 3px;
}}
"""

# 状态栏样式
STATUS_BAR_STYLE = f"""
QStatusBar {{
    background-color: {COLORS['surface']};
    border-top: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
    font-size: 12px;
}}
"""

# 工具提示样式
TOOLTIP_STYLE = f"""
QToolTip {{
    background-color: {COLORS['text_primary']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}}
"""


def get_full_stylesheet() -> str:
    """获取完整的应用样式表"""
    return (
        MAIN_WINDOW_STYLE +
        BUTTON_STYLE +
        PROGRESS_BAR_STYLE +
        LABEL_STYLE +
        LINE_EDIT_STYLE +
        GROUP_BOX_STYLE +
        SCROLL_AREA_STYLE +
        STATUS_BAR_STYLE +
        TOOLTIP_STYLE
    )


def apply_button_style(button, style_type: str = 'primary') -> None:
    """
    为按钮应用指定样式
    
    Args:
        button: QPushButton实例
        style_type: 'primary' 或 'secondary'
    """
    if style_type == 'secondary':
        button.setStyleSheet(SECONDARY_BUTTON_STYLE)
    else:
        button.setStyleSheet(BUTTON_STYLE)


def apply_label_style(label, style_type: str = 'primary') -> None:
    """
    为标签应用指定样式
    
    Args:
        label: QLabel实例
        style_type: 'primary', 'secondary', 或 'title'
    """
    if style_type == 'title':
        label.setStyleSheet(TITLE_LABEL_STYLE)
    elif style_type == 'secondary':
        label.setStyleSheet(SECONDARY_LABEL_STYLE)
    else:
        label.setStyleSheet(LABEL_STYLE)
