"""
分类引擎模块

集成所有核心模块，协调整个图片颜色分类流程。
"""

import logging
import os
from pathlib import Path
from typing import Optional, Callable, TYPE_CHECKING

from .scanner import ImageScanner, PathNotFoundError, AccessDeniedError
from .extractor import ColorExtractor
from .category_manager import CategoryManager
from .rollback_manager import RollbackManager
from .models import (
    ScanResult,
    ColorExtractionResult,
    ClassificationResult,
    RollbackResult,
    MoveRecord,
)

# Lazy import for ProgressTracker to avoid PyQt6 import issues
if TYPE_CHECKING:
    from .progress_tracker import ProgressTracker


# 配置日志
logger = logging.getLogger(__name__)


class ClassificationEngine:
    """
    分类引擎，协调整个图片颜色分类流程
    
    集成 ImageScanner, ColorExtractor, CategoryManager, RollbackManager, ProgressTracker
    提供统一的分类和回退接口。
    """
    
    def __init__(
        self,
        n_colors: int = 3,
        resize_size: tuple[int, int] = (150, 150),
    ):
        """
        初始化分类引擎
        
        Args:
            n_colors: 要提取的主色数量
            resize_size: 颜色分析前缩放图片的尺寸
        """
        self._scanner = ImageScanner()
        self._extractor = ColorExtractor(n_colors=n_colors, resize_size=resize_size)
        self._rollback_manager = RollbackManager()
        self._category_manager: Optional[CategoryManager] = None
        self._progress_tracker: Optional[ProgressTracker] = None
        self._is_running = False
    
    @property
    def scanner(self) -> ImageScanner:
        """获取图片扫描器"""
        return self._scanner
    
    @property
    def extractor(self) -> ColorExtractor:
        """获取颜色提取器"""
        return self._extractor
    
    @property
    def rollback_manager(self) -> RollbackManager:
        """获取回退管理器"""
        return self._rollback_manager
    
    @property
    def category_manager(self) -> Optional[CategoryManager]:
        """获取分类管理器"""
        return self._category_manager
    
    @property
    def progress_tracker(self) -> Optional["ProgressTracker"]:
        """获取进度追踪器"""
        return self._progress_tracker
    
    @property
    def is_running(self) -> bool:
        """检查分类是否正在进行"""
        return self._is_running
    
    def classify(
        self,
        source_path: str,
        target_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> ClassificationResult:
        """
        执行图片颜色分类
        
        协调整个分类流程：
        1. 扫描源目录获取所有图片
        2. 为每张图片提取主色调
        3. 根据主色调将图片移动到对应类别文件夹
        4. 记录所有操作以支持回退
        
        Args:
            source_path: 源图片目录路径
            target_path: 目标分类目录路径，如果为None则使用源目录
            progress_callback: 进度回调函数，接收 (current, total, current_file) 参数
            
        Returns:
            ClassificationResult: 分类结果，包含各类别数量和移动记录
            
        Raises:
            PathNotFoundError: 源路径不存在
            AccessDeniedError: 无访问权限
            RuntimeError: 分类正在进行中
        """
        if self._is_running:
            raise RuntimeError("分类操作正在进行中")
        
        self._is_running = True
        
        try:
            # 清空之前的回退记录
            self._rollback_manager.clear()
            
            # 确定目标路径
            if target_path is None:
                target_path = source_path
            
            # 初始化分类管理器
            self._category_manager = CategoryManager(target_path)
            
            # 步骤1: 扫描图片
            logger.info(f"开始扫描目录: {source_path}")
            scan_result = self._scanner.scan(source_path)
            
            if scan_result.total_count == 0:
                logger.info("未找到任何图片文件")
                return ClassificationResult(
                    category_counts={},
                    total_processed=0,
                    total_failed=0,
                    move_records=[],
                )
            
            logger.info(f"找到 {scan_result.total_count} 张图片")
            
            # 初始化进度追踪器 (lazy import to avoid PyQt6 issues)
            from .progress_tracker import ProgressTracker
            self._progress_tracker = ProgressTracker(scan_result.total_count)
            
            # 创建分类结果
            result = ClassificationResult()
            
            # 步骤2 & 3: 处理每张图片
            for idx, image_path in enumerate(scan_result.image_paths):
                current_file = os.path.basename(image_path)
                
                # 更新进度
                if progress_callback:
                    progress_callback(idx, scan_result.total_count, current_file)
                self._progress_tracker.update(idx, current_file)
                
                try:
                    # 提取颜色
                    extraction_result = self._extractor.extract_colors(image_path)
                    category = extraction_result.dominant_category
                    
                    # 移动图片到对应类别文件夹
                    move_record = self._category_manager.move_image(image_path, category)
                    
                    # 记录移动操作
                    self._rollback_manager.record_move(move_record)
                    result.move_records.append(move_record)
                    
                    # 更新类别计数
                    if category not in result.category_counts:
                        result.category_counts[category] = 0
                    result.category_counts[category] += 1
                    
                    result.total_processed += 1
                    logger.debug(f"已分类: {current_file} -> {category}")
                    
                except Exception as e:
                    logger.warning(f"处理图片失败 {image_path}: {e}")
                    result.total_failed += 1
            
            # 记录创建的文件夹
            for folder in self._category_manager.created_folders:
                self._rollback_manager.record_folder_creation(folder)
            
            # 完成进度
            if progress_callback:
                progress_callback(
                    scan_result.total_count,
                    scan_result.total_count,
                    "完成"
                )
            self._progress_tracker.update(scan_result.total_count, "完成")
            
            logger.info(
                f"分类完成: 成功 {result.total_processed}, 失败 {result.total_failed}"
            )
            
            return result
            
        finally:
            self._is_running = False
    
    def rollback(self) -> RollbackResult:
        """
        执行回退操作，将所有图片恢复到原始位置
        
        Returns:
            RollbackResult: 回退结果，包含成功/失败数量
        """
        if self._is_running:
            raise RuntimeError("分类操作正在进行中，无法回退")
        
        if not self._rollback_manager.has_records():
            logger.info("没有可回退的操作记录")
            return RollbackResult(success_count=0, failed_count=0, failed_files=[])
        
        logger.info(f"开始回退 {self._rollback_manager.get_record_count()} 条记录")
        result = self._rollback_manager.rollback()
        logger.info(
            f"回退完成: 成功 {result.success_count}, 失败 {result.failed_count}"
        )
        
        return result
    
    def can_rollback(self) -> bool:
        """
        检查是否可以执行回退操作
        
        Returns:
            bool: 如果有可回退的记录返回True
        """
        return self._rollback_manager.has_records() and not self._is_running
    
    def get_rollback_count(self) -> int:
        """
        获取可回退的记录数量
        
        Returns:
            int: 记录数量
        """
        return self._rollback_manager.get_record_count()
