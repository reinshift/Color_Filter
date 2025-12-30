# Core modules for image color classification

from .models import (
    ColorCategory,
    ScanResult,
    ColorInfo,
    ColorExtractionResult,
    MoveRecord,
    RollbackResult,
    ClassificationResult,
    # 高级分类相关
    TonalClass,
    HueCategory,
    SaturationLevel,
    DistanceMetric,
    ImageFeatures,
    FeatureWeights,
    ClusterInfo,
    AdvancedClassificationResult,
)
from .scanner import ImageScanner, PathNotFoundError, AccessDeniedError
from .extractor import ColorExtractor
from .category_manager import CategoryManager
from .rollback_manager import RollbackManager

# 高级分类模块
from .advanced_extractor import AdvancedFeatureExtractor
from .histogram_analyzer import HistogramAnalyzer
from .similarity_calculator import SimilarityCalculator
from .adaptive_clusterer import AdaptiveClusterer, ClusterResult
from .category_namer import CategoryNamer

# Lazy import for ProgressTracker, PreviewGenerator, and ClassificationEngine
# to avoid PyQt6 import issues when not needed
def __getattr__(name):
    if name == "ProgressTracker":
        from .progress_tracker import ProgressTracker
        return ProgressTracker
    if name == "PreviewGenerator":
        from .preview_generator import PreviewGenerator
        return PreviewGenerator
    if name == "ClassificationEngine":
        from .engine import ClassificationEngine
        return ClassificationEngine
    if name == "AdvancedClassificationEngine":
        from .advanced_engine import AdvancedClassificationEngine
        return AdvancedClassificationEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
