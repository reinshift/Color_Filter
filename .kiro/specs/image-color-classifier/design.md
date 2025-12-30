# Design Document: 图片颜色分类器

## Overview

图片颜色分类器是一个基于Python的桌面应用，使用K-Means聚类算法分析图片主色调，并自动将图片按颜色分类到不同文件夹。应用采用PyQt6构建扁平简约的用户界面，使用PyInstaller打包为独立可执行文件。

### 技术栈选择

- **UI框架**: PyQt6 - 成熟的跨平台GUI框架，支持现代扁平设计
- **图像处理**: Pillow (PIL) - 图片读取和缩放
- **颜色分析**: scikit-learn (K-Means) - 聚类算法提取主色
- **数值计算**: NumPy - 高效的数组操作
- **打包工具**: PyInstaller - 打包为独立exe

### 算法选择：K-Means聚类

选择K-Means算法的原因：
1. **简单高效**: 算法复杂度适中，处理速度快
2. **效果稳定**: 对于颜色提取任务效果良好
3. **可控性强**: 可以指定提取的颜色数量
4. **广泛验证**: 在图像颜色分析领域被广泛使用

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Window (UI)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Path Select │ │  Controls   │ │     Preview Area        ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Progress Bar                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Classification Engine                     │
│  ┌───────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │ Image Scanner │──│ Color Extractor │──│Category Manager││
│  └───────────────┘  └─────────────────┘  └───────────────┘ │
│                              │                               │
│                     ┌────────┴────────┐                     │
│                     │ Progress Tracker│                     │
│                     └─────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Support Modules                           │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │ Rollback Manager│  │     Preview Generator           │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. ImageScanner 图片扫描器

```python
class ImageScanner:
    """扫描指定路径下的所有图片文件"""
    
    SUPPORTED_FORMATS: tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    
    def scan(self, path: str) -> ScanResult:
        """
        递归扫描指定路径下的所有图片
        
        Args:
            path: 要扫描的文件夹路径
            
        Returns:
            ScanResult: 包含图片路径列表和扫描统计信息
            
        Raises:
            PathNotFoundError: 路径不存在
            AccessDeniedError: 无访问权限
        """
        pass
    
    def is_valid_image(self, file_path: str) -> bool:
        """检查文件是否为有效的图片文件"""
        pass
```

### 2. ColorExtractor 颜色提取器

```python
class ColorExtractor:
    """使用K-Means算法提取图片主色调"""
    
    # 预定义颜色类别及其RGB范围
    COLOR_CATEGORIES: dict[str, tuple[int, int, int]] = {
        '红色': (255, 0, 0),
        '橙色': (255, 165, 0),
        '黄色': (255, 255, 0),
        '绿色': (0, 128, 0),
        '青色': (0, 255, 255),
        '蓝色': (0, 0, 255),
        '紫色': (128, 0, 128),
        '粉色': (255, 192, 203),
        '棕色': (139, 69, 19),
        '黑色': (0, 0, 0),
        '白色': (255, 255, 255),
        '灰色': (128, 128, 128),
    }
    
    def __init__(self, n_colors: int = 3, resize_size: tuple[int, int] = (150, 150)):
        """
        初始化颜色提取器
        
        Args:
            n_colors: 要提取的主色数量
            resize_size: 分析前缩放图片的尺寸
        """
        pass
    
    def extract_colors(self, image_path: str) -> ColorExtractionResult:
        """
        提取图片的主要颜色
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            ColorExtractionResult: 包含主色RGB值和占比
        """
        pass
    
    def classify_color(self, rgb: tuple[int, int, int]) -> str:
        """
        将RGB颜色映射到预定义类别
        
        Args:
            rgb: RGB颜色值元组
            
        Returns:
            str: 颜色类别名称
        """
        pass
    
    def get_dominant_category(self, result: ColorExtractionResult) -> str:
        """获取图片的主要颜色类别"""
        pass
```

### 3. CategoryManager 分类管理器

```python
class CategoryManager:
    """管理图片分类和文件操作"""
    
    def __init__(self, base_path: str):
        """
        初始化分类管理器
        
        Args:
            base_path: 分类文件夹的基础路径
        """
        pass
    
    def create_category_folders(self, categories: list[str]) -> None:
        """创建颜色类别文件夹"""
        pass
    
    def move_image(self, source: str, category: str) -> MoveRecord:
        """
        移动图片到对应类别文件夹
        
        Args:
            source: 源文件路径
            category: 目标颜色类别
            
        Returns:
            MoveRecord: 移动操作记录，用于回退
        """
        pass
    
    def get_category_path(self, category: str) -> str:
        """获取类别文件夹的完整路径"""
        pass
```

### 4. ProgressTracker 进度追踪器

```python
class ProgressTracker(QObject):
    """追踪和报告处理进度"""
    
    # Qt信号
    progress_updated = pyqtSignal(int, int, str)  # current, total, current_file
    completed = pyqtSignal()
    
    def __init__(self, total: int):
        """
        初始化进度追踪器
        
        Args:
            total: 总任务数量
        """
        pass
    
    def update(self, current: int, current_file: str) -> None:
        """更新进度"""
        pass
    
    def get_percentage(self) -> float:
        """获取当前进度百分比"""
        pass
```

### 5. PreviewGenerator 预览生成器

```python
class PreviewGenerator:
    """生成图片缩略图预览"""
    
    THUMBNAIL_SIZE: tuple[int, int] = (100, 100)
    MAX_PREVIEW_COUNT: int = 6
    
    def generate_thumbnail(self, image_path: str) -> QPixmap:
        """
        生成单张图片的缩略图
        
        Args:
            image_path: 图片路径
            
        Returns:
            QPixmap: 缩略图对象
        """
        pass
    
    def generate_category_preview(self, category_path: str) -> list[QPixmap]:
        """
        生成某个类别的预览缩略图列表
        
        Args:
            category_path: 类别文件夹路径
            
        Returns:
            list[QPixmap]: 缩略图列表（最多MAX_PREVIEW_COUNT张）
        """
        pass
```

### 6. RollbackManager 回退管理器

```python
class RollbackManager:
    """管理操作历史和回退功能"""
    
    def __init__(self):
        self._records: list[MoveRecord] = []
        self._created_folders: list[str] = []
    
    def record_move(self, record: MoveRecord) -> None:
        """记录一次移动操作"""
        pass
    
    def record_folder_creation(self, folder_path: str) -> None:
        """记录创建的文件夹"""
        pass
    
    def rollback(self) -> RollbackResult:
        """
        执行回退操作，将所有图片恢复到原位置
        
        Returns:
            RollbackResult: 回退结果，包含成功/失败数量
        """
        pass
    
    def clear(self) -> None:
        """清空操作记录"""
        pass
```

### 7. MainWindow 主窗口

```python
class MainWindow(QMainWindow):
    """应用主窗口，扁平简约设计"""
    
    def __init__(self):
        pass
    
    def setup_ui(self) -> None:
        """设置UI组件"""
        pass
    
    def apply_flat_style(self) -> None:
        """应用扁平设计样式"""
        pass
    
    def on_select_folder(self) -> None:
        """处理文件夹选择"""
        pass
    
    def on_start_classification(self) -> None:
        """开始分类操作"""
        pass
    
    def on_rollback(self) -> None:
        """处理回退操作"""
        pass
    
    def update_progress(self, current: int, total: int, filename: str) -> None:
        """更新进度显示"""
        pass
    
    def show_preview(self, results: dict[str, list[str]]) -> None:
        """显示分类结果预览"""
        pass
    
    def check_admin_mode(self) -> bool:
        """检查是否以管理员模式运行"""
        pass
```

## Data Models

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class ColorCategory(Enum):
    """颜色类别枚举"""
    RED = "红色"
    ORANGE = "橙色"
    YELLOW = "黄色"
    GREEN = "绿色"
    CYAN = "青色"
    BLUE = "蓝色"
    PURPLE = "紫色"
    PINK = "粉色"
    BROWN = "棕色"
    BLACK = "黑色"
    WHITE = "白色"
    GRAY = "灰色"
    OTHER = "其他"

@dataclass
class ScanResult:
    """扫描结果"""
    image_paths: list[str]
    total_count: int
    skipped_count: int
    error_files: list[str]

@dataclass
class ColorInfo:
    """单个颜色信息"""
    rgb: tuple[int, int, int]
    percentage: float
    category: str

@dataclass
class ColorExtractionResult:
    """颜色提取结果"""
    image_path: str
    colors: list[ColorInfo]
    dominant_category: str

@dataclass
class MoveRecord:
    """移动操作记录"""
    source_path: str
    destination_path: str
    timestamp: float

@dataclass
class RollbackResult:
    """回退操作结果"""
    success_count: int
    failed_count: int
    failed_files: list[str]

@dataclass
class ClassificationResult:
    """分类结果"""
    category_counts: dict[str, int]
    total_processed: int
    total_failed: int
    move_records: list[MoveRecord]
```



## Correctness Properties

*正确性属性是系统在所有有效执行中都应该保持为真的特征或行为。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 扫描结果完整性

*For any* 包含图片文件的目录结构，扫描器返回的路径列表应该：
1. 只包含支持格式（jpg, jpeg, png, bmp, gif, webp）的文件
2. 包含目录中所有符合格式的图片文件（无遗漏）

**Validates: Requirements 1.1, 1.2**

### Property 2: 颜色提取一致性

*For any* 纯色或近似纯色的图片，颜色提取器返回的主色应该与图片的实际颜色在RGB空间中的欧氏距离小于阈值（如50）。

**Validates: Requirements 2.1**

### Property 3: 颜色占比完整性

*For any* 图片的颜色提取结果，所有提取颜色的占比之和应该等于100%（允许浮点误差±0.01）。

**Validates: Requirements 2.2**

### Property 4: 颜色分类确定性

*For any* RGB颜色值，颜色分类函数应该：
1. 总是返回一个有效的颜色类别
2. 对相同的RGB值总是返回相同的类别（幂等性）

**Validates: Requirements 2.3**

### Property 5: 分类操作记录完整性

*For any* 分类操作，移动记录的数量应该等于成功移动的文件数量，且每条记录都包含有效的源路径和目标路径。

**Validates: Requirements 3.2, 3.4**

### Property 6: 进度计算正确性

*For any* 进度追踪器，当处理了N个文件（总数为T）时，进度百分比应该等于 (N / T) * 100。

**Validates: Requirements 4.2**

### Property 7: 预览数量限制

*For any* 类别文件夹，生成的预览缩略图数量应该不超过MAX_PREVIEW_COUNT（6张）。

**Validates: Requirements 5.1, 5.2**

### Property 8: 分类-回退 Round Trip

*For any* 成功的分类操作，执行回退后：
1. 所有被移动的图片应该恢复到原始位置
2. 分类创建的空文件夹应该被删除
3. 文件系统状态应该与分类前一致

**Validates: Requirements 6.1, 6.2, 6.3**

## Error Handling

### 文件系统错误

| 错误类型 | 处理方式 |
|---------|---------|
| 路径不存在 | 抛出 `PathNotFoundError`，UI显示友好提示 |
| 无访问权限 | 抛出 `AccessDeniedError`，提示以管理员模式运行 |
| 磁盘空间不足 | 抛出 `DiskFullError`，停止操作并提示 |
| 文件被占用 | 跳过该文件，记录到失败列表 |

### 图片处理错误

| 错误类型 | 处理方式 |
|---------|---------|
| 图片损坏 | 跳过该文件，记录到日志 |
| 不支持的格式 | 跳过该文件 |
| 内存不足 | 减小处理批次，重试 |

### 回退错误

| 错误类型 | 处理方式 |
|---------|---------|
| 原文件已删除 | 跳过，记录到失败列表 |
| 目标位置已有同名文件 | 提示用户选择覆盖或跳过 |

## Testing Strategy

### 测试框架选择

- **单元测试**: pytest
- **属性测试**: hypothesis (Python的属性测试库)
- **UI测试**: pytest-qt

### 单元测试

单元测试用于验证特定示例和边界情况：

1. **ImageScanner测试**
   - 测试空目录扫描
   - 测试只有非图片文件的目录
   - 测试嵌套目录结构
   - 测试无效路径错误处理

2. **ColorExtractor测试**
   - 测试纯红色图片提取
   - 测试纯白色图片提取
   - 测试混合颜色图片
   - 测试损坏图片处理

3. **CategoryManager测试**
   - 测试文件夹创建
   - 测试文件移动
   - 测试重名文件处理

4. **RollbackManager测试**
   - 测试单文件回退
   - 测试多文件回退
   - 测试空文件夹清理

### 属性测试

属性测试用于验证普遍性质，每个测试运行至少100次迭代：

```python
# 测试标注格式示例
# Feature: image-color-classifier, Property 1: 扫描结果完整性
@given(directory_structure=st.directory_with_mixed_files())
def test_scan_returns_only_supported_formats(directory_structure):
    """验证扫描器只返回支持格式的文件"""
    pass

# Feature: image-color-classifier, Property 4: 颜色分类确定性
@given(rgb=st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)))
def test_color_classification_is_deterministic(rgb):
    """验证颜色分类的确定性"""
    pass
```

### 测试配置

```python
# conftest.py
import hypothesis
hypothesis.settings.register_profile(
    "default",
    max_examples=100,
    deadline=None
)
```

### 测试覆盖目标

- 核心逻辑（颜色提取、分类）: >90% 覆盖率
- 文件操作: >80% 覆盖率
- UI组件: 关键交互测试
