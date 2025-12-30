"""
回退管理模块

管理操作历史和回退功能，支持将分类后的图片恢复到原始位置。
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from .models import MoveRecord, RollbackResult


class RollbackManager:
    """管理操作历史和回退功能"""
    
    def __init__(self):
        """初始化回退管理器"""
        self._records: list[MoveRecord] = []
        self._created_folders: list[str] = []
    
    @property
    def records(self) -> list[MoveRecord]:
        """获取移动记录列表的副本"""
        return self._records.copy()
    
    @property
    def created_folders(self) -> list[str]:
        """获取创建的文件夹列表的副本"""
        return self._created_folders.copy()
    
    def record_move(self, record: MoveRecord) -> None:
        """
        记录一次移动操作
        
        Args:
            record: 移动操作记录
        """
        self._records.append(record)
    
    def record_folder_creation(self, folder_path: str) -> None:
        """
        记录创建的文件夹
        
        Args:
            folder_path: 文件夹路径
        """
        # 避免重复记录
        if folder_path not in self._created_folders:
            self._created_folders.append(folder_path)
    
    def rollback(self) -> RollbackResult:
        """
        执行回退操作，将所有图片恢复到原始位置
        
        Returns:
            RollbackResult: 回退结果，包含成功/失败数量
        """
        result = RollbackResult()
        
        # 按时间戳逆序回退（后移动的先恢复）
        sorted_records = sorted(self._records, key=lambda r: r.timestamp, reverse=True)
        
        for record in sorted_records:
            try:
                dest_path = Path(record.destination_path)
                source_path = Path(record.source_path)
                
                # 检查目标文件是否存在（即当前位置的文件）
                if not dest_path.exists():
                    # 文件已被删除或移动，记录失败
                    result.failed_count += 1
                    result.failed_files.append(record.destination_path)
                    continue
                
                # 确保原始位置的父目录存在
                source_parent = source_path.parent
                if not source_parent.exists():
                    source_parent.mkdir(parents=True, exist_ok=True)
                
                # 检查原始位置是否已有同名文件
                if source_path.exists():
                    # 原始位置已有文件，跳过并记录失败
                    result.failed_count += 1
                    result.failed_files.append(record.source_path)
                    continue
                
                # 移动文件回原始位置
                shutil.move(str(dest_path), str(source_path))
                result.success_count += 1
                
            except (PermissionError, OSError) as e:
                # 权限错误或其他OS错误
                result.failed_count += 1
                result.failed_files.append(record.destination_path)
        
        # 删除创建的空文件夹（逆序删除，先删除子文件夹）
        sorted_folders = sorted(self._created_folders, key=len, reverse=True)
        for folder_path in sorted_folders:
            try:
                folder = Path(folder_path)
                if folder.exists() and folder.is_dir():
                    # 只删除空文件夹
                    if not any(folder.iterdir()):
                        folder.rmdir()
            except (PermissionError, OSError):
                # 忽略删除文件夹时的错误
                pass
        
        # 清空记录
        self.clear()
        
        return result
    
    def clear(self) -> None:
        """清空操作记录"""
        self._records.clear()
        self._created_folders.clear()
    
    def has_records(self) -> bool:
        """
        检查是否有操作记录
        
        Returns:
            bool: 如果有记录返回True，否则返回False
        """
        return len(self._records) > 0
    
    def get_record_count(self) -> int:
        """
        获取移动记录数量
        
        Returns:
            int: 记录数量
        """
        return len(self._records)
