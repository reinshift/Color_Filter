"""
数据模型模块

定义图片颜色分类器使用的所有数据类和枚举类型。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np


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


# ============ 高级分类算法相关枚举 ============

class TonalClass(Enum):
    """影调分类枚举"""
    HIGH_KEY = "高调"    # 明亮，高光为主
    MID_KEY = "中调"     # 中等亮度
    LOW_KEY = "低调"     # 暗沉，阴影为主


class HueCategory(Enum):
    """色调类别枚举"""
    WARM = "暖色"        # 红、橙、黄
    COOL = "冷色"        # 蓝、青、紫
    NEUTRAL = "中性"     # 绿、灰、无彩色


class SaturationLevel(Enum):
    """饱和度水平枚举"""
    VIVID = "鲜艳"       # 高饱和度
    MODERATE = "适中"    # 中等饱和度
    MUTED = "柔和"       # 低饱和度
    NEUTRAL = "中性"     # 接近灰色


class DistanceMetric(Enum):
    """直方图距离度量枚举"""
    INTERSECTION = "intersection"      # 直方图交叉
    CHI_SQUARE = "chi_square"          # 卡方距离
    BHATTACHARYYA = "bhattacharyya"    # 巴氏距离
    CORRELATION = "correlation"        # 相关性


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


# ============ 高级分类算法相关数据类 ============

@dataclass
class LightnessStats:
    """明度统计信息"""
    mean: float          # 平均明度
    std: float           # 标准差
    skewness: float      # 偏度


@dataclass
class DominantColor:
    """主色调信息（LAB空间）"""
    lab: tuple[float, float, float]  # LAB 颜色值
    percentage: float                 # 占比 (0-100)


@dataclass
class ImageFeatures:
    """图片多维度特征"""
    image_path: str
    # 直方图特征（归一化为概率分布）
    hue_histogram: np.ndarray           # 色调直方图 (180,)
    lightness_histogram: np.ndarray     # 明度直方图 (256,)
    saturation_histogram: np.ndarray    # 饱和度直方图 (256,)
    # 主色调
    dominant_colors: list[DominantColor]  # 主色调列表
    # 影调分类
    tonal_class: TonalClass
    # 统计信息
    lightness_stats: LightnessStats
    saturation_mean: float              # 平均饱和度 (0-255)


@dataclass
class FeatureWeights:
    """特征权重配置"""
    hue: float = 0.4           # 色调权重
    lightness: float = 0.35    # 明度权重
    saturation: float = 0.25   # 饱和度权重
    
    def normalize(self) -> 'FeatureWeights':
        """归一化权重，使总和为1"""
        total = self.hue + self.lightness + self.saturation
        if total > 0:
            return FeatureWeights(
                hue=self.hue / total,
                lightness=self.lightness / total,
                saturation=self.saturation / total
            )
        return FeatureWeights()


@dataclass
class ClusterInfo:
    """聚类信息"""
    cluster_id: int
    name: str                           # 类别名称，如"高调暖色"
    image_paths: list[str]              # 该类别包含的图片路径
    tonal_class: TonalClass             # 主导影调
    hue_category: HueCategory           # 主导色调
    saturation_level: SaturationLevel   # 饱和度水平
    image_count: int = 0                # 图片数量


@dataclass
class AdvancedClassificationResult:
    """高级分类结果"""
    clusters: list[ClusterInfo] = field(default_factory=list)
    n_clusters: int = 0
    silhouette_score: float = 0.0       # 轮廓系数，衡量聚类质量
    total_images: int = 0
    processing_time: float = 0.0        # 处理时间（秒）
    move_records: list[MoveRecord] = field(default_factory=list)
    
    @property
    def category_counts(self) -> dict[str, int]:
        """兼容旧接口：返回类别计数字典"""
        return {c.name: c.image_count for c in self.clusters}
    
    @property
    def total_processed(self) -> int:
        """兼容旧接口：返回处理总数"""
        return self.total_images
    
    @property
    def total_failed(self) -> int:
        """兼容旧接口：返回失败数（高级模式暂不统计）"""
        return 0
