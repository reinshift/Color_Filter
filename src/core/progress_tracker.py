"""Progress tracking module for image classification operations."""

from PyQt6.QtCore import QObject, pyqtSignal


class ProgressTracker(QObject):
    """追踪和报告处理进度
    
    Attributes:
        progress_updated: Signal emitted when progress changes (current, total, current_file)
        completed: Signal emitted when all tasks are complete
    """
    
    # Qt signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, current_file
    completed = pyqtSignal()
    
    def __init__(self, total: int):
        """初始化进度追踪器
        
        Args:
            total: 总任务数量
        """
        super().__init__()
        self._total = total
        self._current = 0
        self._current_file = ""
    
    @property
    def total(self) -> int:
        """获取总任务数量"""
        return self._total
    
    @property
    def current(self) -> int:
        """获取当前已处理数量"""
        return self._current
    
    def update(self, current: int, current_file: str) -> None:
        """更新进度
        
        Args:
            current: 当前已处理的数量
            current_file: 当前正在处理的文件名
        """
        self._current = current
        self._current_file = current_file
        self.progress_updated.emit(current, self._total, current_file)
        
        # Check if completed
        if current >= self._total:
            self.completed.emit()
    
    def get_percentage(self) -> float:
        """获取当前进度百分比
        
        Returns:
            float: 进度百分比 (0.0 - 100.0)
        """
        if self._total == 0:
            return 0.0
        return (self._current / self._total) * 100.0
    
    def reset(self, total: int) -> None:
        """重置进度追踪器
        
        Args:
            total: 新的总任务数量
        """
        self._total = total
        self._current = 0
        self._current_file = ""
