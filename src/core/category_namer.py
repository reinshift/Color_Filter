"""
类别命名模块

根据聚类特征生成有意义的中文类别名称。
"""

import numpy as np
from typing import Optional

from .models import (
    ImageFeatures,
    TonalClass,
    HueCategory,
    SaturationLevel
)


class CategoryNamer:
    """
    类别命名器
    
    根据聚类中图片的特征，生成描述性的中文类别名称，
    如"高调暖色鲜艳"、"低调冷色柔和"等。
    """
    
    # 色调范围定义 (HSV H通道, 0-179)
    # 暖色: 红(0-10, 170-179), 橙(11-25), 黄(26-35)
    # 冷色: 青(78-99), 蓝(100-130), 紫(131-160)
    # 中性: 绿(36-77), 品红(161-169)
    
    WARM_HUE_RANGES = [(0, 35), (170, 179)]  # 红、橙、黄
    COOL_HUE_RANGES = [(78, 160)]             # 青、蓝、紫
    NEUTRAL_HUE_RANGES = [(36, 77), (161, 169)]  # 绿、品红
    
    # 饱和度阈值
    VIVID_SATURATION_THRESHOLD = 150      # 高饱和度
    MODERATE_SATURATION_THRESHOLD = 80    # 中等饱和度
    NEUTRAL_SATURATION_THRESHOLD = 30     # 接近灰色
    
    def __init__(self):
        """初始化类别命名器"""
        pass
    
    def _analyze_dominant_hue(self, hue_histograms: list[np.ndarray]) -> HueCategory:
        """
        分析主导色调
        
        Args:
            hue_histograms: 色调直方图列表
            
        Returns:
            HueCategory 枚举值
        """
        if not hue_histograms:
            return HueCategory.NEUTRAL
        
        # 合并所有直方图
        combined = np.mean(hue_histograms, axis=0)
        
        # 计算各色调范围的权重
        warm_weight = 0.0
        cool_weight = 0.0
        neutral_weight = 0.0
        
        for start, end in self.WARM_HUE_RANGES:
            warm_weight += np.sum(combined[start:end+1])
        
        for start, end in self.COOL_HUE_RANGES:
            cool_weight += np.sum(combined[start:end+1])
        
        for start, end in self.NEUTRAL_HUE_RANGES:
            neutral_weight += np.sum(combined[start:end+1])
        
        # 判断主导色调
        max_weight = max(warm_weight, cool_weight, neutral_weight)
        
        if max_weight < 0.1:  # 几乎无彩色
            return HueCategory.NEUTRAL
        
        if warm_weight == max_weight:
            return HueCategory.WARM
        elif cool_weight == max_weight:
            return HueCategory.COOL
        else:
            return HueCategory.NEUTRAL
    
    def _analyze_saturation(self, saturation_means: list[float]) -> SaturationLevel:
        """
        分析饱和度水平
        
        Args:
            saturation_means: 平均饱和度列表
            
        Returns:
            SaturationLevel 枚举值
        """
        if not saturation_means:
            return SaturationLevel.MODERATE
        
        avg_saturation = np.mean(saturation_means)
        
        if avg_saturation >= self.VIVID_SATURATION_THRESHOLD:
            return SaturationLevel.VIVID
        elif avg_saturation >= self.MODERATE_SATURATION_THRESHOLD:
            return SaturationLevel.MODERATE
        elif avg_saturation >= self.NEUTRAL_SATURATION_THRESHOLD:
            return SaturationLevel.MUTED
        else:
            return SaturationLevel.NEUTRAL
    
    def _analyze_tonal_class(self, tonal_classes: list[TonalClass]) -> TonalClass:
        """
        分析主导影调
        
        Args:
            tonal_classes: 影调分类列表
            
        Returns:
            TonalClass 枚举值
        """
        if not tonal_classes:
            return TonalClass.MID_KEY
        
        # 统计各影调的数量
        counts = {
            TonalClass.HIGH_KEY: 0,
            TonalClass.MID_KEY: 0,
            TonalClass.LOW_KEY: 0
        }
        
        for tc in tonal_classes:
            counts[tc] += 1
        
        # 返回最多的影调
        return max(counts, key=counts.get)

    def generate_name(self, cluster_features: list[ImageFeatures]) -> str:
        """
        根据聚类特征生成类别名称
        
        名称格式: [影调][色调][饱和度]
        例如: "高调暖色鲜艳", "低调冷色柔和", "中调中性适中"
        
        Args:
            cluster_features: 该聚类中所有图片的特征列表
            
        Returns:
            类别名称字符串
        """
        if not cluster_features:
            return "未分类"
        
        # 提取各维度特征
        hue_histograms = [f.hue_histogram for f in cluster_features]
        saturation_means = [f.saturation_mean for f in cluster_features]
        tonal_classes = [f.tonal_class for f in cluster_features]
        
        # 分析各维度
        tonal = self._analyze_tonal_class(tonal_classes)
        hue = self._analyze_dominant_hue(hue_histograms)
        saturation = self._analyze_saturation(saturation_means)
        
        # 组合名称
        name_parts = [
            tonal.value,      # 高调/中调/低调
            hue.value,        # 暖色/冷色/中性
            saturation.value  # 鲜艳/适中/柔和/中性
        ]
        
        return "".join(name_parts)
    
    def generate_name_with_details(self, cluster_features: list[ImageFeatures]) -> tuple[str, TonalClass, HueCategory, SaturationLevel]:
        """
        生成类别名称并返回详细分类信息
        
        Args:
            cluster_features: 该聚类中所有图片的特征列表
            
        Returns:
            (名称, 影调, 色调, 饱和度)
        """
        if not cluster_features:
            return "未分类", TonalClass.MID_KEY, HueCategory.NEUTRAL, SaturationLevel.MODERATE
        
        # 提取各维度特征
        hue_histograms = [f.hue_histogram for f in cluster_features]
        saturation_means = [f.saturation_mean for f in cluster_features]
        tonal_classes = [f.tonal_class for f in cluster_features]
        
        # 分析各维度
        tonal = self._analyze_tonal_class(tonal_classes)
        hue = self._analyze_dominant_hue(hue_histograms)
        saturation = self._analyze_saturation(saturation_means)
        
        # 组合名称
        name = f"{tonal.value}{hue.value}{saturation.value}"
        
        return name, tonal, hue, saturation
    
    def generate_unique_names(self, all_cluster_features: list[list[ImageFeatures]]) -> list[str]:
        """
        为多个聚类生成唯一的名称
        
        如果有重名，会添加序号区分
        
        Args:
            all_cluster_features: 所有聚类的特征列表
            
        Returns:
            名称列表
        """
        names = []
        name_counts = {}
        
        for features in all_cluster_features:
            base_name = self.generate_name(features)
            
            if base_name in name_counts:
                name_counts[base_name] += 1
                name = f"{base_name}_{name_counts[base_name]}"
            else:
                name_counts[base_name] = 1
                name = base_name
            
            names.append(name)
        
        # 如果第一个也有重名，添加序号
        final_names = []
        seen = {}
        for name in names:
            base = name.split('_')[0] if '_' in name else name
            if names.count(base) > 1 or any(n.startswith(base + '_') for n in names):
                if base not in seen:
                    seen[base] = 1
                    final_names.append(f"{base}_1")
                else:
                    seen[base] += 1
                    final_names.append(f"{base}_{seen[base]}")
            else:
                final_names.append(name)
        
        return final_names
