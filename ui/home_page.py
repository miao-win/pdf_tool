from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Property, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QIcon, QPixmap, QImage


class AnimatedCard(QWidget):
    clicked = Signal(str)

    def __init__(self, name: str, description: str, icon_path: str, color: str, parent=None):
        super().__init__(parent)
        self._name = name
        self._description = description
        self._icon_path = icon_path
        self._base_color = QColor(color)
        self._hovered = False
        self._elevation = 0
        self.setFixedSize(280, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.installEventFilter(self)

        self._animation = QPropertyAnimation(self, b'elevation')
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_elevation(self) -> int:
        return self._elevation

    def set_elevation(self, value: int):
        self._elevation = value
        self.update()

    elevation = Property(int, get_elevation, set_elevation)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.Enter:
            self._hovered = True
            self._animation.setStartValue(self._elevation)
            self._animation.setEndValue(10)
            self._animation.start()
        elif event.type() == QEvent.Type.Leave:
            self._hovered = False
            self._animation.setStartValue(self._elevation)
            self._animation.setEndValue(0)
            self._animation.start()
        elif event.type() == QEvent.Type.MouseButtonPress:
            self.clicked.emit(self._name)
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)

        if self._hovered:
            self._base_color.setAlpha(230)
            pen = QPen(QColor(255, 255, 255, 100))
            pen.setWidth(2)
            painter.setPen(pen)
        else:
            self._base_color.setAlpha(200)
            painter.setPen(Qt.PenStyle.NoPen)

        shadow_color = QColor(0, 0, 0, min(30 + self._elevation * 3, 60))
        painter.setBrush(QBrush(shadow_color))
        painter.drawRoundedRect(rect.adjusted(2, 2, 2, 2), 16, 16)

        painter.setBrush(QBrush(self._base_color))
        painter.drawRoundedRect(rect, 16, 16)

        margin = 24
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(margin, 45, self._name)

        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255, 180)))
        text_rect = self.rect().adjusted(margin, 60, -margin, -margin)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.TextWordWrap, self._description)


class FeatureCardGrid(QWidget):
    split_clicked = Signal()
    merge_clicked = Signal()
    compress_clicked = Signal()
    page_editor_clicked = Signal()
    pdf_to_image_clicked = Signal()
    to_pdf_clicked = Signal()
    files_dropped = Signal(list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        title_label = QLabel('PDF 工具箱')
        title_label.setObjectName('homeTitle')
        main_layout.addWidget(title_label)

        subtitle_label = QLabel('简单、快速、本地运行的 PDF 处理工具')
        subtitle_label.setObjectName('homeSubtitle')
        main_layout.addWidget(subtitle_label)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.split_card = AnimatedCard(
            '拆分 PDF',
            '按页码范围或固定页数\n将 PDF 拆分为多个文件',
            'split',
            '#2563EB'
        )
        self.split_card.clicked.connect(lambda n: self.split_clicked.emit())
        grid_layout.addWidget(self.split_card, 0, 0)

        self.merge_card = AnimatedCard(
            '合并 PDF',
            '将多个 PDF 文件合并\n支持指定页码范围',
            'merge',
            '#16A34A'
        )
        self.merge_card.clicked.connect(lambda n: self.merge_clicked.emit())
        grid_layout.addWidget(self.merge_card, 0, 1)

        self.compress_card = AnimatedCard(
            '压缩 PDF',
            '低/中/高三档压缩\n减小文件体积',
            'compress',
            '#EA580C'
        )
        self.compress_card.clicked.connect(lambda n: self.compress_clicked.emit())
        grid_layout.addWidget(self.compress_card, 0, 2)

        self.page_editor_card = AnimatedCard(
            '页面编辑',
            '旋转、删除 PDF 页面\n支持页码范围指定',
            'edit',
            '#7C3AED'
        )
        self.page_editor_card.clicked.connect(lambda n: self.page_editor_clicked.emit())
        grid_layout.addWidget(self.page_editor_card, 1, 0)

        self.pdf_to_image_card = AnimatedCard(
            'PDF 转图片',
            '将 PDF 页面转换为\nPNG/JPG 图片格式',
            'image',
            '#0891B2'
        )
        self.pdf_to_image_card.clicked.connect(lambda n: self.pdf_to_image_clicked.emit())
        grid_layout.addWidget(self.pdf_to_image_card, 1, 1)

        self.to_pdf_card = AnimatedCard(
            '转为 PDF',
            '图片/Word/PPT\n转换为 PDF 格式',
            'pdf',
            '#DB2777'
        )
        self.to_pdf_card.clicked.connect(lambda n: self.to_pdf_clicked.emit())
        grid_layout.addWidget(self.to_pdf_card, 1, 2)

        main_layout.addLayout(grid_layout)

        drop_hint = QLabel('或拖拽 PDF 文件到此处')
        drop_hint.setObjectName('dropHint')
        main_layout.addWidget(drop_hint)

    def on_files_dropped(self, file_paths: list):
        self.files_dropped.emit(file_paths, 'home')


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
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        self.card_grid = FeatureCardGrid()
        main_layout.addWidget(self.card_grid)

        self.card_grid.split_clicked.connect(self.split_clicked.emit)
        self.card_grid.merge_clicked.connect(self.merge_clicked.emit)
        self.card_grid.compress_clicked.connect(self.compress_clicked.emit)
        self.card_grid.page_editor_clicked.connect(self.page_editor_clicked.emit)
        self.card_grid.pdf_to_image_clicked.connect(self.pdf_to_image_clicked.emit)
        self.card_grid.to_pdf_clicked.connect(self.to_pdf_clicked.emit)
        self.card_grid.files_dropped.connect(self.files_dropped.emit)

        self.setAcceptDrops(True)



    def dragEnterEvent(self, event):
        from PySide6.QtGui import QDragEnterEvent
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        from PySide6.QtGui import QDropEvent
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            if file_paths:
                self.files_dropped.emit(file_paths, 'home')
            event.acceptProposedAction()

    def on_files_dropped(self, file_paths: list):
        self.files_dropped.emit(file_paths, 'home')
