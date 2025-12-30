"""
图片扫描模块

提供图片文件扫描功能，支持递归扫描目录并验证图片格式。
"""

import os
import logging
from pathlib import Path
from typing import Optional

from PIL import Image

from .models import ScanResult


# 配置日志
logger = logging.getLogger(__name__)


class PathNotFoundError(Exception):
    """路径不存在异常"""
    
    def __init__(self, path: str, message: Optional[str] = None):
        self.path = path
        self.message = message or f"路径不存在: {path}"
        super().__init__(self.message)


class AccessDeniedError(Exception):
    """无访问权限异常"""
    
    def __init__(self, path: str, message: Optional[str] = None):
        self.path = path
        self.message = message or f"无法访问路径: {path}"
        super().__init__(self.message)


class ImageScanner:
    """扫描指定路径下的所有图片文件"""
    
    SUPPORTED_FORMATS: tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    
    def scan(self, path: str) -> ScanResult:
        """
        递归扫描指定路径下的所有图片
        
        Args:
            path: 要扫描的文件夹路径
            
        Returns:
            ScanResult: 包含图片路径列表和扫描统计信息
            
        Raises:
            PathNotFoundError: 路径不存在
            AccessDeniedError: 无访问权限
        """
        # 验证路径存在性
        if not os.path.exists(path):
            raise PathNotFoundError(path)
        
        # 验证访问权限
        if not os.access(path, os.R_OK):
            raise AccessDeniedError(path)
        
        # 如果是文件而不是目录
        if os.path.isfile(path):
            raise PathNotFoundError(path, f"路径不是目录: {path}")
        
        result = ScanResult()
        
        # 递归扫描目录
        try:
            for root, dirs, files in os.walk(path):
                # 检查目录访问权限
                if not os.access(root, os.R_OK):
                    logger.warning(f"无法访问目录: {root}")
                    continue
                
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    # 检查文件扩展名是否为支持的格式
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in self.SUPPORTED_FORMATS:
                        continue
                    
                    # 验证图片是否有效
                    if self.is_valid_image(file_path):
                        result.image_paths.append(file_path)
                        result.total_count += 1
                    else:
                        result.error_files.append(file_path)
                        result.skipped_count += 1
                        logger.warning(f"跳过损坏的图片文件: {file_path}")
                        
        except PermissionError as e:
            raise AccessDeniedError(path, f"扫描过程中权限被拒绝: {e}")
        
        return result
    
    def is_valid_image(self, file_path: str) -> bool:
        """
        检查文件是否为有效的图片文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 如果是有效图片返回True，否则返回False
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False
        
        # 检查文件是否可读
        if not os.access(file_path, os.R_OK):
            return False
        
        # 检查扩展名
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            return False
        
        # 尝试打开图片验证其有效性
        try:
            with Image.open(file_path) as img:
                # 验证图片可以被加载
                img.verify()
            return True
        except Exception as e:
            logger.debug(f"图片验证失败 {file_path}: {e}")
            return False
