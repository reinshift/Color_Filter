"""
分类管理模块

管理图片分类和文件操作，包括创建类别文件夹、移动图片等功能。
"""

import os
import shutil
import time
from pathlib import Path
from typing import Optional

from .models import ColorCategory, MoveRecord


class CategoryManager:
    """管理图片分类和文件操作"""
    
    def __init__(self, base_path: str):
        """
        初始化分类管理器
        
        Args:
            base_path: 分类文件夹的基础路径
        """
        self._base_path = Path(base_path)
        self._created_folders: list[str] = []
    
    @property
    def base_path(self) -> Path:
        """获取基础路径"""
        return self._base_path
    
    @property
    def created_folders(self) -> list[str]:
        """获取已创建的文件夹列表"""
        return self._created_folders.copy()
    
    def create_category_folders(self, categories: Optional[list[str]] = None) -> list[str]:
        """
        创建颜色类别文件夹
        
        Args:
            categories: 要创建的类别列表，如果为None则创建所有预定义类别
            
        Returns:
            list[str]: 创建的文件夹路径列表
        """
        if categories is None:
            # 使用所有预定义的颜色类别
            categories = [cat.value for cat in ColorCategory]
        
        created = []
        for category in categories:
            folder_path = self._base_path / category
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                created.append(str(folder_path))
                self._created_folders.append(str(folder_path))
        
        return created
    
    def move_image(self, source: str, category: str) -> MoveRecord:
        """
        移动图片到对应类别文件夹
        
        Args:
            source: 源文件路径
            category: 目标颜色类别
            
        Returns:
            MoveRecord: 移动操作记录，用于回退
            
        Raises:
            FileNotFoundError: 源文件不存在
            PermissionError: 无权限移动文件
        """
        source_path = Path(source)
        
        if not source_path.exists():
            raise FileNotFoundError(f"源文件不存在: {source}")
        
        # 获取目标文件夹路径
        dest_folder = self._base_path / category
        
        # 确保目标文件夹存在
        if not dest_folder.exists():
            dest_folder.mkdir(parents=True, exist_ok=True)
            self._created_folders.append(str(dest_folder))
        
        # 处理文件名冲突
        dest_path = dest_folder / source_path.name
        dest_path = self._resolve_filename_conflict(dest_path)
        
        # 移动文件
        shutil.move(str(source_path), str(dest_path))
        
        # 创建移动记录
        record = MoveRecord(
            source_path=str(source_path),
            destination_path=str(dest_path),
            timestamp=time.time()
        )
        
        return record
    
    def get_category_path(self, category: str) -> str:
        """
        获取类别文件夹的完整路径
        
        Args:
            category: 颜色类别名称
            
        Returns:
            str: 类别文件夹的完整路径
        """
        return str(self._base_path / category)
    
    def _resolve_filename_conflict(self, dest_path: Path) -> Path:
        """
        解决文件名冲突，如果目标文件已存在则添加数字后缀
        
        Args:
            dest_path: 原始目标路径
            
        Returns:
            Path: 解决冲突后的目标路径
        """
        if not dest_path.exists():
            return dest_path
        
        # 分离文件名和扩展名
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        
        # 尝试添加数字后缀
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
