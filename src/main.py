"""
图片颜色分类器 - 应用入口

启动图片颜色分类器应用程序。
"""

import sys
import os

# 打包环境下设置 Qt 插件路径（必须在导入 PyQt6 之前）
if getattr(sys, 'frozen', False):
    # 打包后的路径
    base_path = sys._MEIPASS
    app_path = os.path.dirname(sys.executable)
    
    # 设置 Qt 插件路径
    qt_plugin_path = os.path.join(base_path, 'PyQt6', 'Qt6', 'plugins')
    if os.path.exists(qt_plugin_path):
        os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
        platforms_path = os.path.join(qt_plugin_path, 'platforms')
        if os.path.exists(platforms_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_path
else:
    # 开发环境路径
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """应用程序入口函数"""
    try:
        # 创建应用实例
        app = QApplication(sys.argv)
        app.setApplicationName("图片颜色分类器")
        app.setApplicationVersion("1.0.0")
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        # 运行事件循环
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        if getattr(sys, 'frozen', False):
            input("Press Enter to exit...")


if __name__ == "__main__":
    main()
