"""
PyInstaller 运行时钩子
在应用启动前设置必要的环境变量
"""
import os
import sys

# 设置 Qt 路径（必须在 PyQt6 导入前执行）
if getattr(sys, 'frozen', False):
    # 获取应用程序目录
    app_path = os.path.dirname(sys.executable)
    meipass = getattr(sys, '_MEIPASS', app_path)
    
    # Qt6 bin 目录（包含 Qt6Core.dll 等）
    qt_bin_path = os.path.join(meipass, 'PyQt6', 'Qt6', 'bin')
    if os.path.exists(qt_bin_path):
        # 添加到 PATH 环境变量
        current_path = os.environ.get('PATH', '')
        os.environ['PATH'] = qt_bin_path + os.pathsep + current_path
    
    # 可能的 Qt 插件路径
    possible_paths = [
        os.path.join(meipass, 'PyQt6', 'Qt6', 'plugins'),
        os.path.join(app_path, 'PyQt6', 'Qt6', 'plugins'),
        os.path.join(meipass, 'plugins'),
        os.path.join(app_path, 'plugins'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            os.environ['QT_PLUGIN_PATH'] = path
            break
    
    # 设置平台插件路径
    for path in possible_paths:
        platforms_path = os.path.join(path, 'platforms')
        if os.path.exists(platforms_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_path
            break
