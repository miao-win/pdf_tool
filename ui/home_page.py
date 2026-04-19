from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath


class FeatureCard(QWidget):
    clicked = Signal()

    def __init__(self, title: str, description: str, color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.card_color = QColor(color)
        self._hovered = False
        self.setFixedSize(280, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.Enter:
            self._hovered = True
            self.update()
        elif event.type() == QEvent.Type.Leave:
            self._hovered = False
            self.update()
        elif event.type() == QEvent.Type.MouseButtonPress:
            self.clicked.emit()
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)

        if self._hovered:
            self.card_color.setAlpha(230)
        else:
            self.card_color.setAlpha(200)

        painter.setBrush(QBrush(self.card_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 16, 16)

        margin = 24
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawText(
            margin, 50,
            self.title
        )

        painter.setPen(QPen(QColor(255, 255, 255, 180)))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        text_rect = self.rect().adjusted(margin, 70, -margin, -margin)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.TextWordWrap, self.description)


class HomePage(QWidget):
    split_clicked = Signal()
    merge_clicked = Signal()
    compress_clicked = Signal()
    files_dropped = Signal(list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(40)

        title_label = QLabel('PDF 工具箱')
        title_label.setObjectName('homeTitle')
        main_layout.addWidget(title_label)

        subtitle_label = QLabel('简单、快速、本地运行的 PDF 处理工具')
        subtitle_label.setObjectName('homeSubtitle')
        main_layout.addWidget(subtitle_label)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        self.split_card = FeatureCard(
            '拆分 PDF',
            '按页码范围或固定页数\n将 PDF 拆分为多个文件',
            '#4A90D9'
        )
        self.split_card.clicked.connect(self.split_clicked)
        cards_layout.addWidget(self.split_card)

        self.merge_card = FeatureCard(
            '合并 PDF',
            '将多个 PDF 文件合并\n支持指定页码范围',
            '#5BA55B'
        )
        self.merge_card.clicked.connect(self.merge_clicked)
        cards_layout.addWidget(self.merge_card)

        self.compress_card = FeatureCard(
            '压缩 PDF',
            '低/中/高三档压缩\n减小文件体积',
            '#E67E22'
        )
        self.compress_card.clicked.connect(self.compress_clicked)
        cards_layout.addWidget(self.compress_card)

        main_layout.addLayout(cards_layout)

        drop_hint = QLabel('或拖拽 PDF 文件到此处')
        drop_hint.setObjectName('dropHint')
        main_layout.addWidget(drop_hint)

    def on_files_dropped(self, file_paths: list):
        self.files_dropped.emit(file_paths, 'home')
