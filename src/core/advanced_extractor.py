"""
高级特征提取模块

使用多维度特征提取，包括色调直方图、明度分布、饱和度等。
支持 HSV 和 LAB 色彩空间分析。
"""

import numpy as np
from PIL import Image
from typing import Optional

from .models import (
    ImageFeatures, 
    TonalClass, 
    LightnessStats, 
    DominantColor
)


def _simple_kmeans(pixels: np.ndarray, n_clusters: int, max_iter: int = 100, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """简单的K-Means实现"""
    np.random.seed(random_state)
    n_samples = len(pixels)
    
    if n_samples < n_clusters:
        n_clusters = max(1, n_samples)
    
    indices = np.random.choice(n_samples, n_clusters, replace=False)
    centers = pixels[indices].astype(np.float64)
    
    for _ in range(max_iter):
        distances = np.zeros((n_samples, n_clusters))
        for i in range(n_clusters):
            distances[:, i] = np.sum((pixels - centers[i]) ** 2, axis=1)
        
        labels = np.argmin(distances, axis=1)
        
        new_centers = np.zeros_like(centers)
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                new_centers[i] = pixels[mask].mean(axis=0)
            else:
                new_centers[i] = centers[i]
        
        if np.allclose(centers, new_centers):
            break
        centers = new_centers
    
    return centers, labels


class AdvancedFeatureExtractor:
    """
    高级特征提取器
    
    提取图片的多维度特征，包括：
    - 色调直方图 (HSV H通道)
    - 明度直方图 (LAB L通道)
    - 饱和度直方图 (HSV S通道)
    - 主色调 (LAB空间K-Means)
    - 影调分类
    - 统计信息
    """
    
    def __init__(self,
                 resize_size: tuple[int, int] = (200, 200),
                 hue_bins: int = 180,
                 lightness_bins: int = 256,
                 saturation_bins: int = 256,
                 n_dominant_colors: int = 5,
                 high_key_threshold: float = 170,
                 low_key_threshold: float = 85):
        """
        初始化特征提取器
        
        Args:
            resize_size: 分析前缩放图片的尺寸
            hue_bins: 色调直方图的bin数量
            lightness_bins: 明度直方图的bin数量
            saturation_bins: 饱和度直方图的bin数量
            n_dominant_colors: 提取的主色调数量
            high_key_threshold: 高调判定阈值
            low_key_threshold: 低调判定阈值
        """
        self.resize_size = resize_size
        self.hue_bins = hue_bins
        self.lightness_bins = lightness_bins
        self.saturation_bins = saturation_bins
        self.n_dominant_colors = n_dominant_colors
        self.high_key_threshold = high_key_threshold
        self.low_key_threshold = low_key_threshold
    
    def _rgb_to_hsv(self, rgb: np.ndarray) -> np.ndarray:
        """
        RGB 转 HSV 色彩空间
        
        Args:
            rgb: RGB图像数组 (H, W, 3)，值范围 0-255
            
        Returns:
            HSV图像数组 (H, W, 3)，H: 0-179, S: 0-255, V: 0-255
        """
        rgb = rgb.astype(np.float32) / 255.0
        
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        
        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        diff = max_c - min_c
        
        # Value
        v = max_c
        
        # Saturation
        s = np.where(max_c != 0, diff / max_c, 0)
        
        # Hue
        h = np.zeros_like(max_c)
        
        # 避免除零
        mask = diff != 0
        
        # Red is max
        red_mask = mask & (max_c == r)
        h[red_mask] = (60 * ((g[red_mask] - b[red_mask]) / diff[red_mask]) + 360) % 360
        
        # Green is max
        green_mask = mask & (max_c == g)
        h[green_mask] = (60 * ((b[green_mask] - r[green_mask]) / diff[green_mask]) + 120) % 360
        
        # Blue is max
        blue_mask = mask & (max_c == b)
        h[blue_mask] = (60 * ((r[blue_mask] - g[blue_mask]) / diff[blue_mask]) + 240) % 360
        
        # 转换到 OpenCV 范围: H: 0-179, S: 0-255, V: 0-255
        h = (h / 2).astype(np.uint8)  # 0-179
        s = (s * 255).astype(np.uint8)
        v = (v * 255).astype(np.uint8)
        
        return np.stack([h, s, v], axis=-1)
    
    def _rgb_to_lab(self, rgb: np.ndarray) -> np.ndarray:
        """
        RGB 转 LAB 色彩空间
        
        Args:
            rgb: RGB图像数组 (H, W, 3)，值范围 0-255
            
        Returns:
            LAB图像数组 (H, W, 3)，L: 0-255, a: 0-255, b: 0-255 (偏移后)
        """
        # RGB to XYZ
        rgb = rgb.astype(np.float32) / 255.0
        
        # sRGB gamma correction
        mask = rgb > 0.04045
        rgb_linear = np.where(mask, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
        
        # RGB to XYZ matrix (D65 illuminant)
        r, g, b = rgb_linear[:, :, 0], rgb_linear[:, :, 1], rgb_linear[:, :, 2]
        
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        # XYZ to LAB (D65 reference white)
        xn, yn, zn = 0.95047, 1.0, 1.08883
        
        x = x / xn
        y = y / yn
        z = z / zn
        
        def f(t):
            delta = 6/29
            return np.where(t > delta**3, t**(1/3), t / (3 * delta**2) + 4/29)
        
        fx, fy, fz = f(x), f(y), f(z)
        
        L = 116 * fy - 16  # 0-100
        a = 500 * (fx - fy)  # -128 to 127
        b = 200 * (fy - fz)  # -128 to 127
        
        # 转换到 0-255 范围
        L = (L * 255 / 100).clip(0, 255).astype(np.uint8)
        a = ((a + 128)).clip(0, 255).astype(np.uint8)
        b = ((b + 128)).clip(0, 255).astype(np.uint8)
        
        return np.stack([L, a, b], axis=-1)

    def _compute_histogram(self, channel: np.ndarray, bins: int, normalize: bool = True) -> np.ndarray:
        """
        计算单通道直方图
        
        Args:
            channel: 单通道图像数组
            bins: bin数量
            normalize: 是否归一化为概率分布
            
        Returns:
            直方图数组
        """
        hist, _ = np.histogram(channel.flatten(), bins=bins, range=(0, bins))
        
        if normalize:
            total = hist.sum()
            if total > 0:
                hist = hist.astype(np.float64) / total
        
        return hist
    
    def _compute_lightness_stats(self, lightness: np.ndarray) -> LightnessStats:
        """
        计算明度统计信息
        
        Args:
            lightness: 明度通道数组
            
        Returns:
            LightnessStats 对象
        """
        flat = lightness.flatten().astype(np.float64)
        
        mean = np.mean(flat)
        std = np.std(flat)
        
        # 计算偏度 (skewness)
        if std > 0:
            skewness = np.mean(((flat - mean) / std) ** 3)
        else:
            skewness = 0.0
        
        return LightnessStats(mean=mean, std=std, skewness=skewness)
    
    def _classify_tonal_range(self, lightness_mean: float) -> TonalClass:
        """
        根据明度均值分类影调
        
        Args:
            lightness_mean: 明度均值 (0-255)
            
        Returns:
            TonalClass 枚举值
        """
        if lightness_mean > self.high_key_threshold:
            return TonalClass.HIGH_KEY
        elif lightness_mean < self.low_key_threshold:
            return TonalClass.LOW_KEY
        else:
            return TonalClass.MID_KEY
    
    def _extract_dominant_colors(self, lab: np.ndarray) -> list[DominantColor]:
        """
        提取主色调（LAB空间）
        
        Args:
            lab: LAB图像数组
            
        Returns:
            DominantColor 列表
        """
        pixels = lab.reshape(-1, 3).astype(np.float64)
        
        # 使用 K-Means 聚类
        centers, labels = _simple_kmeans(pixels, self.n_dominant_colors)
        
        # 计算每种颜色的占比
        unique, counts = np.unique(labels, return_counts=True)
        total_pixels = len(labels)
        
        dominant_colors = []
        for i in range(len(centers)):
            if i in unique:
                idx = np.where(unique == i)[0][0]
                percentage = (counts[idx] / total_pixels) * 100
            else:
                percentage = 0.0
            
            # 转换回原始 LAB 范围
            L = centers[i][0] * 100 / 255
            a = centers[i][1] - 128
            b = centers[i][2] - 128
            
            dominant_colors.append(DominantColor(
                lab=(L, a, b),
                percentage=round(percentage, 2)
            ))
        
        # 按占比降序排序
        dominant_colors.sort(key=lambda c: c.percentage, reverse=True)
        
        return dominant_colors
    
    def extract_features(self, image_path: str) -> ImageFeatures:
        """
        提取图片的多维度特征
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            ImageFeatures 对象
            
        Raises:
            FileNotFoundError: 图片文件不存在
            ValueError: 图片无法处理
        """
        try:
            with Image.open(image_path) as img:
                # 转换为 RGB 模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 缩放图片
                img_resized = img.resize(self.resize_size, Image.Resampling.LANCZOS)
                rgb = np.array(img_resized)
                
                # 转换色彩空间
                hsv = self._rgb_to_hsv(rgb)
                lab = self._rgb_to_lab(rgb)
                
                # 计算直方图
                hue_hist = self._compute_histogram(hsv[:, :, 0], self.hue_bins)
                lightness_hist = self._compute_histogram(lab[:, :, 0], self.lightness_bins)
                saturation_hist = self._compute_histogram(hsv[:, :, 1], self.saturation_bins)
                
                # 计算统计信息
                lightness_stats = self._compute_lightness_stats(lab[:, :, 0])
                saturation_mean = float(np.mean(hsv[:, :, 1]))
                
                # 分类影调
                tonal_class = self._classify_tonal_range(lightness_stats.mean)
                
                # 提取主色调
                dominant_colors = self._extract_dominant_colors(lab)
                
                return ImageFeatures(
                    image_path=image_path,
                    hue_histogram=hue_hist,
                    lightness_histogram=lightness_hist,
                    saturation_histogram=saturation_hist,
                    dominant_colors=dominant_colors,
                    tonal_class=tonal_class,
                    lightness_stats=lightness_stats,
                    saturation_mean=saturation_mean
                )
                
        except FileNotFoundError:
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        except Exception as e:
            raise ValueError(f"无法处理图片 {image_path}: {str(e)}")
