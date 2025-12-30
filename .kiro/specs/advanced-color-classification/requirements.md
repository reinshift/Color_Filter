# Requirements Document

## Introduction

改进图片颜色分类算法，采用多维度特征提取和相似度计算，使分类结果在色调、影调、色彩科学上更加一致。当前版本仅使用 K-Means 提取主色并用 RGB 欧氏距离匹配，效果不理想。新算法将综合考虑色调直方图、明度分布、饱和度等多种因素。

## Glossary

- **Feature_Extractor**: 多维度特征提取器，从图片中提取色调、明度、饱和度等特征向量
- **Histogram_Analyzer**: 直方图分析器，计算各通道的分布特征
- **Similarity_Calculator**: 相似度计算器，使用直方图距离算法比较图片特征
- **Adaptive_Clusterer**: 自适应聚类器，根据图片特征自动确定最佳分类数量
- **Color_Space**: 色彩空间，包括 RGB、HSV、LAB 等
- **Tonal_Range**: 影调范围，描述图片明暗分布特征（高调/中调/低调）
- **Dominant_Hue**: 主色调，图片中占主导地位的色相
- **Histogram_Distance**: 直方图距离，衡量两个直方图分布差异的度量

## Requirements

### Requirement 1: 多维度特征提取

**User Story:** As a user, I want the system to extract comprehensive color features from images, so that classification is based on multiple color science dimensions.

#### Acceptance Criteria

1. WHEN an image is loaded, THE Feature_Extractor SHALL convert it to HSV and LAB color spaces
2. WHEN extracting features, THE Feature_Extractor SHALL compute hue histogram (H channel, 180 bins)
3. WHEN extracting features, THE Feature_Extractor SHALL compute lightness histogram (L channel, 256 bins)
4. WHEN extracting features, THE Feature_Extractor SHALL compute saturation histogram (S channel, 256 bins)
5. WHEN extracting features, THE Feature_Extractor SHALL compute weighted dominant colors using perceptual color space
6. WHEN extracting features, THE Feature_Extractor SHALL normalize all histograms to probability distributions

### Requirement 2: 影调分析

**User Story:** As a user, I want the system to analyze tonal characteristics, so that images with similar brightness distributions are grouped together.

#### Acceptance Criteria

1. WHEN analyzing tonal range, THE Histogram_Analyzer SHALL classify images as high-key, mid-key, or low-key based on lightness distribution
2. WHEN analyzing tonal range, THE Histogram_Analyzer SHALL compute mean, standard deviation, and skewness of lightness
3. WHEN analyzing contrast, THE Histogram_Analyzer SHALL measure the spread of lightness values
4. IF an image has lightness mean > 170, THEN THE Histogram_Analyzer SHALL classify it as high-key
5. IF an image has lightness mean < 85, THEN THE Histogram_Analyzer SHALL classify it as low-key

### Requirement 3: 直方图相似度计算

**User Story:** As a user, I want the system to compare images using histogram-based similarity metrics, so that visually similar images are grouped together.

#### Acceptance Criteria

1. WHEN comparing two images, THE Similarity_Calculator SHALL compute histogram intersection for each channel
2. WHEN comparing two images, THE Similarity_Calculator SHALL compute chi-square distance as an alternative metric
3. WHEN comparing two images, THE Similarity_Calculator SHALL compute Bhattacharyya distance for probability distributions
4. WHEN computing final similarity, THE Similarity_Calculator SHALL combine multiple metrics with configurable weights
5. THE Similarity_Calculator SHALL return a normalized similarity score between 0 and 1

### Requirement 4: 自适应聚类

**User Story:** As a user, I want the system to automatically determine the optimal number of categories, so that I don't need to manually specify cluster count.

#### Acceptance Criteria

1. WHEN clustering images, THE Adaptive_Clusterer SHALL use hierarchical clustering with Ward linkage
2. WHEN determining cluster count, THE Adaptive_Clusterer SHALL use silhouette score to find optimal k
3. WHEN clustering, THE Adaptive_Clusterer SHALL support a minimum and maximum cluster count constraint
4. WHEN clustering, THE Adaptive_Clusterer SHALL use the multi-dimensional feature vectors as input
5. IF user specifies a fixed cluster count, THEN THE Adaptive_Clusterer SHALL use that count instead of auto-detection

### Requirement 5: 特征权重配置

**User Story:** As a user, I want to configure the importance of different features, so that I can prioritize hue, lightness, or saturation based on my needs.

#### Acceptance Criteria

1. THE Feature_Extractor SHALL support configurable weights for hue, lightness, and saturation features
2. WHEN weights are modified, THE Similarity_Calculator SHALL apply them during distance computation
3. THE system SHALL provide default weights that balance all features equally
4. THE system SHALL allow saving and loading weight presets

### Requirement 6: 分类结果命名

**User Story:** As a user, I want meaningful category names based on color characteristics, so that I can understand what each category represents.

#### Acceptance Criteria

1. WHEN a cluster is formed, THE system SHALL analyze the cluster's dominant characteristics
2. WHEN naming a category, THE system SHALL combine tonal description (high-key/mid-key/low-key) with dominant hue
3. WHEN naming a category, THE system SHALL include saturation descriptor (vivid/muted/neutral) if applicable
4. THE system SHALL generate names like "高调暖色"、"低调冷色"、"中性灰调" etc.

### Requirement 7: 向后兼容

**User Story:** As a user, I want the new algorithm to integrate with the existing UI, so that I can use the improved classification without learning a new interface.

#### Acceptance Criteria

1. THE new Feature_Extractor SHALL implement the same interface as the existing ColorExtractor
2. THE system SHALL allow switching between simple and advanced classification modes
3. WHEN using advanced mode, THE system SHALL display additional feature information in the UI
4. THE system SHALL maintain the existing rollback functionality with the new algorithm
