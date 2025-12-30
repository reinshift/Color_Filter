# Core modules for image color classification

from .models import (
    ColorCategory,
    ScanResult,
    ColorInfo,
    ColorExtractionResult,
    MoveRecord,
    RollbackResult,
    ClassificationResult,
)
from .scanner import ImageScanner, PathNotFoundError, AccessDeniedError
from .extractor import ColorExtractor
from .category_manager import CategoryManager
from .rollback_manager import RollbackManager

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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
