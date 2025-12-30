# Design Document: Advanced Color Classification

## Overview

本设计文档描述了改进版图片颜色分类算法的技术架构。新算法采用多维度特征提取，结合色调直方图、明度分布、饱和度等多种因素，使用直方图距离算法计算图片相似度，并通过自适应聚类实现更科学的分类结果。

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Classification Engine                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Feature         │  │ Similarity      │  │ Adaptive        │  │
│  │ Extractor       │──│ Calculator      │──│ Clusterer       │  │
│  └────────┬────────┘  └─────────────────┘  └─────────────────┘  │
│           │                                                       │
│  ┌────────┴────────┐                                             │
│  │ Histogram       │                                             │
│  │ Analyzer        │                                             │
│  └─────────────────┘                                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Color Space     │  │ Tonal           │  │ Category        │  │
│  │ Converter       │  │ Classifier      │  │ Namer           │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. AdvancedFeatureExtractor

负责从图片中提取多维度特征向量。

```python
class ImageFeatures:
    """图片特征数据结构"""
    image_path: str
    hue_histogram: np.ndarray        # 色调直方图 (180,)
    lightness_histogram: np.ndarray  # 明度直方图 (256,)
    saturation_histogram: np.ndarray # 饱和度直方图 (256,)
    dominant_colors: list[tuple]     # 主色调列表 [(LAB, percentage), ...]
    tonal_class: str                 # 影调分类: high-key/mid-key/low-key
    lightness_stats: dict            # 明度统计: mean, std, skewness
    saturation_mean: float           # 平均饱和度

class AdvancedFeatureExtractor:
    def __init__(self, 
                 resize_size: tuple = (200, 200),
                 hue_bins: int = 180,
                 lightness_bins: int = 256,
                 saturation_bins: int = 256):
        """初始化特征提取器"""
        
    def extract_features(self, image_path: str) -> ImageFeatures:
        """提取图片的多维度特征"""
        
    def _convert_color_spaces(self, image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """转换到 HSV 和 LAB 色彩空间"""
        
    def _compute_histograms(self, hsv: np.ndarray, lab: np.ndarray) -> tuple:
        """计算各通道直方图"""
        
    def _extract_dominant_colors(self, lab: np.ndarray, n_colors: int = 5) -> list:
        """提取主色调（LAB空间）"""
```

### 2. HistogramAnalyzer

分析直方图特征，进行影调分类。

```python
class TonalClass(Enum):
    HIGH_KEY = "high-key"    # 高调（明亮）
    MID_KEY = "mid-key"      # 中调
    LOW_KEY = "low-key"      # 低调（暗沉）

class HistogramAnalyzer:
    def __init__(self,
                 high_key_threshold: float = 170,
                 low_key_threshold: float = 85):
        """初始化直方图分析器"""
        
    def classify_tonal_range(self, lightness_hist: np.ndarray) -> TonalClass:
        """根据明度直方图分类影调"""
        
    def compute_lightness_stats(self, lightness_hist: np.ndarray) -> dict:
        """计算明度统计量: mean, std, skewness"""
        
    def compute_contrast(self, lightness_hist: np.ndarray) -> float:
        """计算对比度（明度分布的标准差）"""
```

### 3. SimilarityCalculator

计算图片之间的相似度。

```python
class DistanceMetric(Enum):
    INTERSECTION = "intersection"      # 直方图交叉
    CHI_SQUARE = "chi-square"          # 卡方距离
    BHATTACHARYYA = "bhattacharyya"    # 巴氏距离
    CORRELATION = "correlation"        # 相关性

class FeatureWeights:
    """特征权重配置"""
    hue: float = 0.4           # 色调权重
    lightness: float = 0.35    # 明度权重
    saturation: float = 0.25   # 饱和度权重

class SimilarityCalculator:
    def __init__(self, 
                 weights: FeatureWeights = None,
                 metric: DistanceMetric = DistanceMetric.BHATTACHARYYA):
        """初始化相似度计算器"""
        
    def compute_similarity(self, features1: ImageFeatures, features2: ImageFeatures) -> float:
        """计算两张图片的综合相似度 (0-1)"""
        
    def compute_histogram_distance(self, hist1: np.ndarray, hist2: np.ndarray, 
                                   metric: DistanceMetric) -> float:
        """计算直方图距离"""
        
    def _histogram_intersection(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """直方图交叉: sum(min(h1, h2))"""
        
    def _chi_square_distance(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """卡方距离: sum((h1-h2)^2 / (h1+h2))"""
        
    def _bhattacharyya_distance(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """巴氏距离: -ln(sum(sqrt(h1*h2)))"""
        
    def build_distance_matrix(self, features_list: list[ImageFeatures]) -> np.ndarray:
        """构建图片间的距离矩阵"""
```

### 4. AdaptiveClusterer

自适应聚类，自动确定最佳类别数。

```python
class ClusterResult:
    """聚类结果"""
    labels: np.ndarray           # 每张图片的类别标签
    n_clusters: int              # 类别数量
    silhouette_score: float      # 轮廓系数
    cluster_centers: list        # 各类别的中心特征

class AdaptiveClusterer:
    def __init__(self,
                 min_clusters: int = 2,
                 max_clusters: int = 10,
                 linkage: str = 'ward'):
        """初始化自适应聚类器"""
        
    def cluster(self, distance_matrix: np.ndarray, 
                n_clusters: int = None) -> ClusterResult:
        """执行聚类，n_clusters=None 时自动确定"""
        
    def _find_optimal_k(self, distance_matrix: np.ndarray) -> int:
        """使用轮廓系数找到最佳聚类数"""
        
    def _hierarchical_cluster(self, distance_matrix: np.ndarray, 
                              n_clusters: int) -> np.ndarray:
        """层次聚类"""
```

### 5. CategoryNamer

根据聚类特征生成有意义的类别名称。

```python
class HueCategory(Enum):
    WARM = "暖色"      # 红、橙、黄
    COOL = "冷色"      # 蓝、青、紫
    NEUTRAL = "中性"   # 绿、灰
    
class SaturationLevel(Enum):
    VIVID = "鲜艳"
    MODERATE = "适中"
    MUTED = "柔和"
    NEUTRAL = "中性"

class CategoryNamer:
    def __init__(self):
        """初始化类别命名器"""
        
    def generate_name(self, cluster_features: list[ImageFeatures]) -> str:
        """根据聚类特征生成类别名称"""
        
    def _analyze_dominant_hue(self, hue_histograms: list[np.ndarray]) -> HueCategory:
        """分析主导色调"""
        
    def _analyze_saturation(self, sat_means: list[float]) -> SaturationLevel:
        """分析饱和度水平"""
        
    def _get_tonal_description(self, tonal_classes: list[TonalClass]) -> str:
        """获取影调描述"""
```

### 6. AdvancedClassificationEngine

整合所有组件的主引擎。

```python
class AdvancedClassificationEngine:
    def __init__(self,
                 feature_extractor: AdvancedFeatureExtractor = None,
                 similarity_calculator: SimilarityCalculator = None,
                 clusterer: AdaptiveClusterer = None,
                 namer: CategoryNamer = None):
        """初始化高级分类引擎"""
        
    def classify(self, 
                 source_path: str,
                 target_path: str = None,
                 n_clusters: int = None,
                 progress_callback: Callable = None) -> ClassificationResult:
        """执行分类"""
        
    def set_feature_weights(self, weights: FeatureWeights) -> None:
        """设置特征权重"""
```

## Data Models

```python
@dataclass
class ImageFeatures:
    """图片特征"""
    image_path: str
    hue_histogram: np.ndarray
    lightness_histogram: np.ndarray
    saturation_histogram: np.ndarray
    dominant_colors: list[tuple[tuple[float, float, float], float]]  # [(LAB, percentage)]
    tonal_class: TonalClass
    lightness_stats: dict  # {mean, std, skewness}
    saturation_mean: float

@dataclass
class ClusterInfo:
    """聚类信息"""
    cluster_id: int
    name: str
    image_paths: list[str]
    representative_features: ImageFeatures  # 代表性特征
    
@dataclass
class AdvancedClassificationResult:
    """高级分类结果"""
    clusters: list[ClusterInfo]
    n_clusters: int
    silhouette_score: float
    total_images: int
    processing_time: float
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Histogram Normalization

*For any* image, the extracted hue, lightness, and saturation histograms SHALL sum to 1.0 (probability distribution).

**Validates: Requirements 1.6**

### Property 2: Similarity Symmetry

*For any* two images A and B, similarity(A, B) SHALL equal similarity(B, A).

**Validates: Requirements 3.5**

### Property 3: Similarity Bounds

*For any* two images, the computed similarity score SHALL be between 0 and 1 inclusive.

**Validates: Requirements 3.5**

### Property 4: Tonal Classification Consistency

*For any* image with lightness mean > 170, the tonal classification SHALL be HIGH_KEY.

**Validates: Requirements 2.4**

### Property 5: Cluster Assignment Completeness

*For any* set of images, after clustering, every image SHALL be assigned to exactly one cluster.

**Validates: Requirements 4.4**

### Property 6: Distance Matrix Symmetry

*For any* set of images, the computed distance matrix SHALL be symmetric (D[i,j] == D[j,i]).

**Validates: Requirements 3.4**

## Error Handling

| Error Condition | Handling Strategy |
|----------------|-------------------|
| Image cannot be opened | Skip image, log warning, continue processing |
| Image has no valid pixels | Return empty features, exclude from clustering |
| Too few images for clustering | Return single cluster containing all images |
| Clustering fails to converge | Fall back to simple K-Means with default k |
| Invalid feature weights | Reset to default weights, log warning |
| Memory overflow for large datasets | Process in batches, use sparse matrices |

## Testing Strategy

### Unit Tests
- Test color space conversion accuracy
- Test histogram computation correctness
- Test each distance metric implementation
- Test tonal classification thresholds
- Test category naming logic

### Property-Based Tests
- **Property 1**: Generate random images, verify histogram sums to 1.0
- **Property 2**: Generate image pairs, verify similarity symmetry
- **Property 3**: Generate image pairs, verify similarity bounds
- **Property 4**: Generate images with known lightness, verify tonal classification
- **Property 5**: Generate image sets, verify complete cluster assignment
- **Property 6**: Generate image sets, verify distance matrix symmetry

### Integration Tests
- End-to-end classification with sample image sets
- Verify backward compatibility with existing UI
- Performance benchmarks with varying dataset sizes

### Testing Framework
- pytest for unit and integration tests
- hypothesis for property-based tests
- Minimum 100 iterations per property test
