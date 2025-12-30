"""
颜色提取模块

使用K-Means聚类算法提取图片主色调并进行颜色分类。
"""

import math
from typing import Optional

import numpy as np
from PIL import Image

from .models import ColorCategory, ColorExtractionResult, ColorInfo


def _simple_kmeans(pixels: np.ndarray, n_clusters: int, max_iter: int = 100, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """
    简单的K-Means实现，避免sklearn的threadpool依赖问题
    
    Args:
        pixels: 像素数组 (N, 3)
        n_clusters: 聚类数量
        max_iter: 最大迭代次数
        random_state: 随机种子
        
    Returns:
        tuple: (聚类中心, 标签)
    """
    np.random.seed(random_state)
    n_samples = len(pixels)
    
    # 随机初始化聚类中心
    indices = np.random.choice(n_samples, n_clusters, replace=False)
    centers = pixels[indices].astype(np.float64)
    
    for _ in range(max_iter):
        # 计算每个像素到每个中心的距离
        distances = np.zeros((n_samples, n_clusters))
        for i in range(n_clusters):
            distances[:, i] = np.sum((pixels - centers[i]) ** 2, axis=1)
        
        # 分配标签
        labels = np.argmin(distances, axis=1)
        
        # 更新聚类中心
        new_centers = np.zeros_like(centers)
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                new_centers[i] = pixels[mask].mean(axis=0)
            else:
                new_centers[i] = centers[i]
        
        # 检查收敛
        if np.allclose(centers, new_centers):
            break
        centers = new_centers
    
    return centers, labels


class ColorExtractor:
    """使用K-Means算法提取图片主色调"""
    
    # 预定义颜色类别及其RGB参考值
    COLOR_CATEGORIES: dict[str, tuple[int, int, int]] = {
        ColorCategory.RED.value: (255, 0, 0),
        ColorCategory.ORANGE.value: (255, 165, 0),
        ColorCategory.YELLOW.value: (255, 255, 0),
        ColorCategory.GREEN.value: (0, 128, 0),
        ColorCategory.CYAN.value: (0, 255, 255),
        ColorCategory.BLUE.value: (0, 0, 255),
        ColorCategory.PURPLE.value: (128, 0, 128),
        ColorCategory.PINK.value: (255, 192, 203),
        ColorCategory.BROWN.value: (139, 69, 19),
        ColorCategory.BLACK.value: (0, 0, 0),
        ColorCategory.WHITE.value: (255, 255, 255),
        ColorCategory.GRAY.value: (128, 128, 128),
    }

    def __init__(self, n_colors: int = 3, resize_size: tuple[int, int] = (150, 150)):
        """
        初始化颜色提取器
        
        Args:
            n_colors: 要提取的主色数量
            resize_size: 分析前缩放图片的尺寸
        """
        self.n_colors = n_colors
        self.resize_size = resize_size
    
    def extract_colors(self, image_path: str) -> ColorExtractionResult:
        """
        提取图片的主要颜色
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            ColorExtractionResult: 包含主色RGB值和占比
            
        Raises:
            FileNotFoundError: 图片文件不存在
            ValueError: 图片无法处理
        """
        try:
            # 打开并处理图片
            with Image.open(image_path) as img:
                # 转换为RGB模式（处理RGBA、P等模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 缩放图片以提高性能
                img_resized = img.resize(self.resize_size, Image.Resampling.LANCZOS)
                
                # 转换为numpy数组
                pixels = np.array(img_resized)
                pixels = pixels.reshape(-1, 3)
                
                # 使用简单K-Means聚类提取主色
                centers, labels = _simple_kmeans(pixels, self.n_colors)
                
                # 计算每种颜色的占比
                unique, counts = np.unique(labels, return_counts=True)
                total_pixels = len(labels)
                
                # 构建颜色信息列表
                colors: list[ColorInfo] = []
                raw_percentages: list[float] = []
                
                for cluster_idx in range(self.n_colors):
                    rgb = tuple(int(c) for c in centers[cluster_idx])
                    
                    # 计算该颜色的占比
                    if cluster_idx in unique:
                        idx = np.where(unique == cluster_idx)[0][0]
                        percentage = (counts[idx] / total_pixels) * 100
                    else:
                        percentage = 0.0
                    
                    category = self.classify_color(rgb)
                    raw_percentages.append(percentage)
                    colors.append(ColorInfo(
                        rgb=rgb,
                        percentage=round(percentage, 2),
                        category=category
                    ))
                
                # 确保百分比总和为100%（修正四舍五入误差）
                total_rounded = sum(c.percentage for c in colors)
                if abs(total_rounded - 100.0) > 0.001 and colors:
                    # 找到占比最大的颜色，调整其百分比以确保总和为100%
                    diff = round(100.0 - total_rounded, 2)
                    max_idx = max(range(len(colors)), key=lambda i: colors[i].percentage)
                    colors[max_idx] = ColorInfo(
                        rgb=colors[max_idx].rgb,
                        percentage=round(colors[max_idx].percentage + diff, 2),
                        category=colors[max_idx].category
                    )
                
                # 按占比降序排序
                colors.sort(key=lambda c: c.percentage, reverse=True)
                
                # 获取主要颜色类别
                dominant_category = self.get_dominant_category_from_colors(colors)
                
                return ColorExtractionResult(
                    image_path=image_path,
                    colors=colors,
                    dominant_category=dominant_category
                )
                
        except FileNotFoundError:
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        except Exception as e:
            raise ValueError(f"无法处理图片 {image_path}: {str(e)}")
    
    def classify_color(self, rgb: tuple[int, int, int]) -> str:
        """
        将RGB颜色映射到预定义类别
        
        使用欧氏距离找到最接近的预定义颜色类别。
        
        Args:
            rgb: RGB颜色值元组
            
        Returns:
            str: 颜色类别名称
        """
        min_distance = float('inf')
        closest_category = ColorCategory.OTHER.value
        
        r, g, b = rgb
        
        # 特殊处理：检查是否为灰度色（R≈G≈B）
        if self._is_grayscale(rgb):
            brightness = (r + g + b) / 3
            if brightness < 50:
                return ColorCategory.BLACK.value
            elif brightness > 200:
                return ColorCategory.WHITE.value
            else:
                return ColorCategory.GRAY.value
        
        # 计算与每个预定义颜色的欧氏距离
        for category_name, ref_rgb in self.COLOR_CATEGORIES.items():
            # 跳过黑白灰，因为已经在上面处理过了
            if category_name in [ColorCategory.BLACK.value, ColorCategory.WHITE.value, ColorCategory.GRAY.value]:
                continue
                
            distance = self._euclidean_distance(rgb, ref_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_category = category_name
        
        return closest_category
    
    def get_dominant_category(self, result: ColorExtractionResult) -> str:
        """
        获取图片的主要颜色类别
        
        Args:
            result: 颜色提取结果
            
        Returns:
            str: 主要颜色类别名称
        """
        return self.get_dominant_category_from_colors(result.colors)
    
    def get_dominant_category_from_colors(self, colors: list[ColorInfo]) -> str:
        """
        从颜色列表中获取主要颜色类别
        
        Args:
            colors: 颜色信息列表
            
        Returns:
            str: 主要颜色类别名称
        """
        if not colors:
            return ColorCategory.OTHER.value
        
        # 返回占比最高的颜色类别
        # 颜色列表已按占比降序排序
        return colors[0].category
    
    def _euclidean_distance(self, rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
        """
        计算两个RGB颜色之间的欧氏距离
        
        Args:
            rgb1: 第一个RGB颜色
            rgb2: 第二个RGB颜色
            
        Returns:
            float: 欧氏距离
        """
        return math.sqrt(
            (rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2
        )
    
    def _is_grayscale(self, rgb: tuple[int, int, int], threshold: int = 20) -> bool:
        """
        检查颜色是否为灰度色
        
        Args:
            rgb: RGB颜色值
            threshold: 判断阈值，R、G、B之间的最大差值
            
        Returns:
            bool: 是否为灰度色
        """
        r, g, b = rgb
        return (abs(r - g) <= threshold and 
                abs(g - b) <= threshold and 
                abs(r - b) <= threshold)
