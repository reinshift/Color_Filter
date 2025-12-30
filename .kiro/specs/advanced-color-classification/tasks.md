# Implementation Plan: Advanced Color Classification

## Overview

实现改进版图片颜色分类算法，采用多维度特征提取和直方图相似度计算。实现将分为数据模型、特征提取、相似度计算、聚类、命名和引擎整合几个阶段。

## Tasks

- [x] 1. 创建数据模型和枚举类型
  - [x] 1.1 创建 TonalClass、HueCategory、SaturationLevel 枚举
    - 在 `src/core/models.py` 中添加新的枚举类型
    - _Requirements: 2.1, 6.2, 6.3_
  - [x] 1.2 创建 ImageFeatures 数据类
    - 包含所有特征字段：直方图、主色调、影调分类、统计量
    - _Requirements: 1.1-1.6_
  - [x] 1.3 创建 FeatureWeights 和 ClusterInfo 数据类
    - 特征权重配置和聚类信息结构
    - _Requirements: 5.1, 4.1_
  - [x] 1.4 创建 AdvancedClassificationResult 数据类
    - 扩展现有 ClassificationResult
    - _Requirements: 4.4_

- [x] 2. 实现 AdvancedFeatureExtractor
  - [x] 2.1 实现色彩空间转换方法
    - RGB -> HSV 和 RGB -> LAB 转换
    - 使用 OpenCV 或 PIL/scikit-image
    - _Requirements: 1.1_
  - [ ]* 2.2 编写色彩空间转换的属性测试
    - **Property: 色彩空间转换值域正确性**
    - **Validates: Requirements 1.1**
  - [x] 2.3 实现直方图计算方法
    - 计算 H(180bins)、L(256bins)、S(256bins) 直方图
    - 归一化为概率分布
    - _Requirements: 1.2, 1.3, 1.4, 1.6_
  - [ ]* 2.4 编写直方图归一化的属性测试
    - **Property 1: Histogram Normalization**
    - **Validates: Requirements 1.6**
  - [x] 2.5 实现主色调提取方法
    - 在 LAB 空间使用 K-Means 提取主色
    - 返回颜色和占比
    - _Requirements: 1.5_
  - [x] 2.6 整合 extract_features 主方法
    - 组合所有特征提取步骤
    - _Requirements: 1.1-1.6_

- [x] 3. 实现 HistogramAnalyzer
  - [x] 3.1 实现明度统计计算
    - 计算 mean、std、skewness
    - _Requirements: 2.2_
  - [x] 3.2 实现影调分类方法
    - 根据明度均值分类为 high-key/mid-key/low-key
    - _Requirements: 2.1, 2.4, 2.5_
  - [ ]* 3.3 编写影调分类的属性测试
    - **Property 4: Tonal Classification Consistency**
    - **Validates: Requirements 2.4, 2.5**
  - [x] 3.4 实现对比度计算
    - 基于明度分布的标准差
    - _Requirements: 2.3_

- [x] 4. Checkpoint - 确保特征提取测试通过
  - 运行所有测试，确认特征提取模块正常工作
  - 如有问题请询问用户

- [x] 5. 实现 SimilarityCalculator
  - [x] 5.1 实现直方图交叉距离
    - intersection = sum(min(h1, h2))
    - _Requirements: 3.1_
  - [x] 5.2 实现卡方距离
    - chi_square = sum((h1-h2)^2 / (h1+h2+eps))
    - _Requirements: 3.2_
  - [x] 5.3 实现巴氏距离
    - bhattacharyya = -ln(sum(sqrt(h1*h2)))
    - _Requirements: 3.3_
  - [ ]* 5.4 编写相似度对称性的属性测试
    - **Property 2: Similarity Symmetry**
    - **Validates: Requirements 3.5**
  - [ ]* 5.5 编写相似度边界的属性测试
    - **Property 3: Similarity Bounds**
    - **Validates: Requirements 3.5**
  - [x] 5.6 实现加权综合相似度计算
    - 结合多通道距离和特征权重
    - _Requirements: 3.4, 5.2_
  - [x] 5.7 实现距离矩阵构建
    - 构建 N×N 对称距离矩阵
    - _Requirements: 3.4_
  - [ ]* 5.8 编写距离矩阵对称性的属性测试
    - **Property 6: Distance Matrix Symmetry**
    - **Validates: Requirements 3.4**

- [x] 6. 实现 AdaptiveClusterer
  - [x] 6.1 实现层次聚类方法
    - 使用纯 numpy 实现 Ward 链接方法
    - _Requirements: 4.1_
  - [x] 6.2 实现轮廓系数计算和最优 k 选择
    - 在 min_k 到 max_k 范围内搜索
    - _Requirements: 4.2, 4.3_
  - [x] 6.3 实现 cluster 主方法
    - 支持自动和手动指定聚类数
    - _Requirements: 4.4, 4.5_
  - [ ]* 6.4 编写聚类完整性的属性测试
    - **Property 5: Cluster Assignment Completeness**
    - **Validates: Requirements 4.4**

- [x] 7. Checkpoint - 确保聚类测试通过
  - 运行所有测试，确认聚类模块正常工作
  - 如有问题请询问用户

- [x] 8. 实现 CategoryNamer
  - [x] 8.1 实现主导色调分析
    - 分析色调直方图，判断暖色/冷色/中性
    - _Requirements: 6.2_
  - [x] 8.2 实现饱和度水平分析
    - 判断鲜艳/适中/柔和/中性
    - _Requirements: 6.3_
  - [x] 8.3 实现类别名称生成
    - 组合影调+色调+饱和度描述
    - 如"高调暖色鲜艳"、"低调冷色柔和"
    - _Requirements: 6.4_
  - [ ]* 8.4 编写命名格式的属性测试
    - **Property: 类别名称包含必要组成部分**
    - **Validates: Requirements 6.2, 6.3, 6.4**

- [x] 9. 实现 AdvancedClassificationEngine
  - [x] 9.1 创建引擎类框架
    - 整合所有组件
    - _Requirements: 7.1_
  - [x] 9.2 实现 classify 主方法
    - 特征提取 -> 距离矩阵 -> 聚类 -> 命名 -> 移动文件
    - _Requirements: 1-6_
  - [x] 9.3 实现特征权重配置方法
    - set_feature_weights
    - _Requirements: 5.1, 5.2_
  - [x] 9.4 实现与现有引擎的兼容接口
    - 保持 ClassificationEngine 接口兼容
    - _Requirements: 7.1_

- [x] 10. UI 集成
  - [x] 10.1 添加分类模式切换
    - 简单模式 / 高级模式
    - _Requirements: 7.2_
  - [x] 10.2 添加特征权重配置 UI
    - 滑块调节色调/明度/饱和度权重
    - _Requirements: 5.1_
  - [x] 10.3 更新预览显示
    - 显示新的类别名称和特征信息
    - _Requirements: 7.3_
  - [x] 10.4 确保回退功能兼容
    - 测试新算法的回退操作
    - _Requirements: 7.4_

- [x] 11. Final Checkpoint - 完整测试
  - 运行所有单元测试和属性测试
  - 进行端到端集成测试
  - 如有问题请询问用户

## Notes

- Tasks marked with `*` are optional property-based tests
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- 使用 Python 实现，依赖 numpy、scipy、opencv-python/pillow
