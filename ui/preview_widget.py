from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QListWidget
)
from PySide6.QtCore import Qt


class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setFixedWidth(120)
        self.thumbnail_list.setSpacing(5)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(400)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 600)
        scroll_area.setWidget(self.preview_label)

        main_layout.addWidget(self.thumbnail_list)
        main_layout.addWidget(scroll_area, 1)
