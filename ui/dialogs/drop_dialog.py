"""
拖放选择对话框 480×320
6 按钮图标 IconWidget
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QSize, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont

from ui.widgets.icon import IconWidget
from ui.widgets.painters import CornerMarks
from utils.theme_manager import get_theme_manager


class DropDialog(QDialog):
    """拖放文件后选择功能的对话框"""
    function_selected = Signal(str)

    FUNCTIONS = [
        ('split', '拆分', 'split'),
        ('merge', '合并', 'merge'),
        ('compress', '压缩', 'compress'),
        ('edit', '页面编辑', 'edit'),
        ('pdf_to_image', '转图片', 'pdf_to_image'),
        ('to_pdf', '转PDF', 'to_pdf'),
    ]

    def __init__(self, file_name: str = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle('选择功能')
        self.setFixedSize(480, 320)
        self.file_name = file_name
        self.theme = get_theme_manager().current_theme
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 文件提示
        self.file_label = QLabel(f'已识别文件: {self.file_name}')
        self.file_label.setObjectName('subtitle')
        layout.addWidget(self.file_label)

        self.hint_label = QLabel('请选择要执行的操作:')
        self.hint_label.setObjectName('caption')
        layout.addWidget(self.hint_label)

        # 功能按钮网格
        grid = QHBoxLayout()
        grid.setSpacing(12)

        for func_id, func_name, icon_name in self.FUNCTIONS:
            btn = self._create_func_button(func_id, func_name, icon_name)
            grid.addWidget(btn)

        layout.addLayout(grid)
        layout.addStretch()

    def _create_func_button(self, func_id: str, func_name: str, icon_name: str):
        btn = QWidget(self)
        btn.setFixedSize(64, 80)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.func_id = func_id
        btn.mousePressEvent = lambda e: self._on_func_clicked(func_id)

        # 绘制在paintEvent中
        btn.paintEvent = lambda e, b=btn, i=icon_name, n=func_name: self._paint_func_button(b, i, n)
        return btn

    def _paint_func_button(self, btn, icon_name, func_name):
        p = QPainter(btn)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = btn.width(), btn.height()

        # 角标（科幻风）
        if self.theme == 'scifi':
            marks = CornerMarks(btn)
            marks.set_theme('scifi')
            marks.set_active(True)
            marks.render(p, QPoint(0, 0))

        # 图标
        icon = IconWidget(icon_name, 28, self.theme)
        icon.render(p, QPoint((w - 28)//2, 8))

        # 文字
        font = QFont()
        font.setPointSize(11)
        p.setFont(font)
        text_color = QColor('#1F2328' if self.theme == 'minimal' else '#1C1B1A' if self.theme == 'ink' else '#E2F3FF')
        p.setPen(text_color)
        p.drawText(0, 48, w, 20, Qt.AlignmentFlag.AlignCenter, func_name)

    def _on_func_clicked(self, func_id: str):
        self.function_selected.emit(func_id)
        self.accept()

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()
