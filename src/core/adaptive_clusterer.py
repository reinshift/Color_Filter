"""
自适应聚类模块

使用层次聚类和轮廓系数自动确定最佳聚类数。
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass

from .models import ImageFeatures


@dataclass
class ClusterResult:
    """聚类结果"""
    labels: np.ndarray           # 每张图片的类别标签
    n_clusters: int              # 类别数量
    silhouette_score: float      # 轮廓系数
    linkage_matrix: Optional[np.ndarray] = None  # 层次聚类链接矩阵


class AdaptiveClusterer:
    """
    自适应聚类器
    
    使用层次聚类（Ward链接）和轮廓系数自动确定最佳聚类数。
    """
    
    def __init__(self,
                 min_clusters: int = 2,
                 max_clusters: int = 10,
                 linkage: str = 'ward'):
        """
        初始化自适应聚类器
        
        Args:
            min_clusters: 最小聚类数
            max_clusters: 最大聚类数
            linkage: 链接方法 ('ward', 'complete', 'average', 'single')
        """
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.linkage = linkage
    
    def _compute_condensed_distance(self, distance_matrix: np.ndarray) -> np.ndarray:
        """
        将方阵距离矩阵转换为压缩形式（上三角）
        
        Args:
            distance_matrix: N×N 距离矩阵
            
        Returns:
            压缩距离向量
        """
        n = distance_matrix.shape[0]
        condensed = []
        for i in range(n):
            for j in range(i + 1, n):
                condensed.append(distance_matrix[i, j])
        return np.array(condensed)
    
    def _hierarchical_linkage(self, distance_matrix: np.ndarray) -> np.ndarray:
        """
        执行层次聚类，返回链接矩阵
        
        使用简化的 Ward 方法实现
        
        Args:
            distance_matrix: N×N 距离矩阵
            
        Returns:
            链接矩阵 (n-1, 4): [cluster1, cluster2, distance, size]
        """
        n = distance_matrix.shape[0]
        
        # 复制距离矩阵
        dist = distance_matrix.copy()
        
        # 初始化：每个点是一个簇
        cluster_sizes = {i: 1 for i in range(n)}
        active_clusters = set(range(n))
        
        linkage_matrix = []
        next_cluster_id = n
        
        for _ in range(n - 1):
            # 找到最近的两个簇
            min_dist = np.inf
            merge_i, merge_j = -1, -1
            
            active_list = sorted(active_clusters)
            for idx_i, i in enumerate(active_list):
                for j in active_list[idx_i + 1:]:
                    if dist[i, j] < min_dist:
                        min_dist = dist[i, j]
                        merge_i, merge_j = i, j
            
            if merge_i == -1:
                break
            
            # 记录合并
            size_new = cluster_sizes[merge_i] + cluster_sizes[merge_j]
            linkage_matrix.append([merge_i, merge_j, min_dist, size_new])
            
            # 更新距离（Ward方法）
            for k in active_clusters:
                if k != merge_i and k != merge_j:
                    ni = cluster_sizes[merge_i]
                    nj = cluster_sizes[merge_j]
                    nk = cluster_sizes[k]
                    
                    # Ward 距离更新公式
                    d_ik = dist[merge_i, k] if merge_i < k else dist[k, merge_i]
                    d_jk = dist[merge_j, k] if merge_j < k else dist[k, merge_j]
                    d_ij = min_dist
                    
                    new_dist = np.sqrt(
                        ((ni + nk) * d_ik ** 2 + 
                         (nj + nk) * d_jk ** 2 - 
                         nk * d_ij ** 2) / (ni + nj + nk)
                    )
                    
                    # 更新距离矩阵
                    if merge_i < k:
                        dist[merge_i, k] = new_dist
                    else:
                        dist[k, merge_i] = new_dist
            
            # 更新簇信息
            cluster_sizes[merge_i] = size_new
            active_clusters.remove(merge_j)
        
        return np.array(linkage_matrix)

    def _cut_tree(self, linkage_matrix: np.ndarray, n_clusters: int, n_samples: int) -> np.ndarray:
        """
        从链接矩阵中切割出指定数量的簇
        
        Args:
            linkage_matrix: 链接矩阵
            n_clusters: 目标簇数量
            n_samples: 原始样本数量
            
        Returns:
            标签数组
        """
        # 初始化：每个点是自己的簇
        labels = np.arange(n_samples)
        
        # 需要执行的合并次数
        n_merges = n_samples - n_clusters
        
        for i in range(min(n_merges, len(linkage_matrix))):
            c1, c2 = int(linkage_matrix[i, 0]), int(linkage_matrix[i, 1])
            
            # 找到属于 c2 的所有点，合并到 c1
            # 注意：c1, c2 可能是原始点或合并后的簇
            mask = (labels == c2) | (labels == c1)
            new_label = min(c1, c2)
            labels[mask] = new_label
        
        # 重新编号标签为 0, 1, 2, ...
        unique_labels = np.unique(labels)
        label_map = {old: new for new, old in enumerate(unique_labels)}
        labels = np.array([label_map[l] for l in labels])
        
        return labels
    
    def _compute_silhouette_score(self, distance_matrix: np.ndarray, labels: np.ndarray) -> float:
        """
        计算轮廓系数
        
        Args:
            distance_matrix: N×N 距离矩阵
            labels: 聚类标签
            
        Returns:
            轮廓系数 [-1, 1]
        """
        n = len(labels)
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels)
        
        if n_clusters <= 1 or n_clusters >= n:
            return 0.0
        
        silhouette_values = []
        
        for i in range(n):
            label_i = labels[i]
            
            # 计算 a(i): 与同簇其他点的平均距离
            same_cluster = np.where(labels == label_i)[0]
            same_cluster = same_cluster[same_cluster != i]
            
            if len(same_cluster) == 0:
                a_i = 0.0
            else:
                a_i = np.mean([distance_matrix[i, j] for j in same_cluster])
            
            # 计算 b(i): 与最近其他簇的平均距离
            b_i = np.inf
            for other_label in unique_labels:
                if other_label == label_i:
                    continue
                other_cluster = np.where(labels == other_label)[0]
                if len(other_cluster) > 0:
                    avg_dist = np.mean([distance_matrix[i, j] for j in other_cluster])
                    b_i = min(b_i, avg_dist)
            
            if b_i == np.inf:
                b_i = 0.0
            
            # 计算轮廓值
            max_ab = max(a_i, b_i)
            if max_ab > 0:
                s_i = (b_i - a_i) / max_ab
            else:
                s_i = 0.0
            
            silhouette_values.append(s_i)
        
        return float(np.mean(silhouette_values))
    
    def _find_optimal_k(self, distance_matrix: np.ndarray, 
                        linkage_matrix: np.ndarray) -> tuple[int, float]:
        """
        使用轮廓系数找到最佳聚类数
        
        Args:
            distance_matrix: N×N 距离矩阵
            linkage_matrix: 链接矩阵
            
        Returns:
            (最佳聚类数, 最佳轮廓系数)
        """
        n = distance_matrix.shape[0]
        
        # 调整搜索范围
        min_k = max(2, self.min_clusters)
        max_k = min(n - 1, self.max_clusters)
        
        if min_k > max_k:
            return min_k, 0.0
        
        best_k = min_k
        best_score = -1.0
        
        for k in range(min_k, max_k + 1):
            labels = self._cut_tree(linkage_matrix, k, n)
            score = self._compute_silhouette_score(distance_matrix, labels)
            
            if score > best_score:
                best_score = score
                best_k = k
        
        return best_k, best_score
    
    def cluster(self, distance_matrix: np.ndarray,
                n_clusters: Optional[int] = None) -> ClusterResult:
        """
        执行聚类
        
        Args:
            distance_matrix: N×N 距离矩阵
            n_clusters: 指定聚类数，None 则自动确定
            
        Returns:
            ClusterResult 对象
        """
        n = distance_matrix.shape[0]
        
        if n < 2:
            return ClusterResult(
                labels=np.zeros(n, dtype=int),
                n_clusters=1,
                silhouette_score=0.0
            )
        
        # 执行层次聚类
        linkage_matrix = self._hierarchical_linkage(distance_matrix)
        
        if n_clusters is None:
            # 自动确定最佳聚类数
            n_clusters, silhouette = self._find_optimal_k(distance_matrix, linkage_matrix)
        else:
            # 使用指定的聚类数
            n_clusters = max(1, min(n_clusters, n))
            labels = self._cut_tree(linkage_matrix, n_clusters, n)
            silhouette = self._compute_silhouette_score(distance_matrix, labels)
            
            return ClusterResult(
                labels=labels,
                n_clusters=n_clusters,
                silhouette_score=silhouette,
                linkage_matrix=linkage_matrix
            )
        
        # 使用最佳聚类数切割
        labels = self._cut_tree(linkage_matrix, n_clusters, n)
        
        return ClusterResult(
            labels=labels,
            n_clusters=n_clusters,
            silhouette_score=silhouette,
            linkage_matrix=linkage_matrix
        )
