# Requirements Document

## Introduction

图片颜色分类器是一个桌面应用程序，用于扫描指定路径下的所有图片，通过颜色分析算法提取图片的主色调，并自动将图片按颜色分类到不同文件夹中。应用采用扁平简约的UI风格，支持管理员模式自动分类、进度显示、小图预览和操作回退功能。

## Glossary

- **Color_Classifier**: 颜色分类器核心模块，负责分析图片主色调并进行分类
- **Image_Scanner**: 图片扫描器，负责遍历指定路径下的所有图片文件
- **Color_Extractor**: 颜色提取器，使用K-Means聚类算法提取图片的主要颜色
- **Category_Manager**: 分类管理器，负责创建文件夹和移动/复制图片
- **Preview_Generator**: 预览生成器，生成图片缩略图用于预览展示
- **Rollback_Manager**: 回退管理器，记录操作历史并支持撤销分类操作
- **Progress_Tracker**: 进度追踪器，跟踪并显示分类进度
- **Main_Window**: 主窗口界面，提供用户交互的扁平简约UI

## Requirements

### Requirement 1: 图片扫描

**User Story:** 作为用户，我想要选择一个文件夹路径，以便应用能够扫描该路径下的所有图片文件。

#### Acceptance Criteria

1. WHEN 用户选择一个文件夹路径 THEN THE Image_Scanner SHALL 递归扫描该路径下所有支持的图片格式（jpg, jpeg, png, bmp, gif, webp）
2. WHEN 扫描完成 THEN THE Image_Scanner SHALL 返回所有找到的图片文件路径列表
3. IF 选择的路径不存在或无法访问 THEN THE Image_Scanner SHALL 返回明确的错误信息
4. WHEN 扫描过程中遇到损坏的图片文件 THEN THE Image_Scanner SHALL 跳过该文件并记录到日志中

### Requirement 2: 颜色提取

**User Story:** 作为用户，我想要应用能够分析每张图片的主要颜色，以便进行准确的颜色分类。

#### Acceptance Criteria

1. WHEN 处理一张图片 THEN THE Color_Extractor SHALL 使用K-Means聚类算法提取图片的主要颜色（默认提取3种主色）
2. WHEN 提取颜色完成 THEN THE Color_Extractor SHALL 返回主色的RGB值和对应的颜色占比
3. THE Color_Extractor SHALL 将提取的RGB颜色映射到预定义的颜色类别（红、橙、黄、绿、青、蓝、紫、粉、棕、黑、白、灰）
4. WHEN 图片尺寸过大 THEN THE Color_Extractor SHALL 先将图片缩放到合适尺寸再进行分析以提高性能

### Requirement 3: 颜色分类

**User Story:** 作为用户，我想要应用能够根据图片的主色调自动创建文件夹并分类图片。

#### Acceptance Criteria

1. WHEN 开始分类操作 THEN THE Category_Manager SHALL 在目标路径下为每个颜色类别创建对应的文件夹
2. WHEN 分类一张图片 THEN THE Category_Manager SHALL 根据图片的主色调将其移动或复制到对应的颜色文件夹
3. WHEN 图片的主色调无法明确归类 THEN THE Category_Manager SHALL 将其放入"其他"文件夹
4. THE Category_Manager SHALL 在移动图片前记录原始路径以支持回退操作

### Requirement 4: 进度显示

**User Story:** 作为用户，我想要在分类过程中看到进度条，以便了解处理进度。

#### Acceptance Criteria

1. WHEN 分类操作开始 THEN THE Progress_Tracker SHALL 显示进度条并初始化为0%
2. WHILE 分类操作进行中 THEN THE Progress_Tracker SHALL 实时更新进度百分比和已处理/总数信息
3. WHEN 分类操作完成 THEN THE Progress_Tracker SHALL 显示100%并提示完成
4. THE Main_Window SHALL 在进度条下方显示当前正在处理的文件名

### Requirement 5: 预览功能

**User Story:** 作为用户，我想要在分类完成后预览各类别的图片，以便确认分类结果是否满意。

#### Acceptance Criteria

1. WHEN 分类完成 THEN THE Preview_Generator SHALL 为每个颜色类别生成缩略图预览
2. WHEN 某个类别图片数量超过6张 THEN THE Preview_Generator SHALL 仅显示前6张作为预览
3. THE Main_Window SHALL 以网格形式展示各类别的预览缩略图
4. WHEN 用户点击某个类别 THEN THE Main_Window SHALL 展开显示该类别的所有图片缩略图

### Requirement 6: 回退功能

**User Story:** 作为用户，如果我对分类结果不满意，我想要能够撤销操作将图片恢复到原始位置。

#### Acceptance Criteria

1. THE Rollback_Manager SHALL 在每次分类操作前保存完整的操作记录
2. WHEN 用户点击回退按钮 THEN THE Rollback_Manager SHALL 将所有图片恢复到原始位置
3. WHEN 回退操作完成 THEN THE Rollback_Manager SHALL 删除本次分类创建的空文件夹
4. IF 原始文件已被修改或删除 THEN THE Rollback_Manager SHALL 提示用户并跳过该文件

### Requirement 7: 管理员模式

**User Story:** 作为用户，我想要以管理员模式运行应用时能够自动开始分类，以便快速处理图片。

#### Acceptance Criteria

1. WHEN 应用以管理员权限启动 THEN THE Main_Window SHALL 显示管理员模式标识
2. WHERE 应用以管理员模式运行 THEN THE Category_Manager SHALL 具有完整的文件系统访问权限
3. THE Main_Window SHALL 提供"自动分类"按钮，点击后自动执行扫描和分类操作

### Requirement 8: 用户界面

**User Story:** 作为用户，我想要一个扁平简约风格的界面，以便获得良好的使用体验。

#### Acceptance Criteria

1. THE Main_Window SHALL 采用扁平设计风格，使用简洁的图标和清晰的排版
2. THE Main_Window SHALL 使用柔和的配色方案，主色调为浅灰和白色
3. THE Main_Window SHALL 提供文件夹选择按钮、开始分类按钮、回退按钮和预览区域
4. WHEN 操作进行中 THEN THE Main_Window SHALL 禁用相关按钮防止重复操作
5. THE Main_Window SHALL 支持窗口大小调整并保持布局合理

### Requirement 9: 应用打包

**User Story:** 作为用户，我想要一个独立的可执行文件，以便在没有Python环境的电脑上也能运行。

#### Acceptance Criteria

1. THE Color_Classifier SHALL 被打包为独立的Windows可执行文件（.exe）
2. THE 打包后的应用 SHALL 包含所有必要的依赖库
3. THE 打包后的应用 SHALL 在首次运行时不需要额外安装任何组件
