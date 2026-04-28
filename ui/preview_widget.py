from pathlib import Path
from typing import List, Optional, Tuple

import pymupdf
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QListWidget, QListWidgetItem, QPushButton,
    QLineEdit, QSizePolicy, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage

from utils.constants import (
    PREVIEW_MIN_WIDTH, PREVIEW_PLACEHOLDER_MIN_WIDTH, PREVIEW_PLACEHOLDER_MIN_HEIGHT,
    PREVIEW_LABEL_MIN_WIDTH, PREVIEW_LABEL_MIN_HEIGHT, THUMBNAIL_LIST_WIDTH,
    THUMBNAIL_ITEM_HEIGHT, THUMBNAIL_SCALE, NAV_BAR_HEIGHT, NAV_BUTTON_SIZE,
    NAV_BUTTON_HEIGHT, MAX_RENDER_ZOOM, MIN_LABEL_SIZE,
)
from utils.pdf_cache import get_pdf_cache
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PreviewWidget(QWidget):
    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc = None
        self._current_page = 0
        self._total_pages = 0
        self._image_paths: List[Path] = []
        self._current_image_index = 0
        self._mode = None
        self._render_cache: dict = {}
        self._pdf_cache = get_pdf_cache()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._placeholder = QLabel('拖拽文件到左侧区域开始预览')
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setObjectName('previewPlaceholder')
        self._placeholder.setMinimumSize(PREVIEW_PLACEHOLDER_MIN_WIDTH, PREVIEW_PLACEHOLDER_MIN_HEIGHT)
        main_layout.addWidget(self._placeholder)

        self._viewer_widget = QWidget()
        viewer_layout = QVBoxLayout(self._viewer_widget)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer_layout.setSpacing(0)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)

        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setFixedWidth(THUMBNAIL_LIST_WIDTH)
        self.thumbnail_list.setSpacing(4)
        self.thumbnail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.thumbnail_list.currentRowChanged.connect(self._on_thumbnail_clicked)
        content_layout.addWidget(self.thumbnail_list)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setObjectName('previewScrollArea')

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(PREVIEW_LABEL_MIN_WIDTH, PREVIEW_LABEL_MIN_HEIGHT)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area.setWidget(self.preview_label)

        content_layout.addWidget(scroll_area, 1)

        viewer_layout.addLayout(content_layout, 1)

        nav_bar = QWidget()
        nav_bar.setObjectName('previewNavBar')
        nav_bar.setFixedHeight(NAV_BAR_HEIGHT)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(8, 4, 8, 4)

        self._prev_btn = QPushButton('◀')
        self._prev_btn.setFixedSize(NAV_BUTTON_SIZE, NAV_BUTTON_HEIGHT)
        self._prev_btn.setObjectName('navBtn')
        self._prev_btn.clicked.connect(self.prev_page)
        nav_layout.addWidget(self._prev_btn)

        nav_layout.addStretch()

        self._page_label = QLabel('0 / 0')
        self._page_label.setObjectName('previewPageLabel')
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self._page_label)

        nav_layout.addStretch()

        self._page_spin = QSpinBox()
        self._page_spin.setFixedWidth(70)
        self._page_spin.setMinimum(1)
        self._page_spin.setObjectName('previewPageSpin')
        self._page_spin.valueChanged.connect(self._on_spin_changed)
        nav_layout.addWidget(self._page_spin)

        self._next_btn = QPushButton('▶')
        self._next_btn.setFixedSize(NAV_BUTTON_SIZE, NAV_BUTTON_HEIGHT)
        self._next_btn.setObjectName('navBtn')
        self._next_btn.clicked.connect(self.next_page)
        nav_layout.addWidget(self._next_btn)

        viewer_layout.addWidget(nav_bar)

        self._viewer_widget.setVisible(False)
        main_layout.addWidget(self._viewer_widget)

    def _cache_key(self, page_idx: int, width: int, height: int) -> Tuple:
        return (page_idx, width, height)

    def _get_cached_pixmap(self, page_idx: int, width: int, height: int) -> Optional[QPixmap]:
        key = self._cache_key(page_idx, width, height)
        return self._render_cache.get(key)

    def _set_cached_pixmap(self, page_idx: int, width: int, height: int, pixmap: QPixmap):
        if len(self._render_cache) > 20:
            oldest_key = next(iter(self._render_cache))
            del self._render_cache[oldest_key]
        key = self._cache_key(page_idx, width, height)
        self._render_cache[key] = pixmap

    def _invalidate_cache(self):
        self._render_cache.clear()

    def load_pdf(self, path: Path):
        self.clear()
        try:
            self._doc = pymupdf.open(str(path))
            self._total_pages = len(self._doc)
            self._current_page = 0
            self._mode = 'pdf'

            self._pdf_cache.get_page_count_or_load(path)

            self._viewer_widget.setVisible(True)
            self._placeholder.setVisible(False)

            self._page_spin.setRange(1, self._total_pages)
            self._page_spin.setValue(1)

            self._generate_thumbnails()
            self._render_current_page()
        except Exception as e:
            logger.error("Failed to load PDF %s: %s", path, e, exc_info=True)
            self._placeholder.setText(f'无法打开 PDF:\n{e}')
            self._placeholder.setVisible(True)
            self._viewer_widget.setVisible(False)

    def load_images(self, paths: List[Path]):
        self.clear()
        valid_paths = [p for p in paths if p.exists() and p.suffix.lower() in {
            '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp'
        }]
        if not valid_paths:
            self._placeholder.setText('没有可预览的图片')
            return

        self._image_paths = valid_paths
        self._current_image_index = 0
        self._mode = 'images'
        self._total_pages = len(valid_paths)

        self._viewer_widget.setVisible(True)
        self._placeholder.setVisible(False)

        self._page_spin.setRange(1, self._total_pages)
        self._page_spin.setValue(1)

        self._generate_image_thumbnails()
        self._render_current_image()

    def clear(self):
        if self._doc:
            self._doc.close()
            self._doc = None
        self._current_page = 0
        self._total_pages = 0
        self._image_paths.clear()
        self._current_image_index = 0
        self._mode = None
        self._invalidate_cache()
        self.thumbnail_list.clear()
        self.preview_label.clear()
        self._page_label.setText('0 / 0')
        self._viewer_widget.setVisible(False)
        self._placeholder.setVisible(True)
        self._placeholder.setText('拖拽文件到左侧区域开始预览')

    def prev_page(self):
        if self._mode == 'pdf' and self._current_page > 0:
            self._current_page -= 1
            self._render_current_page()
            self._sync_nav()
        elif self._mode == 'images' and self._current_image_index > 0:
            self._current_image_index -= 1
            self._render_current_image()
            self._sync_nav()

    def next_page(self):
        if self._mode == 'pdf' and self._current_page < self._total_pages - 1:
            self._current_page += 1
            self._render_current_page()
            self._sync_nav()
        elif self._mode == 'images' and self._current_image_index < self._total_pages - 1:
            self._current_image_index += 1
            self._render_current_image()
            self._sync_nav()

    def go_to_page(self, page: int):
        if self._mode == 'pdf':
            idx = max(0, min(page - 1, self._total_pages - 1))
            if idx != self._current_page:
                self._current_page = idx
                self._render_current_page()
                self._sync_nav()
        elif self._mode == 'images':
            idx = max(0, min(page - 1, self._total_pages - 1))
            if idx != self._current_image_index:
                self._current_image_index = idx
                self._render_current_image()
                self._sync_nav()

    def current_page_index(self) -> int:
        if self._mode == 'pdf':
            return self._current_page
        elif self._mode == 'images':
            return self._current_image_index
        return 0

    def total_pages(self) -> int:
        return self._total_pages

    def _on_thumbnail_clicked(self, row: int):
        if row < 0:
            return
        if self._mode == 'pdf':
            self._current_page = row
            self._render_current_page()
            self._sync_nav(skip_thumbnail=True)
        elif self._mode == 'images':
            self._current_image_index = row
            self._render_current_image()
            self._sync_nav(skip_thumbnail=True)

    def _on_spin_changed(self, value: int):
        if self._mode == 'pdf':
            idx = value - 1
            if 0 <= idx < self._total_pages and idx != self._current_page:
                self._current_page = idx
                self._render_current_page()
                self._sync_nav(skip_spin=True)
        elif self._mode == 'images':
            idx = value - 1
            if 0 <= idx < self._total_pages and idx != self._current_image_index:
                self._current_image_index = idx
                self._render_current_image()
                self._sync_nav(skip_spin=True)

    def _sync_nav(self, skip_thumbnail=False, skip_spin=False):
        if self._mode == 'pdf':
            page_num = self._current_page + 1
        elif self._mode == 'images':
            page_num = self._current_image_index + 1
        else:
            return

        self._page_label.setText(f'{page_num} / {self._total_pages}')
        self._prev_btn.setEnabled(page_num > 1)
        self._next_btn.setEnabled(page_num < self._total_pages)

        if not skip_thumbnail:
            self.thumbnail_list.blockSignals(True)
            current = self._current_page if self._mode == 'pdf' else self._current_image_index
            self.thumbnail_list.setCurrentRow(current)
            self.thumbnail_list.blockSignals(False)

        if not skip_spin:
            self._page_spin.blockSignals(True)
            self._page_spin.setValue(page_num)
            self._page_spin.blockSignals(False)

        self.page_changed.emit(page_num)

    def _generate_thumbnails(self):
        self.thumbnail_list.clear()
        if not self._doc:
            return
        for i in range(self._total_pages):
            try:
                page = self._doc[i]
                mat = pymupdf.Matrix(THUMBNAIL_SCALE, THUMBNAIL_SCALE)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                item = QListWidgetItem()
                item.setText(f'{i + 1}')
                item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
                item.setSizeHint(QSize(THUMBNAIL_LIST_WIDTH, THUMBNAIL_ITEM_HEIGHT))
                self.thumbnail_list.addItem(item)
            except Exception as e:
                logger.warning("Failed to generate thumbnail for page %d: %s", i + 1, e)
                item = QListWidgetItem(f'{i + 1}')
                item.setSizeHint(QSize(THUMBNAIL_LIST_WIDTH, 30))
                self.thumbnail_list.addItem(item)

        if self._total_pages > 0:
            self.thumbnail_list.setCurrentRow(0)

    def _generate_image_thumbnails(self):
        self.thumbnail_list.clear()
        for i, path in enumerate(self._image_paths):
            try:
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    scaled = pixmap.scaled(THUMBNAIL_LIST_WIDTH, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    item = QListWidgetItem()
                    item.setText(f'{i + 1}')
                    item.setData(Qt.ItemDataRole.DecorationRole, scaled)
                    item.setSizeHint(QSize(THUMBNAIL_LIST_WIDTH, THUMBNAIL_ITEM_HEIGHT))
                    self.thumbnail_list.addItem(item)
                else:
                    item = QListWidgetItem(f'{i + 1}')
                    item.setSizeHint(QSize(THUMBNAIL_LIST_WIDTH, 30))
                    self.thumbnail_list.addItem(item)
            except Exception as e:
                logger.warning("Failed to generate thumbnail for image %s: %s", path, e)
                item = QListWidgetItem(f'{i + 1}')
                item.setSizeHint(QSize(THUMBNAIL_LIST_WIDTH, 30))
                self.thumbnail_list.addItem(item)

        if self._image_paths:
            self.thumbnail_list.setCurrentRow(0)

    def _render_current_page(self):
        if not self._doc or self._current_page >= self._total_pages:
            return
        try:
            label_size = self.preview_label.size()
            if label_size.width() < MIN_LABEL_SIZE or label_size.height() < MIN_LABEL_SIZE:
                label_size = QSize(PREVIEW_MIN_WIDTH, 700)

            cached = self._get_cached_pixmap(self._current_page, label_size.width(), label_size.height())
            if cached:
                self.preview_label.setPixmap(cached)
                return

            page = self._doc[self._current_page]
            zoom_x = label_size.width() / page.rect.width
            zoom_y = label_size.height() / page.rect.height
            zoom = min(zoom_x, zoom_y, MAX_RENDER_ZOOM)
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            scaled = pixmap.scaled(
                label_size.width(), label_size.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._set_cached_pixmap(self._current_page, label_size.width(), label_size.height(), scaled)
            self.preview_label.setPixmap(scaled)
        except Exception as e:
            logger.error("Failed to render page %d: %s", self._current_page + 1, e, exc_info=True)
            self.preview_label.setText(f'渲染失败: {e}')

    def _render_current_image(self):
        if not self._image_paths or self._current_image_index >= len(self._image_paths):
            return
        try:
            path = self._image_paths[self._current_image_index]
            pixmap = QPixmap(str(path))
            if pixmap.isNull():
                self.preview_label.setText(f'无法加载图片:\n{path.name}')
                return
            label_size = self.preview_label.size()
            if label_size.width() < MIN_LABEL_SIZE or label_size.height() < MIN_LABEL_SIZE:
                label_size = QSize(PREVIEW_MIN_WIDTH, 700)
            scaled = pixmap.scaled(
                label_size.width() - 20, label_size.height() - 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
        except Exception as e:
            logger.error("Failed to load image %s: %s", path, e, exc_info=True)
            self.preview_label.setText(f'加载图片失败: {e}')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._invalidate_cache()
        if self._mode == 'pdf':
            self._render_current_page()
        elif self._mode == 'images':
            self._render_current_image()
