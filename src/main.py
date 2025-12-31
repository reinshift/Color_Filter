"""
图片颜色分类器 - 入口
"""

import sys
import os

# 打包环境设置
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    qt_plugin = os.path.join(base_path, 'PyQt6', 'Qt6', 'plugins')
    if os.path.exists(qt_plugin):
        os.environ['QT_PLUGIN_PATH'] = qt_plugin
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui import MainWindow


def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("图片颜色分类器")
        
        # 设置字体
        font = QFont("Segoe UI", 10)
        if not font.exactMatch():
            font = QFont("Microsoft YaHei UI", 10)
        app.setFont(font)
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        if getattr(sys, 'frozen', False):
            input("Press Enter to exit...")


if __name__ == "__main__":
    main()
