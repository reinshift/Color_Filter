"""
相似度计算模块

计算图片之间的相似度，支持多种直方图距离度量。
"""

import numpy as np
from typing import Optional

from .models import (
    ImageFeatures,
    FeatureWeights,
    DistanceMetric
)


class SimilarityCalculator:
    """
    相似度计算器
    
    计算图片之间的相似度，支持多种直方图距离度量：
    - 直方图交叉 (Histogram Intersection)
    - 卡方距离 (Chi-Square Distance)
    - 巴氏距离 (Bhattacharyya Distance)
    - 相关性 (Correlation)
    """
    
    def __init__(self,
                 weights: Optional[FeatureWeights] = None,
                 metric: DistanceMetric = DistanceMetric.BHATTACHARYYA):
        """
        初始化相似度计算器
        
        Args:
            weights: 特征权重配置，None 则使用默认权重
            metric: 默认距离度量方法
        """
        self.weights = weights if weights else FeatureWeights()
        self.metric = metric
    
    def histogram_intersection(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """
        直方图交叉相似度
        
        intersection = sum(min(h1, h2))
        值越大表示越相似，范围 [0, 1]（对于归一化直方图）
        
        Args:
            hist1: 第一个直方图（归一化）
            hist2: 第二个直方图（归一化）
            
        Returns:
            相似度值 [0, 1]
        """
        return float(np.sum(np.minimum(hist1, hist2)))
    
    def chi_square_distance(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """
        卡方距离
        
        chi_square = sum((h1-h2)^2 / (h1+h2+eps))
        值越小表示越相似，范围 [0, +inf)
        
        Args:
            hist1: 第一个直方图（归一化）
            hist2: 第二个直方图（归一化）
            
        Returns:
            距离值 [0, +inf)
        """
        eps = 1e-10
        denominator = hist1 + hist2 + eps
        return float(np.sum((hist1 - hist2) ** 2 / denominator))
    
    def bhattacharyya_distance(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """
        巴氏距离
        
        bhattacharyya = -ln(sum(sqrt(h1*h2)))
        值越小表示越相似，范围 [0, +inf)
        
        Args:
            hist1: 第一个直方图（归一化）
            hist2: 第二个直方图（归一化）
            
        Returns:
            距离值 [0, +inf)
        """
        bc = np.sum(np.sqrt(hist1 * hist2))
        # 防止 log(0)
        bc = np.clip(bc, 1e-10, 1.0)
        return float(-np.log(bc))
    
    def correlation_similarity(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """
        相关性相似度
        
        correlation = sum((h1-mean1)*(h2-mean2)) / (std1*std2*N)
        值越大表示越相似，范围 [-1, 1]
        
        Args:
            hist1: 第一个直方图（归一化）
            hist2: 第二个直方图（归一化）
            
        Returns:
            相关性值 [-1, 1]
        """
        mean1 = np.mean(hist1)
        mean2 = np.mean(hist2)
        
        h1_centered = hist1 - mean1
        h2_centered = hist2 - mean2
        
        numerator = np.sum(h1_centered * h2_centered)
        denominator = np.sqrt(np.sum(h1_centered ** 2) * np.sum(h2_centered ** 2))
        
        if denominator < 1e-10:
            return 0.0
        
        return float(numerator / denominator)

    def compute_histogram_distance(self, hist1: np.ndarray, hist2: np.ndarray,
                                   metric: Optional[DistanceMetric] = None) -> float:
        """
        计算直方图距离
        
        Args:
            hist1: 第一个直方图（归一化）
            hist2: 第二个直方图（归一化）
            metric: 距离度量方法，None 则使用默认方法
            
        Returns:
            距离值（已转换为 [0, 1] 范围，0 表示完全相同）
        """
        if metric is None:
            metric = self.metric
        
        if metric == DistanceMetric.INTERSECTION:
            # 交叉是相似度，转换为距离
            return 1.0 - self.histogram_intersection(hist1, hist2)
        
        elif metric == DistanceMetric.CHI_SQUARE:
            # 卡方距离，归一化到 [0, 1]
            dist = self.chi_square_distance(hist1, hist2)
            # 使用 sigmoid 风格的归一化
            return 1.0 - np.exp(-dist)
        
        elif metric == DistanceMetric.BHATTACHARYYA:
            # 巴氏距离，归一化到 [0, 1]
            dist = self.bhattacharyya_distance(hist1, hist2)
            return 1.0 - np.exp(-dist)
        
        elif metric == DistanceMetric.CORRELATION:
            # 相关性是相似度 [-1, 1]，转换为距离 [0, 1]
            corr = self.correlation_similarity(hist1, hist2)
            return (1.0 - corr) / 2.0
        
        else:
            raise ValueError(f"不支持的距离度量: {metric}")
    
    def compute_similarity(self, features1: ImageFeatures, features2: ImageFeatures) -> float:
        """
        计算两张图片的综合相似度
        
        结合色调、明度、饱和度三个通道的直方图距离，
        使用配置的权重进行加权平均。
        
        Args:
            features1: 第一张图片的特征
            features2: 第二张图片的特征
            
        Returns:
            相似度值 [0, 1]，1 表示完全相同
        """
        weights = self.weights.normalize()
        
        # 计算各通道距离
        hue_dist = self.compute_histogram_distance(
            features1.hue_histogram, features2.hue_histogram
        )
        lightness_dist = self.compute_histogram_distance(
            features1.lightness_histogram, features2.lightness_histogram
        )
        saturation_dist = self.compute_histogram_distance(
            features1.saturation_histogram, features2.saturation_histogram
        )
        
        # 加权平均距离
        weighted_dist = (
            weights.hue * hue_dist +
            weights.lightness * lightness_dist +
            weights.saturation * saturation_dist
        )
        
        # 转换为相似度
        return 1.0 - weighted_dist
    
    def compute_distance(self, features1: ImageFeatures, features2: ImageFeatures) -> float:
        """
        计算两张图片的综合距离
        
        Args:
            features1: 第一张图片的特征
            features2: 第二张图片的特征
            
        Returns:
            距离值 [0, 1]，0 表示完全相同
        """
        return 1.0 - self.compute_similarity(features1, features2)
    
    def build_distance_matrix(self, features_list: list[ImageFeatures]) -> np.ndarray:
        """
        构建图片间的距离矩阵
        
        Args:
            features_list: 图片特征列表
            
        Returns:
            N×N 对称距离矩阵
        """
        n = len(features_list)
        matrix = np.zeros((n, n), dtype=np.float64)
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = self.compute_distance(features_list[i], features_list[j])
                matrix[i, j] = dist
                matrix[j, i] = dist  # 对称
        
        return matrix
    
    def set_weights(self, weights: FeatureWeights) -> None:
        """设置特征权重"""
        self.weights = weights
    
    def set_metric(self, metric: DistanceMetric) -> None:
        """设置距离度量方法"""
        self.metric = metric
