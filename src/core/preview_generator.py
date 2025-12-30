"""Preview generation module for image thumbnails."""

import os
from pathlib import Path
from typing import Optional

from PIL import Image
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class PreviewGenerator:
    """生成图片缩略图预览
    
    Attributes:
        THUMBNAIL_SIZE: Default thumbnail dimensions
        MAX_PREVIEW_COUNT: Maximum number of previews per category
    """
    
    THUMBNAIL_SIZE: tuple[int, int] = (100, 100)
    MAX_PREVIEW_COUNT: int = 6
    
    # Supported image formats
    SUPPORTED_FORMATS: tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    
    def __init__(self, thumbnail_size: Optional[tuple[int, int]] = None):
        """初始化预览生成器
        
        Args:
            thumbnail_size: Optional custom thumbnail size (width, height)
        """
        self._thumbnail_size = thumbnail_size or self.THUMBNAIL_SIZE
    
    def generate_thumbnail(self, image_path: str) -> Optional[QPixmap]:
        """生成单张图片的缩略图
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            QPixmap: 缩略图对象，如果生成失败则返回None
        """
        try:
            # Open and resize image using PIL
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (handles RGBA, P mode, etc.)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create thumbnail maintaining aspect ratio
                img.thumbnail(self._thumbnail_size, Image.Resampling.LANCZOS)
                
                # Convert PIL Image to QPixmap
                return self._pil_to_qpixmap(img)
                
        except Exception:
            return None
    
    def generate_category_preview(self, category_path: str) -> list[QPixmap]:
        """生成某个类别的预览缩略图列表
        
        Args:
            category_path: 类别文件夹路径
            
        Returns:
            list[QPixmap]: 缩略图列表（最多MAX_PREVIEW_COUNT张）
        """
        thumbnails: list[QPixmap] = []
        
        if not os.path.isdir(category_path):
            return thumbnails
        
        # Get all image files in the category folder
        image_files = self._get_image_files(category_path)
        
        # Generate thumbnails for up to MAX_PREVIEW_COUNT images
        for image_path in image_files[:self.MAX_PREVIEW_COUNT]:
            thumbnail = self.generate_thumbnail(image_path)
            if thumbnail is not None:
                thumbnails.append(thumbnail)
        
        return thumbnails
    
    def _get_image_files(self, directory: str) -> list[str]:
        """获取目录中的所有图片文件
        
        Args:
            directory: 目录路径
            
        Returns:
            list[str]: 图片文件路径列表
        """
        image_files: list[str] = []
        
        try:
            for entry in os.scandir(directory):
                if entry.is_file():
                    ext = Path(entry.name).suffix.lower()
                    if ext in self.SUPPORTED_FORMATS:
                        image_files.append(entry.path)
        except (OSError, PermissionError):
            pass
        
        # Sort for consistent ordering
        image_files.sort()
        return image_files
    
    def _pil_to_qpixmap(self, pil_image: Image.Image) -> QPixmap:
        """将PIL Image转换为QPixmap
        
        Args:
            pil_image: PIL Image对象
            
        Returns:
            QPixmap: Qt图像对象
        """
        # Convert PIL image to bytes
        data = pil_image.tobytes("raw", "RGB")
        
        # Create QImage from bytes
        qimage = QImage(
            data,
            pil_image.width,
            pil_image.height,
            pil_image.width * 3,  # bytes per line
            QImage.Format.Format_RGB888
        )
        
        # Convert to QPixmap
        return QPixmap.fromImage(qimage)
    
    def get_image_count(self, category_path: str) -> int:
        """获取类别文件夹中的图片数量
        
        Args:
            category_path: 类别文件夹路径
            
        Returns:
            int: 图片数量
        """
        return len(self._get_image_files(category_path))
