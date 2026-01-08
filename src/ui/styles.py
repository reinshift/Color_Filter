"""
Fluent Design 样式表
Windows 11 风格，支持亚克力效果和夜间模式
"""

# 浅色主题配色
COLORS_LIGHT = {
    'bg_solid': '#F5F5F5',
    'surface': 'rgba(255, 255, 255, 0.50)',
    'surface_solid': 'rgba(255, 255, 255, 0.85)',
    'accent': '#0078D4',
    'accent_hover': '#1984D8',
    'accent_pressed': '#006CBE',
    'text': '#1A1A1A',
    'text_secondary': '#606060',
    'text_on_accent': '#FFFFFF',
    'border': 'rgba(0, 0, 0, 0.06)',
    'border_strong': 'rgba(0, 0, 0, 0.12)',
    'control': 'rgba(255, 255, 255, 0.55)',
    'titlebar_hover': 'rgba(0, 0, 0, 0.05)',
    'close_hover': '#E81123',
    'card_bg': 'rgba(255, 255, 255, 0.65)',
    'input_bg': 'rgba(255, 255, 255, 0.7)',
    'input_hover': 'rgba(255, 255, 255, 0.85)',
}

# 深色主题配色
COLORS_DARK = {
    'bg_solid': '#202020',
    'surface': 'rgba(40, 40, 40, 0.50)',
    'surface_solid': 'rgba(40, 40, 40, 0.85)',
    'accent': '#60CDFF',
    'accent_hover': '#7AD4FF',
    'accent_pressed': '#4AC0F2',
    'text': '#FFFFFF',
    'text_secondary': '#B0B0B0',  # 提高亮度，让 Tab 标题更清晰
    'text_on_accent': '#000000',
    'border': 'rgba(255, 255, 255, 0.08)',
    'border_strong': 'rgba(255, 255, 255, 0.15)',
    'control': 'rgba(255, 255, 255, 0.06)',
    'titlebar_hover': 'rgba(255, 255, 255, 0.08)',
    'close_hover': '#E81123',
    'card_bg': 'rgba(50, 50, 50, 0.65)',
    'input_bg': 'rgba(60, 60, 60, 0.7)',
    'input_hover': 'rgba(70, 70, 70, 0.85)',
}

# 当前使用的配色（默认浅色）
COLORS = COLORS_LIGHT.copy()

def set_dark_mode(dark: bool):
    """切换深色/浅色模式"""
    global COLORS
    COLORS.clear()
    COLORS.update(COLORS_DARK if dark else COLORS_LIGHT)


def get_stylesheet(dark_mode: bool = False) -> str:
    """获取全局样式表"""
    c = COLORS_DARK if dark_mode else COLORS_LIGHT
    return f"""
        * {{ font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif; font-size: 13px; }}
        QMainWindow, QWidget#central {{ background: transparent; }}
        QWidget {{ background: transparent; }}
        QLabel {{ color: {c['text']}; background: transparent; border: none; }}
        
        QFrame#card {{
            background: {c['card_bg']};
            border: none;
            border-radius: 8px;
        }}
        
        QLineEdit {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 8px 12px;
            color: {c['text']};
        }}
        QLineEdit:hover {{ background: {c['input_hover']}; }}
        QLineEdit:focus {{ border-color: {c['accent']}; }}
        
        QComboBox {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 8px 12px;
            padding-right: 30px;
            color: {c['text']};
        }}
        QComboBox:hover {{ background: {c['input_hover']}; }}
        QComboBox::drop-down {{ border: none; width: 30px; }}
        QComboBox::down-arrow {{ image: none; }}
        QComboBox QAbstractItemView {{
            background: {c['input_hover']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 4px;
            selection-background-color: {c['accent']};
            selection-color: {c['text_on_accent']};
        }}
        
        QSpinBox {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 6px 10px;
            color: {c['text']};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{ background: transparent; border: none; width: 20px; }}
        
        QSlider {{ background: transparent; border: none; min-height: 24px; }}
        QSlider::groove:horizontal {{ background: {c['border_strong']}; height: 4px; border-radius: 2px; }}
        QSlider::handle:horizontal {{ background: {c['accent']}; width: 18px; height: 18px; margin: -7px 0; border-radius: 9px; }}
        QSlider::sub-page:horizontal {{ background: {c['accent']}; border-radius: 2px; }}
        
        QProgressBar {{ background: {c['border_strong']}; border: none; border-radius: 2px; height: 4px; }}
        QProgressBar::chunk {{ background: {c['accent']}; border-radius: 2px; }}
        
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; border: none; }}
        QScrollBar::handle:vertical {{ background: {c['border_strong']}; border-radius: 5px; min-height: 30px; margin: 2px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['text_secondary']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        
        QTabWidget {{ background: transparent; border: none; }}
        QTabWidget::pane {{ background: transparent; border: none; }}
        QTabBar {{ background: transparent; border: none; }}
        QTabBar::tab {{
            background: transparent;
            color: {c['text_secondary']};
            padding: 10px 20px;
            margin-right: 4px;
            border: none;
            border-bottom: 2px solid transparent;
        }}
        QTabBar::tab:selected {{ color: {c['accent']}; border-bottom-color: {c['accent']}; }}
        QTabBar::tab:hover:!selected {{ color: {c['text']}; background: {c['titlebar_hover']}; }}
        
        /* 弹窗样式 */
        QMessageBox {{
            background: {c['surface_solid']};
        }}
        QMessageBox QLabel {{
            color: {c['text']};
            background: transparent;
        }}
        QMessageBox QPushButton {{
            background: {c['control']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 6px 16px;
            min-width: 60px;
        }}
        QMessageBox QPushButton:hover {{
            background: {c['input_hover']};
        }}
        QMessageBox QPushButton:pressed {{
            background: {c['input_bg']};
        }}
    """


def get_button_styles(dark_mode: bool = False):
    """获取按钮样式"""
    c = COLORS_DARK if dark_mode else COLORS_LIGHT
    
    primary = f"""
        QPushButton {{
            background: {c['accent']};
            color: {c['text_on_accent']};
            border: none;
            border-radius: 4px;
            padding: 8px 20px;
            font-weight: 500;
        }}
        QPushButton:hover {{ background: {c['accent_hover']}; }}
        QPushButton:pressed {{ background: {c['accent_pressed']}; }}
        QPushButton:disabled {{ background: {c['border_strong']}; color: {c['text_secondary']}; }}
    """
    
    secondary = f"""
        QPushButton {{
            background: {c['control']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 8px 16px;
        }}
        QPushButton:hover {{ background: {c['input_hover']}; }}
        QPushButton:pressed {{ background: {c['input_bg']}; }}
        QPushButton:checked {{ background: {c['accent']}; color: {c['text_on_accent']}; border-color: {c['accent']}; }}
        QPushButton:disabled {{ color: {c['text_secondary']}; }}
    """
    
    return primary, secondary


# 默认按钮样式（浅色模式）
PRIMARY_BTN = f"""
    QPushButton {{
        background: {COLORS_LIGHT['accent']};
        color: {COLORS_LIGHT['text_on_accent']};
        border: none;
        border-radius: 4px;
        padding: 8px 20px;
        font-weight: 500;
    }}
    QPushButton:hover {{ background: {COLORS_LIGHT['accent_hover']}; }}
    QPushButton:pressed {{ background: {COLORS_LIGHT['accent_pressed']}; }}
    QPushButton:disabled {{ background: rgba(0,0,0,0.1); color: rgba(0,0,0,0.3); }}
"""

SECONDARY_BTN = f"""
    QPushButton {{
        background: rgba(255,255,255,0.6);
        color: {COLORS_LIGHT['text']};
        border: 1px solid {COLORS_LIGHT['border']};
        border-radius: 4px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{ background: rgba(255,255,255,0.8); }}
    QPushButton:pressed {{ background: rgba(255,255,255,0.95); }}
    QPushButton:checked {{ background: {COLORS_LIGHT['accent']}; color: white; border-color: {COLORS_LIGHT['accent']}; }}
    QPushButton:disabled {{ color: rgba(0,0,0,0.3); }}
"""

# 标题栏按钮
TITLEBAR_BTN = f"""
    QPushButton {{
        background: transparent;
        border: none;
        border-radius: 0;
        color: {COLORS_LIGHT['text']};
        font-size: 10px;
        font-family: "Segoe MDL2 Assets", "Segoe UI Symbol", sans-serif;
    }}
    QPushButton:hover {{ background: {COLORS_LIGHT['titlebar_hover']}; }}
    QPushButton:pressed {{ background: rgba(0, 0, 0, 0.1); }}
"""

CLOSE_BTN = f"""
    QPushButton {{
        background: transparent;
        border: none;
        border-radius: 0;
        color: {COLORS_LIGHT['text']};
        font-size: 10px;
        font-family: "Segoe MDL2 Assets", "Segoe UI Symbol", sans-serif;
    }}
    QPushButton:hover {{ background: {COLORS_LIGHT['close_hover']}; color: white; }}
    QPushButton:pressed {{ background: #F1707A; color: white; }}
"""

# 卡片样式
def get_card_style(opacity: int = 200) -> str:
    alpha = min(0.5 + (255 - opacity) / 255 * 0.35, 0.85)
    return f"background: rgba(255,255,255,{alpha}); border: 1px solid {COLORS_LIGHT['border']}; border-radius: 8px;"

# 文字样式 - 动态获取
def get_subtitle_style(dark_mode: bool = False) -> str:
    c = COLORS_DARK if dark_mode else COLORS_LIGHT
    return f"font-size: 14px; font-weight: 600; color: {c['text']};"

def get_caption_style(dark_mode: bool = False) -> str:
    c = COLORS_DARK if dark_mode else COLORS_LIGHT
    return f"font-size: 12px; color: {c['text_secondary']};"

# 默认样式（浅色模式）
TITLE_STYLE = f"font-size: 22px; font-weight: 600; color: {COLORS_LIGHT['text']};"
SUBTITLE_STYLE = f"font-size: 14px; font-weight: 600; color: {COLORS_LIGHT['text']};"
CAPTION_STYLE = f"font-size: 12px; color: {COLORS_LIGHT['text_secondary']};"

# 胶囊形 Toggle 开关样式
def get_toggle_style(dark_mode: bool = False) -> str:
    c = COLORS_DARK if dark_mode else COLORS_LIGHT
    # 关闭状态：灰色背景
    # 开启状态：accent 颜色背景
    return f"""
        QPushButton {{
            background: {c['border_strong']};
            border: none;
            border-radius: 11px;
            min-width: 44px;
            max-width: 44px;
            min-height: 22px;
            max-height: 22px;
            padding: 0px;
        }}
        QPushButton:checked {{
            background: {c['accent']};
        }}
    """
