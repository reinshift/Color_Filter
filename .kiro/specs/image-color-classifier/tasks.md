# Implementation Plan: 图片颜色分类器

## Overview

本实现计划将图片颜色分类器分解为增量式的编码任务，从核心数据模型开始，逐步构建扫描、颜色提取、分类、回退等功能模块，最后完成UI集成和打包。

## Tasks

- [x] 1. 项目初始化和数据模型
  - [x] 1.1 创建项目结构和依赖配置
    - 创建 `requirements.txt` 包含 PyQt6, Pillow, scikit-learn, numpy, hypothesis, pytest
    - 创建项目目录结构: `src/`, `src/core/`, `src/ui/`, `tests/`
    - _Requirements: 9.1, 9.2_
  - [x] 1.2 实现数据模型
    - 创建 `src/core/models.py`
    - 实现 ColorCategory 枚举、ScanResult、ColorInfo、ColorExtractionResult、MoveRecord、RollbackResult、ClassificationResult 数据类
    - _Requirements: 2.2, 3.4, 6.1_

- [x] 2. 图片扫描模块
  - [x] 2.1 实现 ImageScanner 类
    - 创建 `src/core/scanner.py`
    - 实现 `scan()` 方法递归扫描目录
    - 实现 `is_valid_image()` 方法验证图片格式
    - 实现自定义异常 PathNotFoundError, AccessDeniedError
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [x] 2.2 编写 ImageScanner 属性测试

    - **Property 1: 扫描结果完整性**
    - **Validates: Requirements 1.1, 1.2**

- [-] 3. 颜色提取模块
  - [x] 3.1 实现 ColorExtractor 类
    - 创建 `src/core/extractor.py`
    - 实现 K-Means 颜色提取算法
    - 实现 `extract_colors()` 方法
    - 实现 `classify_color()` 方法将RGB映射到预定义类别
    - 实现 `get_dominant_category()` 方法
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 3.2 编写颜色提取属性测试

    - **Property 2: 颜色提取一致性**
    - **Validates: Requirements 2.1**
  - [x] 3.3 编写颜色占比属性测试

    - **Property 3: 颜色占比完整性**
    - **Validates: Requirements 2.2**
  - [x] 3.4 编写颜色分类属性测试

    - **Property 4: 颜色分类确定性**
    - **Validates: Requirements 2.3**

- [x] 4. Checkpoint - 核心算法验证
  - 确保所有测试通过，如有问题请询问用户

- [x] 5. 分类管理模块
  - [x] 5.1 实现 CategoryManager 类
    - 创建 `src/core/category_manager.py`
    - 实现 `create_category_folders()` 方法
    - 实现 `move_image()` 方法
    - 实现 `get_category_path()` 方法
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [ ]* 5.2 编写分类操作属性测试
    - **Property 5: 分类操作记录完整性**
    - **Validates: Requirements 3.2, 3.4**

- [x] 6. 回退管理模块
  - [x] 6.1 实现 RollbackManager 类
    - 创建 `src/core/rollback_manager.py`
    - 实现 `record_move()` 方法
    - 实现 `record_folder_creation()` 方法
    - 实现 `rollback()` 方法
    - 实现 `clear()` 方法
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [ ]* 6.2 编写回退 Round Trip 属性测试
    - **Property 8: 分类-回退 Round Trip**
    - **Validates: Requirements 6.1, 6.2, 6.3**

- [x] 7. 进度追踪和预览模块
  - [x] 7.1 实现 ProgressTracker 类
    - 创建 `src/core/progress_tracker.py`
    - 实现 Qt 信号机制
    - 实现 `update()` 和 `get_percentage()` 方法
    - _Requirements: 4.1, 4.2, 4.3_
  - [ ]* 7.2 编写进度计算属性测试
    - **Property 6: 进度计算正确性**
    - **Validates: Requirements 4.2**
  - [x] 7.3 实现 PreviewGenerator 类
    - 创建 `src/core/preview_generator.py`
    - 实现 `generate_thumbnail()` 方法
    - 实现 `generate_category_preview()` 方法
    - _Requirements: 5.1, 5.2_
  - [ ]* 7.4 编写预览数量属性测试
    - **Property 7: 预览数量限制**
    - **Validates: Requirements 5.1, 5.2**

- [x] 8. Checkpoint - 后端模块完成
  - 确保所有测试通过，如有问题请询问用户

- [x] 9. 分类引擎集成
  - [x] 9.1 实现 ClassificationEngine 类
    - 创建 `src/core/engine.py`
    - 集成 ImageScanner, ColorExtractor, CategoryManager, RollbackManager, ProgressTracker
    - 实现 `classify()` 方法协调整个分类流程
    - 实现 `rollback()` 方法
    - _Requirements: 1.1, 2.1, 3.1, 3.2, 6.2_

- [x] 10. 用户界面
  - [x] 10.1 实现扁平简约样式
    - 创建 `src/ui/styles.py`
    - 定义 QSS 样式表（浅灰白色调、扁平按钮、简洁进度条）
    - _Requirements: 8.1, 8.2_
  - [x] 10.2 实现 MainWindow 主窗口
    - 创建 `src/ui/main_window.py`
    - 实现文件夹选择功能
    - 实现开始分类按钮
    - 实现回退按钮
    - 实现进度条显示
    - _Requirements: 8.3, 8.4, 8.5_
  - [x] 10.3 实现预览区域
    - 实现分类结果预览网格
    - 实现类别展开功能
    - _Requirements: 5.3, 5.4_
  - [x] 10.4 实现管理员模式检测
    - 实现 `check_admin_mode()` 方法
    - 显示管理员模式标识
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 11. 应用入口和打包
  - [x] 11.1 创建应用入口
    - 创建 `src/main.py`
    - 初始化 QApplication 和 MainWindow
    - _Requirements: 7.3_
  - [x] 11.2 配置 PyInstaller 打包
    - 创建 `build.spec` 配置文件
    - 配置单文件打包、图标、依赖
    - _Requirements: 9.1, 9.2, 9.3_

- [x] 12. Final Checkpoint - 完整功能验证
  - 确保所有测试通过
  - 验证打包后的 exe 可以正常运行
  - 如有问题请询问用户

## Notes

- 标记 `*` 的任务为可选任务，可跳过以加快MVP开发
- 每个任务都引用了具体的需求条款以确保可追溯性
- 属性测试验证普遍性正确性属性
- Checkpoint 任务用于阶段性验证
