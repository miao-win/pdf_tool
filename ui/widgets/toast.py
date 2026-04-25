"""
Toast 提示组件 320×60px 4s
三主题各自风格
"""
import random

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QFont

from ui.widgets.icon import IconWidget
from ui.widgets.painters import CinnabarSeal
from utils.theme_manager import get_theme_manager


class Toast(QWidget):
    """Toast 提示"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 60)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.theme = 'minimal'
        self._opacity = 1.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.hide)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)

        self.text_label = QLabel()
        self.text_label.setObjectName('caption')
        layout.addWidget(self.text_label, 1)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def show_message(self, message: str, msg_type: str = 'success'):
        self.text_label.setText(message)
        self.theme = get_theme_manager().current_theme

        if self.theme == 'minimal':
            if msg_type == 'success':
                self._draw_icon = lambda: IconWidget('check', 20, 'minimal')
            elif msg_type == 'error':
                self._draw_icon = lambda: IconWidget('error', 20, 'minimal')
            else:
                self._draw_icon = lambda: IconWidget('info', 20, 'minimal')
        elif self.theme == 'ink':
            self._draw_icon = lambda: CinnabarSeal('成' if msg_type == 'success' else '错', 20)
        elif self.theme == 'scifi':
            self._draw_icon = lambda: IconWidget('check' if msg_type == 'success' else 'error', 20, 'scifi')

        self.setWindowOpacity(0.0)
        self.show()

        anim = QPropertyAnimation(self, b'windowOpacity')
        anim.setDuration(200)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()

        self._timer.start(4000)

    def hide(self):
        anim = QPropertyAnimation(self, b'windowOpacity')
        anim.setDuration(200)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(super().hide)
        anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.theme == 'minimal':
            p.fillRect(self.rect(), QColor('#FFFFFF'))
            p.setPen(QPen(QColor('#E5E7EB'), 1))
            p.drawRoundedRect(1, 1, 318, 58, 10, 10)
            # 绿色左边框
            p.fillRect(0, 10, 3, 40, QColor('#22C55E'))
        elif self.theme == 'ink':
            p.fillRect(self.rect(), QColor('#FBF6E9'))
            p.setPen(QPen(QColor('#D4C9B0'), 1))
            p.drawRoundedRect(1, 1, 318, 58, 4, 4)
            # 宣纸噪点效果简化
            p.setPen(Qt.PenStyle.NoPen)
            for _ in range(20):
                x = random.randint(0, 320)
                y = random.randint(0, 60)
                p.setBrush(QColor(212, 201, 176, random.randint(20, 50)))
                p.drawEllipse(x, y, 1, 1)
        elif self.theme == 'scifi':
            p.fillRect(self.rect(), QColor('#111826'))
            p.setPen(QPen(QColor('#1A2A3A'), 1))
            p.drawRoundedRect(1, 1, 318, 58, 2, 2)
            # 青蓝边框
            p.setPen(QPen(QColor('#00E5FF'), 1))
            p.drawLine(0, 10, 0, 50)

        # 绘制图标
        if hasattr(self, '_draw_icon'):
            icon = self._draw_icon()
            icon.render(p, QPoint(16, 20))

        # 科幻风额外文本
        if self.theme == 'scifi':
            font = QFont("Share Tech Mono", 9)
            p.setFont(font)
            p.setPen(QColor('#6D8299'))
            p.drawText(250, 45, '[ OK ]')
