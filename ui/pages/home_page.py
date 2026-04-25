"""
主页 - 三主题适配
欢迎语 + 3×2 卡片徽章 + 拖放区
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath

from ui.widgets.icon import IconWidget
from ui.widgets.painters import CinnabarSeal, CornerMarks
from utils.theme_manager import get_theme_manager


class FeatureCard(QFrame):
    clicked = Signal(str)

    def __init__(self, name: str, description: str, icon_name: str, card_id: str, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.name = name
        self.description = description
        self.icon_name = icon_name
        self.theme = 'minimal'
        self._hovered = False
        self.setFixedSize(260, 160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName('card')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit(self.card_id)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # 背景
        if self.theme == 'minimal':
            p.fillRect(self.rect(), QColor('#FFFFFF'))
            if self._hovered:
                p.fillRect(self.rect(), QColor(0, 0, 0, 3))
                p.setPen(QPen(QColor('#2E6BE6'), 2))
                p.drawRoundedRect(1, 1, w-2, h-2, 10, 10)
            else:
                p.setPen(QPen(QColor('#E5E7EB'), 1))
                p.drawRoundedRect(1, 1, w-2, h-2, 10, 10)
        elif self.theme == 'ink':
            p.fillRect(self.rect(), QColor('#FBF6E9'))
            if self._hovered:
                # 墨晕效果
                for i in range(3):
                    alpha = 15 - i * 4
                    p.setPen(QPen(QColor(184, 168, 138, alpha), 4 + i*2))
                    p.drawRoundedRect(2-i, 2-i, w-4+i*2, h-4+i*2, 4, 4)
            p.setPen(QPen(QColor('#D4C9B0'), 1))
            p.drawRoundedRect(1, 1, w-2, h-2, 4, 4)
        elif self.theme == 'scifi':
            p.fillRect(self.rect(), QColor('#162236'))
            if self._hovered:
                p.setPen(QPen(QColor('#00E5FF'), 1.5))
                glow = QPen(QColor(0, 229, 255, 40), 3)
                p.setPen(glow)
                p.drawRoundedRect(1, 1, w-2, h-2, 2, 2)
                p.setPen(QPen(QColor('#00E5FF'), 1.5))
            else:
                p.setPen(QPen(QColor('#1E3450'), 1))
            p.drawRoundedRect(1, 1, w-2, h-2, 2, 2)

        # 图标
        icon = IconWidget(self.icon_name, 32, self.theme)
        icon.render(p, QPoint(16, 16))

        # 标题
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        p.setFont(font)
        text_color = QColor('#1F2328' if self.theme == 'minimal' else '#1C1B1A' if self.theme == 'ink' else '#E2F3FF')
        p.setPen(text_color)
        p.drawText(16, 68, self.name)

        # 描述
        font.setPointSize(12)
        font.setBold(False)
        p.setFont(font)
        desc_color = QColor('#57606A' if self.theme == 'minimal' else '#5C5650' if self.theme == 'ink' else '#8FAEC8')
        p.setPen(desc_color)
        p.drawText(16, 92, 228, 60, Qt.TextFlag.TextWordWrap, self.description)


class HomePage(QWidget):
    split_clicked = Signal()
    merge_clicked = Signal()
    compress_clicked = Signal()
    page_editor_clicked = Signal()
    pdf_to_image_clicked = Signal()
    to_pdf_clicked = Signal()
    files_dropped = Signal(list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = 'minimal'
        self._init_ui()
        self.setAcceptDrops(True)

        # 监听主题变化
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # 欢迎语
        self.welcome_widget = QWidget(self)
        self.welcome_widget.setMinimumHeight(80)
        layout.addWidget(self.welcome_widget)

        # 欢迎文字（在paintEvent中绘制）
        self.welcome_label = QLabel('欢迎使用 PDF 工具箱')
        self.welcome_label.setObjectName('title')
        font = QFont("Inter", 20)
        font.setBold(True)
        self.welcome_label.setFont(font)
        layout.addWidget(self.welcome_label)

        self.subtitle_label = QLabel('选择下方功能开始处理您的 PDF 文件')
        self.subtitle_label.setObjectName('subtitle')
        layout.addWidget(self.subtitle_label)

        # 卡片网格
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cards_data = [
            ('拆分 PDF', '按页码范围或固定页数\n将 PDF 拆分为多个文件', 'split', 'split'),
            ('合并 PDF', '将多个 PDF 文件合并\n支持指定页码范围', 'merge', 'merge'),
            ('压缩 PDF', '低/中/高三档压缩\n减小文件体积', 'compress', 'compress'),
            ('页面编辑', '旋转、删除 PDF 页面\n支持页码范围指定', 'edit', 'page_editor'),
            ('PDF 转图片', '将 PDF 页面转换为\nPNG/JPG 图片格式', 'pdf_to_image', 'pdf_to_image'),
            ('转为 PDF', '图片/Word/PPT\n转换为 PDF 格式', 'to_pdf', 'to_pdf'),
        ]

        self.cards = {}
        for i, (name, desc, icon, cid) in enumerate(cards_data):
            card = FeatureCard(name, desc, icon, cid)
            card.clicked.connect(self._on_card_clicked)
            grid.addWidget(card, i // 3, i % 3)
            self.cards[cid] = card

        layout.addLayout(grid)

        # 拖放区
        self.drop_zone = QWidget(self)
        self.drop_zone.setMinimumHeight(120)
        self.drop_zone.setAcceptDrops(True)
        layout.addWidget(self.drop_zone)

        drop_layout = QVBoxLayout(self.drop_zone)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.drop_icon = IconWidget('drag', 32, 'minimal')
        drop_layout.addWidget(self.drop_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        self.drop_label = QLabel('拖拽 PDF 文件到此处')
        self.drop_label.setObjectName('subtitle')
        drop_layout.addWidget(self.drop_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def _on_theme_changed(self, theme: str):
        self.theme = theme
        self.drop_icon.set_theme(theme)
        for card in self.cards.values():
            card.set_theme(theme)
        self.update()

    def _on_card_clicked(self, card_id: str):
        signal_map = {
            'split': self.split_clicked,
            'merge': self.merge_clicked,
            'compress': self.compress_clicked,
            'page_editor': self.page_editor_clicked,
            'pdf_to_image': self.pdf_to_image_clicked,
            'to_pdf': self.to_pdf_clicked,
        }
        if card_id in signal_map:
            signal_map[card_id].emit()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.theme == 'ink':
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            seal = CinnabarSeal('工', 32)
            seal.set_theme('ink')
            seal.render(p, QPoint(self.width() - 80, 20))
            p.end()
        elif self.theme == 'scifi':
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(QPen(QColor(0, 229, 255, 30), 1))
            p.drawLine(40, 30, self.width() - 40, 30)
            p.setPen(QPen(QColor(255, 46, 154, 20), 1))
            p.drawLine(42, 32, self.width() - 38, 32)
            p.end()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            if file_paths:
                self.files_dropped.emit(file_paths, 'home')
            event.acceptProposedAction()
