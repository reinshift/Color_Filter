"""
高级分类引擎模块

整合所有高级分类组件，提供完整的图片颜色分类功能。
"""

import os
import shutil
import time
from typing import Optional, Callable

from .models import (
    ImageFeatures,
    FeatureWeights,
    DistanceMetric,
    ClusterInfo,
    AdvancedClassificationResult,
    MoveRecord,
    TonalClass,
    HueCategory,
    SaturationLevel
)
from .advanced_extractor import AdvancedFeatureExtractor
from .similarity_calculator import SimilarityCalculator
from .adaptive_clusterer import AdaptiveClusterer
from .category_namer import CategoryNamer
from .scanner import ImageScanner


class AdvancedClassificationEngine:
    """
    高级分类引擎
    
    整合特征提取、相似度计算、聚类和命名组件，
    提供完整的图片颜色分类功能。
    """
    
    def __init__(self,
                 feature_extractor: Optional[AdvancedFeatureExtractor] = None,
                 similarity_calculator: Optional[SimilarityCalculator] = None,
                 clusterer: Optional[AdaptiveClusterer] = None,
                 namer: Optional[CategoryNamer] = None):
        """
        初始化高级分类引擎
        
        Args:
            feature_extractor: 特征提取器，None 则使用默认配置
            similarity_calculator: 相似度计算器，None 则使用默认配置
            clusterer: 聚类器，None 则使用默认配置
            namer: 命名器，None 则使用默认配置
        """
        self.feature_extractor = feature_extractor or AdvancedFeatureExtractor()
        self.similarity_calculator = similarity_calculator or SimilarityCalculator()
        self.clusterer = clusterer or AdaptiveClusterer()
        self.namer = namer or CategoryNamer()
        self.scanner = ImageScanner()
    
    def set_feature_weights(self, weights: FeatureWeights) -> None:
        """设置特征权重"""
        self.similarity_calculator.set_weights(weights)
    
    def set_distance_metric(self, metric: DistanceMetric) -> None:
        """设置距离度量方法"""
        self.similarity_calculator.set_metric(metric)
    
    def set_cluster_range(self, min_clusters: int, max_clusters: int) -> None:
        """设置聚类数范围"""
        self.clusterer.min_clusters = min_clusters
        self.clusterer.max_clusters = max_clusters
    
    def extract_all_features(self, 
                             image_paths: list[str],
                             progress_callback: Optional[Callable[[int, int, str], None]] = None
                             ) -> list[ImageFeatures]:
        """
        提取所有图片的特征
        
        Args:
            image_paths: 图片路径列表
            progress_callback: 进度回调函数 (current, total, message)
            
        Returns:
            特征列表
        """
        features = []
        total = len(image_paths)
        
        for i, path in enumerate(image_paths):
            if progress_callback:
                progress_callback(i + 1, total, f"提取特征: {os.path.basename(path)}")
            
            try:
                feat = self.feature_extractor.extract_features(path)
                features.append(feat)
            except Exception as e:
                # 跳过无法处理的图片
                print(f"警告: 无法处理图片 {path}: {e}")
                continue
        
        return features

    def classify(self,
                 source_path: str,
                 target_path: Optional[str] = None,
                 n_clusters: Optional[int] = None,
                 progress_callback: Optional[Callable[[int, int, str], None]] = None
                 ) -> AdvancedClassificationResult:
        """
        执行分类
        
        Args:
            source_path: 源文件夹路径
            target_path: 目标文件夹路径，None 则在源文件夹下创建子文件夹
            n_clusters: 指定聚类数，None 则自动确定
            progress_callback: 进度回调函数 (current, total, message)
            
        Returns:
            AdvancedClassificationResult 对象
        """
        start_time = time.time()
        
        # 1. 扫描图片
        if progress_callback:
            progress_callback(0, 100, "扫描图片...")
        
        scan_result = self.scanner.scan(source_path)
        image_paths = scan_result.image_paths
        
        if len(image_paths) == 0:
            return AdvancedClassificationResult(
                clusters=[],
                n_clusters=0,
                silhouette_score=0.0,
                total_images=0,
                processing_time=time.time() - start_time
            )
        
        # 2. 提取特征
        features = self.extract_all_features(image_paths, progress_callback)
        
        if len(features) < 2:
            # 图片太少，无法聚类
            cluster_info = ClusterInfo(
                cluster_id=0,
                name="全部图片",
                image_paths=[f.image_path for f in features],
                tonal_class=features[0].tonal_class if features else TonalClass.MID_KEY,
                hue_category=HueCategory.NEUTRAL,
                saturation_level=SaturationLevel.MODERATE,
                image_count=len(features)
            )
            return AdvancedClassificationResult(
                clusters=[cluster_info],
                n_clusters=1,
                silhouette_score=0.0,
                total_images=len(features),
                processing_time=time.time() - start_time
            )
        
        # 3. 构建距离矩阵
        if progress_callback:
            progress_callback(0, 100, "计算相似度...")
        
        distance_matrix = self.similarity_calculator.build_distance_matrix(features)
        
        # 4. 聚类
        if progress_callback:
            progress_callback(0, 100, "执行聚类...")
        
        cluster_result = self.clusterer.cluster(distance_matrix, n_clusters)
        
        # 5. 为每个聚类生成名称和信息
        if progress_callback:
            progress_callback(0, 100, "生成类别名称...")
        
        clusters = self._build_cluster_info(features, cluster_result.labels)
        
        # 6. 移动文件
        move_records = []
        if target_path is not None:
            move_records = self._move_files(clusters, target_path, progress_callback)
        
        return AdvancedClassificationResult(
            clusters=clusters,
            n_clusters=cluster_result.n_clusters,
            silhouette_score=cluster_result.silhouette_score,
            total_images=len(features),
            processing_time=time.time() - start_time,
            move_records=move_records
        )
    
    def _build_cluster_info(self, 
                            features: list[ImageFeatures],
                            labels: list[int]) -> list[ClusterInfo]:
        """
        构建聚类信息
        
        Args:
            features: 特征列表
            labels: 聚类标签
            
        Returns:
            ClusterInfo 列表
        """
        import numpy as np
        
        unique_labels = np.unique(labels)
        all_cluster_features = []
        
        # 收集每个聚类的特征
        for label in unique_labels:
            cluster_features = [f for f, l in zip(features, labels) if l == label]
            all_cluster_features.append(cluster_features)
        
        # 生成唯一名称
        names = self.namer.generate_unique_names(all_cluster_features)
        
        clusters = []
        for i, (label, cluster_features) in enumerate(zip(unique_labels, all_cluster_features)):
            name, tonal, hue, saturation = self.namer.generate_name_with_details(cluster_features)
            
            # 使用唯一名称
            unique_name = names[i]
            
            cluster_info = ClusterInfo(
                cluster_id=int(label),
                name=unique_name,
                image_paths=[f.image_path for f in cluster_features],
                tonal_class=tonal,
                hue_category=hue,
                saturation_level=saturation,
                image_count=len(cluster_features)
            )
            clusters.append(cluster_info)
        
        return clusters

    def _move_files(self,
                    clusters: list[ClusterInfo],
                    target_path: str,
                    progress_callback: Optional[Callable[[int, int, str], None]] = None
                    ) -> list[MoveRecord]:
        """
        移动文件到目标文件夹
        
        Args:
            clusters: 聚类信息列表
            target_path: 目标文件夹路径
            progress_callback: 进度回调函数
            
        Returns:
            移动记录列表
        """
        move_records = []
        total_files = sum(c.image_count for c in clusters)
        current = 0
        
        for cluster in clusters:
            # 创建类别文件夹
            category_path = os.path.join(target_path, cluster.name)
            os.makedirs(category_path, exist_ok=True)
            
            for image_path in cluster.image_paths:
                current += 1
                if progress_callback:
                    progress_callback(current, total_files, f"移动文件: {os.path.basename(image_path)}")
                
                try:
                    filename = os.path.basename(image_path)
                    dest_path = os.path.join(category_path, filename)
                    
                    # 处理重名文件
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(category_path, f"{base}_{counter}{ext}")
                            counter += 1
                    
                    shutil.move(image_path, dest_path)
                    
                    move_records.append(MoveRecord(
                        source_path=image_path,
                        destination_path=dest_path,
                        timestamp=time.time()
                    ))
                except Exception as e:
                    print(f"警告: 无法移动文件 {image_path}: {e}")
        
        return move_records
    
    def preview(self,
                source_path: str,
                n_clusters: Optional[int] = None,
                progress_callback: Optional[Callable[[int, int, str], None]] = None
                ) -> AdvancedClassificationResult:
        """
        预览分类结果（不移动文件）
        
        Args:
            source_path: 源文件夹路径
            n_clusters: 指定聚类数，None 则自动确定
            progress_callback: 进度回调函数
            
        Returns:
            AdvancedClassificationResult 对象
        """
        return self.classify(
            source_path=source_path,
            target_path=None,  # 不移动文件
            n_clusters=n_clusters,
            progress_callback=progress_callback
        )
