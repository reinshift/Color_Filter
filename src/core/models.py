"""
数据模型模块

定义图片颜色分类器使用的所有数据类和枚举类型。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ColorCategory(Enum):
    """颜色类别枚举"""
    RED = "红色"
    ORANGE = "橙色"
    YELLOW = "黄色"
    GREEN = "绿色"
    CYAN = "青色"
    BLUE = "蓝色"
    PURPLE = "紫色"
    PINK = "粉色"
    BROWN = "棕色"
    BLACK = "黑色"
    WHITE = "白色"
    GRAY = "灰色"
    OTHER = "其他"


@dataclass
class ScanResult:
    """扫描结果"""
    image_paths: list[str] = field(default_factory=list)
    total_count: int = 0
    skipped_count: int = 0
    error_files: list[str] = field(default_factory=list)


@dataclass
class ColorInfo:
    """单个颜色信息"""
    rgb: tuple[int, int, int]
    percentage: float
    category: str


@dataclass
class ColorExtractionResult:
    """颜色提取结果"""
    image_path: str
    colors: list[ColorInfo] = field(default_factory=list)
    dominant_category: str = ""


@dataclass
class MoveRecord:
    """移动操作记录"""
    source_path: str
    destination_path: str
    timestamp: float


@dataclass
class RollbackResult:
    """回退操作结果"""
    success_count: int = 0
    failed_count: int = 0
    failed_files: list[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """分类结果"""
    category_counts: dict[str, int] = field(default_factory=dict)
    total_processed: int = 0
    total_failed: int = 0
    move_records: list[MoveRecord] = field(default_factory=list)
