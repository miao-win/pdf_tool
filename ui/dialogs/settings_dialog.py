"""
设置浮层 320px 宽
主题预览 90×60px 纯自绘矢量示意
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient

from utils.theme_manager import get_theme_manager


class ThemePreview(QWidget):
    """主题预览组件 90×60"""
    def __init__(self, theme_name: str, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.setFixedSize(90, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.theme_name == 'minimal':
            # 白底+蓝标题+灰卡片
            p.fillRect(0, 0, 90, 60, QColor('#FAFAFA'))
            p.fillRect(4, 4, 82, 12, QColor('#FFFFFF'))
            p.setPen(QPen(QColor('#2E6BE6'), 2))
            p.drawLine(8, 10, 20, 10)
            p.fillRect(4, 20, 82, 36, QColor('#FFFFFF'))
            p.setPen(QPen(QColor('#E5E7EB'), 1))
            p.drawRoundedRect(4, 20, 82, 36, 4, 4)
            p.fillRect(10, 30, 30, 8, QColor('#2E6BE6'))
        elif self.theme_name == 'ink':
            # 米黄底+朱砂标题+卡片
            p.fillRect(0, 0, 90, 60, QColor('#F4EEDF'))
            p.fillRect(4, 4, 82, 12, QColor('#FBF6E9'))
            p.setPen(QPen(QColor('#8B2B2B'), 2))
            p.drawLine(8, 10, 20, 10)
            p.fillRect(4, 20, 82, 36, QColor('#FBF6E9'))
            p.setPen(QPen(QColor('#D4C9B0'), 1))
            p.drawRect(4, 20, 82, 36)
            p.fillRect(10, 30, 30, 8, QColor('#8B2B2B'))
        elif self.theme_name == 'scifi':
            # 黑底+青蓝标题+卡片
            p.fillRect(0, 0, 90, 60, QColor('#0A0E14'))
            p.fillRect(4, 4, 82, 12, QColor('#111826'))
            p.setPen(QPen(QColor('#00E5FF'), 1))
            p.drawLine(8, 10, 20, 10)
            p.fillRect(4, 20, 82, 36, QColor('#111826'))
            p.setPen(QPen(QColor('#1A2A3A'), 1))
            p.drawRect(4, 20, 82, 36)
            p.fillRect(10, 30, 30, 8, QColor('#00E5FF'))


class SettingsDialog(QDialog):
    """设置浮层"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setFixedWidth(320)
        self.theme = get_theme_manager().current_theme
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 主题选择
        theme_label = QLabel('主题')
        theme_label.setObjectName('subtitle')
        layout.addWidget(theme_label)

        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(12)

        self.previews = {}
        for theme_name in ['minimal', 'ink', 'scifi']:
            preview = ThemePreview(theme_name)
            preview.mousePressEvent = lambda e, t=theme_name: self._on_theme_selected(t)
            preview_layout.addWidget(preview)
            self.previews[theme_name] = preview

        layout.addLayout(preview_layout)

        # 主题名称
        names = {'minimal': '简约', 'ink': '水墨', 'scifi': '科幻'}
        name_layout = QHBoxLayout()
        for theme_name in ['minimal', 'ink', 'scifi']:
            lbl = QLabel(names[theme_name])
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedWidth(90)
            name_layout.addWidget(lbl)
        layout.addLayout(name_layout)

        layout.addStretch()

        # 关闭按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _on_theme_selected(self, theme_name: str):
        theme_manager = get_theme_manager()
        theme_manager.apply(theme_name)
        self.theme = theme_name
        self.update()
