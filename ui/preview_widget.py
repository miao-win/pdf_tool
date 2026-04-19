import fitz
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage


class ThumbnailItem(QListWidgetItem):
    def __init__(self, page_num: int, pixmap: QPixmap):
        super().__init__()
        self.page_num = page_num
        self.setData(Qt.ItemDataRole.UserRole, page_num)


class PreviewWidget(QWidget):
    page_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc = None
        self._current_page = 0
        self._zoom = 1.0
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setFixedWidth(120)
        self.thumbnail_list.setSpacing(5)
        self.thumbnail_list.currentRowChanged.connect(self._on_thumbnail_selected)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(400)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 600)
        scroll_area.setWidget(self.preview_label)

        main_layout.addWidget(self.thumbnail_list)
        main_layout.addWidget(scroll_area, 1)

    def load_pdf(self, pdf_path: Path):
        try:
            self._doc = fitz.open(str(pdf_path))
            self._render_thumbnails()
            if self._doc.page_count > 0:
                self._render_preview(0)
        except Exception as e:
            self._doc = None

    def _render_thumbnails(self):
        self.thumbnail_list.clear()
        if not self._doc:
            return

        for page_num in range(self._doc.page_count):
            page = self._doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            img = QImage(pix.samples, pix.width, pix.height, QImage.Format.Format_RGBX)
            pixmap = QPixmap.fromImage(img)

            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, page_num)
            item.setSizeHint(QSize(110, 150))
            self.thumbnail_list.addItem(item)

            from PySide6.QtWidgets import QLabel
            widget = QLabel()
            widget.setPixmap(pixmap.scaled(
                100, 140, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.thumbnail_list.setItemWidget(item, widget)

    def _render_preview(self, page_num: int):
        if not self._doc or page_num < 0 or page_num >= self._doc.page_count:
            return

        self._current_page = page_num
        page = self._doc[page_num]

        base_dpi = 72
        matrix = fitz.Matrix(self._zoom, self._zoom)
        pix = page.get_pixmap(matrix=matrix)

        img = QImage(pix.samples, pix.width, pix.height, QImage.Format.Format_RGBX)
        pixmap = QPixmap.fromImage(img)

        self.preview_label.setPixmap(pixmap.scaled(
            int(400 * self._zoom), int(600 * self._zoom),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.thumbnail_list.setCurrentRow(page_num)

    def _on_thumbnail_selected(self, row: int):
        if row >= 0:
            self._render_preview(row)
            self.page_selected.emit(row)

    def set_zoom(self, zoom: float):
        self._zoom = max(0.5, min(3.0, zoom))
        if self._doc and self._current_page < self._doc.page_count:
            self._render_preview(self._current_page)

    def zoom_in(self):
        self.set_zoom(self._zoom + 0.25)

    def zoom_out(self):
        self.set_zoom(self._zoom - 0.25)

    def get_current_page(self) -> int:
        return self._current_page

    def close_pdf(self):
        if self._doc:
            self._doc.close()
            self._doc = None
        self.thumbnail_list.clear()
        self.preview_label.clear()
