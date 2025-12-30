"""
主窗口模块

实现图片颜色分类器的主界面，采用扁平简约设计风格。
支持简单模式和高级模式两种分类算法。
"""

import ctypes
import os
import sys
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QFrame,
    QGridLayout,
    QGroupBox,
    QSizePolicy,
    QComboBox,
    QSlider,
    QSpinBox,
)
from PyQt6.QtGui import QPixmap, QIcon

from .styles import (
    get_full_stylesheet,
    apply_button_style,
    apply_label_style,
    SECONDARY_BUTTON_STYLE,
    PREVIEW_CARD_STYLE,
    ADMIN_BADGE_STYLE,
    COLORS,
)
from core.engine import ClassificationEngine
from core.advanced_engine import AdvancedClassificationEngine
from core.preview_generator import PreviewGenerator
from core.models import (
    ClassificationResult, 
    RollbackResult,
    AdvancedClassificationResult,
    FeatureWeights,
)


class ClassificationWorker(QThread):
    """分类工作线程，避免阻塞UI"""
    
    progress_updated = pyqtSignal(int, int, str)
    finished = pyqtSignal(object)  # ClassificationResult or AdvancedClassificationResult
    error = pyqtSignal(str)
    
    def __init__(self, engine, source_path: str, target_path: Optional[str] = None, 
                 n_clusters: Optional[int] = None, is_advanced: bool = False):
        super().__init__()
        self.engine = engine
        self.source_path = source_path
        self.target_path = target_path
        self.n_clusters = n_clusters
        self.is_advanced = is_advanced
    
    def run(self):
        try:
            if self.is_advanced:
                result = self.engine.classify(
                    self.source_path,
                    self.target_path,
                    n_clusters=self.n_clusters,
                    progress_callback=self._on_progress
                )
            else:
                result = self.engine.classify(
                    self.source_path,
                    self.target_path,
                    progress_callback=self._on_progress
                )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
    
    def _on_progress(self, current: int, total: int, current_file: str):
        self.progress_updated.emit(current, total, current_file)


class MainWindow(QMainWindow):
    """
    应用主窗口，扁平简约设计
    
    提供文件夹选择、分类控制、进度显示和预览功能。
    支持简单模式和高级模式两种分类算法。
    """
    
    def __init__(self):
        super().__init__()
        self._engine = ClassificationEngine()
        self._advanced_engine = AdvancedClassificationEngine()
        self._preview_generator = PreviewGenerator()
        self._worker: Optional[ClassificationWorker] = None
        self._is_admin = self.check_admin_mode()
        self._last_result = None  # ClassificationResult or AdvancedClassificationResult
        self._is_advanced_mode = False
        
        self.setup_ui()
        self.apply_flat_style()
    
    def setup_ui(self) -> None:
        """设置UI组件"""
        self.setWindowTitle("图片颜色分类器")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # 标题区域
        self._setup_header(main_layout)
        
        # 路径选择区域
        self._setup_path_selection(main_layout)
        
        # 模式选择和高级设置区域
        self._setup_mode_selection(main_layout)
        
        # 控制按钮区域
        self._setup_controls(main_layout)
        
        # 进度显示区域
        self._setup_progress(main_layout)
        
        # 预览区域
        self._setup_preview(main_layout)
        
        # 更新按钮状态
        self._update_button_states()
    
    def _setup_header(self, layout: QVBoxLayout) -> None:
        """设置标题区域"""
        header_layout = QHBoxLayout()
        
        # 标题
        title_label = QLabel("图片颜色分类器")
        apply_label_style(title_label, 'title')
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 管理员模式标识
        if self._is_admin:
            admin_badge = QLabel("管理员模式")
            admin_badge.setStyleSheet(ADMIN_BADGE_STYLE)
            header_layout.addWidget(admin_badge)
        
        layout.addLayout(header_layout)
    
    def _setup_path_selection(self, layout: QVBoxLayout) -> None:
        """设置路径选择区域"""
        path_group = QGroupBox("选择文件夹")
        path_layout = QHBoxLayout(path_group)
        
        # 路径输入框
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("请选择要分类的图片文件夹...")
        self._path_edit.setReadOnly(True)
        path_layout.addWidget(self._path_edit)
        
        # 浏览按钮
        self._browse_btn = QPushButton("浏览...")
        self._browse_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self._browse_btn.clicked.connect(self.on_select_folder)
        path_layout.addWidget(self._browse_btn)
        
        layout.addWidget(path_group)
    
    def _setup_mode_selection(self, layout: QVBoxLayout) -> None:
        """设置模式选择和高级设置区域"""
        mode_group = QGroupBox("分类设置")
        mode_layout = QVBoxLayout(mode_group)
        
        # 模式选择行
        mode_row = QHBoxLayout()
        
        mode_label = QLabel("分类模式:")
        mode_row.addWidget(mode_label)
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("简单模式 (按主色调分类)", False)
        self._mode_combo.addItem("高级模式 (多维度特征分析)", True)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self._mode_combo.setMinimumWidth(200)
        mode_row.addWidget(self._mode_combo)
        
        mode_row.addStretch()
        mode_layout.addLayout(mode_row)
        
        # 高级设置容器
        self._advanced_settings = QWidget()
        advanced_layout = QVBoxLayout(self._advanced_settings)
        advanced_layout.setContentsMargins(0, 8, 0, 0)
        
        # 聚类数设置
        cluster_row = QHBoxLayout()
        cluster_label = QLabel("聚类数:")
        cluster_row.addWidget(cluster_label)
        
        self._auto_cluster_check = QPushButton("自动")
        self._auto_cluster_check.setCheckable(True)
        self._auto_cluster_check.setChecked(True)
        self._auto_cluster_check.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self._auto_cluster_check.clicked.connect(self._on_auto_cluster_toggled)
        cluster_row.addWidget(self._auto_cluster_check)
        
        self._cluster_spin = QSpinBox()
        self._cluster_spin.setRange(2, 20)
        self._cluster_spin.setValue(5)
        self._cluster_spin.setEnabled(False)
        self._cluster_spin.setMinimumWidth(60)
        cluster_row.addWidget(self._cluster_spin)
        
        cluster_row.addStretch()
        advanced_layout.addLayout(cluster_row)
        
        # 特征权重设置
        weights_row = QHBoxLayout()
        
        # 色调权重
        hue_label = QLabel("色调:")
        weights_row.addWidget(hue_label)
        self._hue_slider = QSlider(Qt.Orientation.Horizontal)
        self._hue_slider.setRange(0, 100)
        self._hue_slider.setValue(40)
        self._hue_slider.setMaximumWidth(80)
        weights_row.addWidget(self._hue_slider)
        self._hue_value = QLabel("40%")
        self._hue_value.setMinimumWidth(35)
        weights_row.addWidget(self._hue_value)
        self._hue_slider.valueChanged.connect(lambda v: self._hue_value.setText(f"{v}%"))
        
        # 明度权重
        light_label = QLabel("明度:")
        weights_row.addWidget(light_label)
        self._lightness_slider = QSlider(Qt.Orientation.Horizontal)
        self._lightness_slider.setRange(0, 100)
        self._lightness_slider.setValue(35)
        self._lightness_slider.setMaximumWidth(80)
        weights_row.addWidget(self._lightness_slider)
        self._lightness_value = QLabel("35%")
        self._lightness_value.setMinimumWidth(35)
        weights_row.addWidget(self._lightness_value)
        self._lightness_slider.valueChanged.connect(lambda v: self._lightness_value.setText(f"{v}%"))
        
        # 饱和度权重
        sat_label = QLabel("饱和度:")
        weights_row.addWidget(sat_label)
        self._saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self._saturation_slider.setRange(0, 100)
        self._saturation_slider.setValue(25)
        self._saturation_slider.setMaximumWidth(80)
        weights_row.addWidget(self._saturation_slider)
        self._saturation_value = QLabel("25%")
        self._saturation_value.setMinimumWidth(35)
        weights_row.addWidget(self._saturation_value)
        self._saturation_slider.valueChanged.connect(lambda v: self._saturation_value.setText(f"{v}%"))
        
        weights_row.addStretch()
        advanced_layout.addLayout(weights_row)
        
        self._advanced_settings.setVisible(False)
        mode_layout.addWidget(self._advanced_settings)
        
        layout.addWidget(mode_group)
    
    def _on_mode_changed(self, index: int) -> None:
        """模式切换回调"""
        self._is_advanced_mode = self._mode_combo.currentData()
        self._advanced_settings.setVisible(self._is_advanced_mode)
    
    def _on_auto_cluster_toggled(self) -> None:
        """自动聚类切换回调"""
        is_auto = self._auto_cluster_check.isChecked()
        self._cluster_spin.setEnabled(not is_auto)
        self._auto_cluster_check.setText("自动" if is_auto else "手动")
    
    def _setup_controls(self, layout: QVBoxLayout) -> None:
        """设置控制按钮区域"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        # 开始分类按钮
        self._start_btn = QPushButton("开始分类")
        self._start_btn.setMinimumWidth(120)
        apply_button_style(self._start_btn, 'primary')
        self._start_btn.clicked.connect(self.on_start_classification)
        controls_layout.addWidget(self._start_btn)
        
        # 回退按钮
        self._rollback_btn = QPushButton("撤销分类")
        self._rollback_btn.setMinimumWidth(120)
        self._rollback_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self._rollback_btn.clicked.connect(self.on_rollback)
        controls_layout.addWidget(self._rollback_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)

    def _setup_progress(self, layout: QVBoxLayout) -> None:
        """设置进度显示区域"""
        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout(progress_group)
        
        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        progress_layout.addWidget(self._progress_bar)
        
        # 进度信息
        info_layout = QHBoxLayout()
        
        self._progress_label = QLabel("就绪")
        apply_label_style(self._progress_label, 'secondary')
        info_layout.addWidget(self._progress_label)
        
        info_layout.addStretch()
        
        self._file_label = QLabel("")
        apply_label_style(self._file_label, 'secondary')
        info_layout.addWidget(self._file_label)
        
        progress_layout.addLayout(info_layout)
        
        layout.addWidget(progress_group)
    
    def _setup_preview(self, layout: QVBoxLayout) -> None:
        """设置预览区域"""
        preview_group = QGroupBox("分类预览")
        preview_layout = QVBoxLayout(preview_group)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 预览容器
        self._preview_container = QWidget()
        self._preview_layout = QVBoxLayout(self._preview_container)
        self._preview_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 初始提示
        self._empty_label = QLabel("分类完成后将在此显示预览")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_label_style(self._empty_label, 'secondary')
        self._preview_layout.addWidget(self._empty_label)
        
        scroll_area.setWidget(self._preview_container)
        preview_layout.addWidget(scroll_area)
        
        preview_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(preview_group, 1)
    
    def apply_flat_style(self) -> None:
        """应用扁平设计样式"""
        self.setStyleSheet(get_full_stylesheet())
    
    def on_select_folder(self) -> None:
        """处理文件夹选择"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择图片文件夹",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self._path_edit.setText(folder)
            self._update_button_states()
    
    def on_start_classification(self) -> None:
        """开始分类操作"""
        source_path = self._path_edit.text()
        
        if not source_path:
            QMessageBox.warning(self, "提示", "请先选择要分类的文件夹")
            return
        
        if not os.path.isdir(source_path):
            QMessageBox.warning(self, "错误", "选择的路径不存在或不是文件夹")
            return
        
        # 禁用按钮
        self._set_buttons_enabled(False)
        
        # 重置进度
        self._progress_bar.setValue(0)
        self._progress_label.setText("正在扫描...")
        self._file_label.setText("")
        
        # 根据模式选择引擎
        if self._is_advanced_mode:
            # 更新特征权重
            weights = FeatureWeights(
                hue=self._hue_slider.value() / 100.0,
                lightness=self._lightness_slider.value() / 100.0,
                saturation=self._saturation_slider.value() / 100.0
            )
            self._advanced_engine.set_feature_weights(weights)
            
            # 获取聚类数
            n_clusters = None if self._auto_cluster_check.isChecked() else self._cluster_spin.value()
            
            # 启动高级模式工作线程，target_path=source_path 表示在源文件夹下创建子文件夹
            self._worker = ClassificationWorker(
                self._advanced_engine, 
                source_path,
                target_path=source_path,
                n_clusters=n_clusters,
                is_advanced=True
            )
        else:
            # 启动简单模式工作线程
            self._worker = ClassificationWorker(self._engine, source_path, is_advanced=False)
        
        self._worker.progress_updated.connect(self.update_progress)
        self._worker.finished.connect(self._on_classification_finished)
        self._worker.error.connect(self._on_classification_error)
        self._worker.start()
    
    def _on_classification_finished(self, result) -> None:
        """分类完成回调"""
        self._last_result = result
        self._set_buttons_enabled(True)
        self._update_button_states()
        
        # 显示完成信息
        if isinstance(result, AdvancedClassificationResult):
            self._progress_label.setText(
                f"完成: {result.total_images} 张图片, {result.n_clusters} 个类别, "
                f"轮廓系数: {result.silhouette_score:.2f}"
            )
        else:
            self._progress_label.setText(
                f"完成: 成功 {result.total_processed} 张, 失败 {result.total_failed} 张"
            )
        self._file_label.setText("")
        
        # 显示预览
        if result.total_processed > 0:
            self.show_preview(result)
        
        # 显示完成对话框
        if isinstance(result, AdvancedClassificationResult):
            QMessageBox.information(
                self,
                "分类完成",
                f"成功分类 {result.total_images} 张图片\n"
                f"分为 {result.n_clusters} 个类别\n"
                f"聚类质量 (轮廓系数): {result.silhouette_score:.2f}"
            )
        else:
            QMessageBox.information(
                self,
                "分类完成",
                f"成功分类 {result.total_processed} 张图片\n"
                f"失败 {result.total_failed} 张"
            )
    
    def _on_classification_error(self, error_msg: str) -> None:
        """分类错误回调"""
        self._set_buttons_enabled(True)
        self._update_button_states()
        self._progress_label.setText("分类失败")
        
        QMessageBox.critical(self, "错误", f"分类过程中发生错误:\n{error_msg}")
    
    def on_rollback(self) -> None:
        """处理回退操作"""
        # 检查当前模式的引擎是否可以回退
        can_rollback_simple = self._engine.can_rollback()
        can_rollback_advanced = self._advanced_engine.can_rollback()
        
        if not can_rollback_simple and not can_rollback_advanced:
            QMessageBox.information(self, "提示", "没有可撤销的操作")
            return
        
        # 优先回退高级模式的操作
        if can_rollback_advanced:
            rollback_count = self._advanced_engine.get_rollback_count()
            reply = QMessageBox.question(
                self,
                "确认撤销",
                f"确定要撤销上次分类操作吗?\n"
                f"将恢复 {rollback_count} 个文件到原位置。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                result = self._advanced_engine.rollback()
                self._update_button_states()
                self._clear_preview()
                
                QMessageBox.information(
                    self,
                    "撤销完成",
                    f"成功恢复 {result.success_count} 个文件\n"
                    f"失败 {result.failed_count} 个"
                )
        elif can_rollback_simple:
            rollback_count = self._engine.get_rollback_count()
            reply = QMessageBox.question(
                self,
                "确认撤销",
                f"确定要撤销上次分类操作吗?\n"
                f"将恢复 {rollback_count} 个文件到原位置。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                result = self._engine.rollback()
                self._update_button_states()
                self._clear_preview()
                
                QMessageBox.information(
                    self,
                    "撤销完成",
                    f"成功恢复 {result.success_count} 个文件\n"
                    f"失败 {result.failed_count} 个"
                )
    
    def update_progress(self, current: int, total: int, filename: str) -> None:
        """更新进度显示"""
        if total > 0:
            percentage = int((current / total) * 100)
            self._progress_bar.setValue(percentage)
            self._progress_label.setText(f"处理中: {current}/{total}")
            self._file_label.setText(filename)

    def show_preview(self, result) -> None:
        """显示分类结果预览"""
        self._clear_preview()
        
        source_path = self._path_edit.text()
        
        # 获取类别计数（兼容两种结果类型）
        category_counts = result.category_counts
        
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            category_path = os.path.join(source_path, category)
            
            if os.path.isdir(category_path):
                card = self._create_category_card(category, count, category_path)
                self._preview_layout.addWidget(card)
    
    def _create_category_card(self, category: str, count: int, category_path: str) -> QFrame:
        """创建类别预览卡片"""
        card = QFrame()
        card.setStyleSheet(PREVIEW_CARD_STYLE)
        card.setProperty("expanded", False)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        
        # 标题行
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"{category} ({count}张)")
        title_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        expand_btn = QPushButton("展开")
        expand_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        expand_btn.setFixedWidth(60)
        expand_btn.clicked.connect(lambda: self._toggle_category_expand(card, category_path, expand_btn))
        header_layout.addWidget(expand_btn)
        
        card_layout.addLayout(header_layout)
        
        # 缩略图网格容器
        thumbnails_widget = QWidget()
        thumbnails_widget.setVisible(False)
        thumbnails_layout = QGridLayout(thumbnails_widget)
        thumbnails_layout.setSpacing(8)
        card_layout.addWidget(thumbnails_widget)
        
        # 存储引用
        card.thumbnails_widget = thumbnails_widget
        card.thumbnails_layout = thumbnails_layout
        card.category_path = category_path
        
        return card
    
    def _toggle_category_expand(self, card: QFrame, category_path: str, btn: QPushButton) -> None:
        """切换类别展开/折叠状态"""
        is_expanded = card.property("expanded")
        
        if is_expanded:
            # 折叠
            card.thumbnails_widget.setVisible(False)
            btn.setText("展开")
            card.setProperty("expanded", False)
        else:
            # 展开并加载缩略图
            self._load_thumbnails(card, category_path)
            card.thumbnails_widget.setVisible(True)
            btn.setText("收起")
            card.setProperty("expanded", True)
    
    def _load_thumbnails(self, card: QFrame, category_path: str) -> None:
        """加载类别缩略图"""
        layout = card.thumbnails_layout
        
        # 清空现有缩略图
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 生成缩略图
        thumbnails = self._preview_generator.generate_category_preview(category_path)
        
        # 添加到网格
        cols = 6
        for idx, pixmap in enumerate(thumbnails):
            row = idx // cols
            col = idx % cols
            
            thumb_label = QLabel()
            thumb_label.setPixmap(pixmap)
            thumb_label.setFixedSize(100, 100)
            thumb_label.setScaledContents(True)
            thumb_label.setStyleSheet(
                f"border: 1px solid {COLORS['border']}; border-radius: 4px;"
            )
            layout.addWidget(thumb_label, row, col)
    
    def _clear_preview(self) -> None:
        """清空预览区域"""
        # 移除所有子部件
        while self._preview_layout.count():
            item = self._preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加空提示
        self._empty_label = QLabel("分类完成后将在此显示预览")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_label_style(self._empty_label, 'secondary')
        self._preview_layout.addWidget(self._empty_label)
    
    def _set_buttons_enabled(self, enabled: bool) -> None:
        """设置按钮启用状态"""
        self._browse_btn.setEnabled(enabled)
        self._start_btn.setEnabled(enabled)
        self._rollback_btn.setEnabled(enabled)
    
    def _update_button_states(self) -> None:
        """更新按钮状态"""
        has_path = bool(self._path_edit.text())
        can_rollback = self._engine.can_rollback() or self._advanced_engine.can_rollback()
        
        self._start_btn.setEnabled(has_path)
        self._rollback_btn.setEnabled(can_rollback)
    
    def check_admin_mode(self) -> bool:
        """检查是否以管理员模式运行"""
        try:
            if sys.platform == 'win32':
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
