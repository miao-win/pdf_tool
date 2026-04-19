import fitz
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QListWidget, QListWidgetItem, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage


class CheckableThumbnailItem(QListWidgetItem):
    def __init__(self, page_num: int):
        super().__init__()
        self.page_num = page_num
        self.setData(Qt.ItemDataRole.UserRole, page_num)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(Qt.CheckState.Unchecked)


class PreviewWidget(QWidget):
    page_selected = Signal(int)
    selection_changed = Signal(list)

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
        self.thumbnail_list.itemChanged.connect(self._on_item_changed)

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
        self.thumbnail_list.blockSignals(True)
        self.thumbnail_list.clear()
        if not self._doc:
            self.thumbnail_list.blockSignals(False)
            return

        for page_num in range(self._doc.page_count):
            page = self._doc[page_num]
            # 根据主题设置不同的渲染参数
            pix = page.get_pixmap(
                matrix=fitz.Matrix(0.2, 0.2),
                colorspace=fitz.csRGB,
                alpha=False
            )
            img = QImage(pix.samples, pix.width, pix.height, QImage.Format.Format_RGBX)
            pixmap = QPixmap.fromImage(img)

            item = CheckableThumbnailItem(page_num)
            item.setSizeHint(QSize(110, 150))
            self.thumbnail_list.addItem(item)

            widget = QLabel()
            widget.setPixmap(pixmap.scaled(
                100, 140, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_label = QLabel(f'{page_num + 1}')
            page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_label.setStyleSheet('color: #64748B; font-size: 11px;')

            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addWidget(widget)
            container_layout.addWidget(page_label)
            self.thumbnail_list.setItemWidget(item, container)

        self.thumbnail_list.blockSignals(False)

    def _render_preview(self, page_num: int):
        if not self._doc or page_num < 0 or page_num >= self._doc.page_count:
            return

        self._current_page = page_num
        page = self._doc[page_num]

        matrix = fitz.Matrix(self._zoom, self._zoom)
        # 根据主题设置不同的渲染参数
        pix = page.get_pixmap(
            matrix=matrix,
            colorspace=fitz.csRGB,
            alpha=False
        )

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

    def _on_item_changed(self, item: CheckableThumbnailItem):
        self.selection_changed.emit(self.get_selected_pages())

    def get_selected_pages(self) -> List[int]:
        selected = []
        for i in range(self.thumbnail_list.count()):
            item = self.thumbnail_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.page_num)
        return selected

    def clear_selection(self):
        for i in range(self.thumbnail_list.count()):
            item = self.thumbnail_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

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
