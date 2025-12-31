"""
Windows 亚克力/毛玻璃效果模块

使用 Windows API SetWindowCompositionAttribute 实现亚克力模糊效果
支持 Windows 10 1803+ 和 Windows 11
"""

import sys
import ctypes
from ctypes import wintypes, Structure, POINTER, byref, sizeof, c_int
from ctypes.wintypes import DWORD, HWND


class ACCENT_STATE:
    """窗口效果状态"""
    ACCENT_DISABLED = 0
    ACCENT_ENABLE_GRADIENT = 1
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
    ACCENT_ENABLE_BLURBEHIND = 3  # Aero 模糊
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4  # 亚克力模糊
    ACCENT_INVALID_STATE = 5


class ACCENT_POLICY(Structure):
    """亚克力效果策略结构"""
    _fields_ = [
        ("AccentState", DWORD),
        ("AccentFlags", DWORD),
        ("GradientColor", DWORD),
        ("AnimationId", DWORD),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    """窗口组合属性数据结构"""
    _fields_ = [
        ("Attribute", DWORD),
        ("Data", POINTER(ACCENT_POLICY)),
        ("SizeOfData", ctypes.c_size_t),
    ]


# Windows Composition Attribute
WCA_ACCENT_POLICY = 19

# DWM 窗口属性
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2  # 圆角
DWMWCP_ROUNDSMALL = 3  # 小圆角


def _get_hwnd(widget) -> int:
    """获取 PyQt 窗口句柄"""
    try:
        return int(widget.winId())
    except Exception:
        return 0


def enable_rounded_corners(widget, small: bool = False) -> bool:
    """
    启用 Windows 11 圆角窗口
    
    Args:
        widget: PyQt 窗口对象
        small: 是否使用小圆角
        
    Returns:
        是否成功启用
    """
    if sys.platform != 'win32':
        return False
    
    hwnd = _get_hwnd(widget)
    if not hwnd:
        return False
    
    try:
        dwmapi = ctypes.windll.dwmapi
        preference = DWMWCP_ROUNDSMALL if small else DWMWCP_ROUND
        value = c_int(preference)
        result = dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_WINDOW_CORNER_PREFERENCE,
            byref(value),
            sizeof(value)
        )
        return result == 0
    except Exception:
        # 静默失败，不影响窗口显示
        return False


def enable_acrylic(widget, color: int = 0x99F0F0F0) -> bool:
    """
    启用亚克力模糊效果
    
    Args:
        widget: PyQt 窗口对象
        color: ABGR 格式颜色值，默认为半透明灰白色
               格式: 0xAABBGGRR (Alpha, Blue, Green, Red)
               
    Returns:
        是否成功启用
    """
    if sys.platform != 'win32':
        return False
    
    hwnd = _get_hwnd(widget)
    if not hwnd:
        return False
    
    try:
        user32 = ctypes.windll.user32
        SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
        SetWindowCompositionAttribute.argtypes = [HWND, POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
        SetWindowCompositionAttribute.restype = ctypes.c_int
        
        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2  # 绘制所有边框
        accent.GradientColor = color
        accent.AnimationId = 0
        
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = sizeof(accent)
        
        result = SetWindowCompositionAttribute(hwnd, byref(data))
        return result != 0
        
    except Exception:
        # 静默失败，不影响窗口显示
        return False
