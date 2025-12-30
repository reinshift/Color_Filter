"""
直方图分析模块

分析直方图特征，进行影调分类和统计计算。
"""

import numpy as np
from typing import Optional

from .models import TonalClass, LightnessStats


class HistogramAnalyzer:
    """
    直方图分析器
    
    分析明度直方图，进行影调分类和统计计算。
    """
    
    def __init__(self,
                 high_key_threshold: float = 170,
                 low_key_threshold: float = 85):
        """
        初始化直方图分析器
        
        Args:
            high_key_threshold: 高调判定阈值（明度均值）
            low_key_threshold: 低调判定阈值（明度均值）
        """
        self.high_key_threshold = high_key_threshold
        self.low_key_threshold = low_key_threshold
    
    def classify_tonal_range(self, lightness_hist: np.ndarray) -> TonalClass:
        """
        根据明度直方图分类影调
        
        Args:
            lightness_hist: 归一化的明度直方图
            
        Returns:
            TonalClass 枚举值
        """
        # 计算加权平均明度
        bins = len(lightness_hist)
        bin_centers = np.arange(bins) * (256 / bins) + (256 / bins / 2)
        mean_lightness = np.sum(lightness_hist * bin_centers)
        
        if mean_lightness > self.high_key_threshold:
            return TonalClass.HIGH_KEY
        elif mean_lightness < self.low_key_threshold:
            return TonalClass.LOW_KEY
        else:
            return TonalClass.MID_KEY
    
    def compute_lightness_stats(self, lightness_hist: np.ndarray) -> LightnessStats:
        """
        从直方图计算明度统计量
        
        Args:
            lightness_hist: 归一化的明度直方图
            
        Returns:
            LightnessStats 对象
        """
        bins = len(lightness_hist)
        bin_centers = np.arange(bins) * (256 / bins) + (256 / bins / 2)
        
        # 加权平均
        mean = np.sum(lightness_hist * bin_centers)
        
        # 加权标准差
        variance = np.sum(lightness_hist * (bin_centers - mean) ** 2)
        std = np.sqrt(variance)
        
        # 加权偏度
        if std > 0:
            skewness = np.sum(lightness_hist * ((bin_centers - mean) / std) ** 3)
        else:
            skewness = 0.0
        
        return LightnessStats(mean=mean, std=std, skewness=skewness)
    
    def compute_contrast(self, lightness_hist: np.ndarray) -> float:
        """
        计算对比度（基于明度分布的标准差）
        
        Args:
            lightness_hist: 归一化的明度直方图
            
        Returns:
            对比度值（标准差）
        """
        stats = self.compute_lightness_stats(lightness_hist)
        return stats.std
    
    def compute_dynamic_range(self, lightness_hist: np.ndarray, 
                              percentile_low: float = 5,
                              percentile_high: float = 95) -> float:
        """
        计算动态范围（明度分布的有效范围）
        
        Args:
            lightness_hist: 归一化的明度直方图
            percentile_low: 低百分位
            percentile_high: 高百分位
            
        Returns:
            动态范围值
        """
        # 计算累积分布
        cdf = np.cumsum(lightness_hist)
        
        bins = len(lightness_hist)
        bin_values = np.arange(bins) * (256 / bins)
        
        # 找到百分位对应的明度值
        low_idx = np.searchsorted(cdf, percentile_low / 100)
        high_idx = np.searchsorted(cdf, percentile_high / 100)
        
        low_value = bin_values[min(low_idx, bins - 1)]
        high_value = bin_values[min(high_idx, bins - 1)]
        
        return high_value - low_value
