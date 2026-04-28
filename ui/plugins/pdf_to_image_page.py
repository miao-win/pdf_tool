from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QProgressBar,
    QFileDialog, QComboBox, QCheckBox, QButtonGroup,
    QRadioButton
)
from PySide6.QtCore import Qt, Signal

from ..preview_widget import PreviewWidget
from ..drag_drop_mixin import DragDropMixin
from ..base_page import ExportPathMixin, BackButtonMixin
from ..dialogs import Dialogs
from workers.pdf_to_image_worker import PDFToImageWorker
from utils import get_config_manager
from utils.constants import PREVIEW_MIN_WIDTH
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PDFToImagePage(ExportPathMixin, BackButtonMixin, DragDropMixin, QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file = None
        self._worker = None
        self._config = get_config_manager()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.addLayout(self._create_top_bar())

        title_label = QLabel('PDF 转图片')
        title_label.setObjectName('pageTitle')
        main_layout.addWidget(title_label)

        desc_label = QLabel('将 PDF 页面的内容转换为图片，支持 PNG、JPG 等格式')
        desc_label.setObjectName('pageDesc')
        main_layout.addWidget(desc_label)

        content_layout = QHBoxLayout()

        left_panel = QVBoxLayout()

        file_group = QGroupBox('选择文件')
        file_layout = QVBoxLayout()

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText('拖拽 PDF 文件到此处或点击选择...')
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)

        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        file_group.setLayout(file_layout)
        left_panel.addWidget(file_group)

        format_group = QGroupBox('输出格式')
        format_layout = QVBoxLayout()

        format_type_layout = QHBoxLayout()
        format_type_layout.addWidget(QLabel('图片格式:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['PNG (透明背景)', 'JPG (白底)'])
        self.format_combo.setCurrentIndex(0)
        format_type_layout.addWidget(self.format_combo)
        format_type_layout.addStretch()
        format_layout.addLayout(format_type_layout)

        self.jpg_quality_widget = QWidget()
        jpg_quality_layout = QHBoxLayout(self.jpg_quality_widget)
        jpg_quality_layout.addWidget(QLabel('JPG 质量:'))
        self.quality_slider = QComboBox()
        self.quality_slider.addItems(['1', '25', '50', '75', '100'])
        self.quality_slider.setCurrentIndex(2)
        jpg_quality_layout.addWidget(self.quality_slider)
        jpg_quality_layout.addStretch()
        self.jpg_quality_widget.setVisible(False)
        format_layout.addWidget(self.jpg_quality_widget)

        self.format_combo.currentIndexChanged.connect(self._on_format_changed)

        format_group.setLayout(format_layout)
        left_panel.addWidget(format_group)

        dpi_group = QGroupBox('DPI 设置')
        dpi_layout = QVBoxLayout()

        dpi_select_layout = QHBoxLayout()
        dpi_select_layout.addWidget(QLabel('分辨率:'))
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItems(['72 (屏幕)', '150 (标准)', '300 (高清)', '600 (打印)'])
        self.dpi_combo.setCurrentIndex(1)
        dpi_select_layout.addWidget(self.dpi_combo)
        dpi_select_layout.addStretch()
        dpi_layout.addLayout(dpi_select_layout)

        dpi_hint = QLabel('72DPI: 屏幕显示 | 150DPI: 一般办公 | 300DPI: 高清打印 | 600DPI: 专业出版')
        dpi_hint.setObjectName('hintLabel')
        dpi_layout.addWidget(dpi_hint)

        dpi_group.setLayout(dpi_layout)
        left_panel.addWidget(dpi_group)

        page_group = QGroupBox('页面范围（可选）')
        page_layout = QVBoxLayout()

        self.page_all_radio = QRadioButton('全部页面')
        self.page_all_radio.setChecked(True)
        page_layout.addWidget(self.page_all_radio)

        self.page_range_radio = QRadioButton('指定页面范围')
        page_layout.addWidget(self.page_range_radio)

        self.page_range_edit = QLineEdit()
        self.page_range_edit.setPlaceholderText('例如: 1-3, 5, 7-9')
        self.page_range_edit.setEnabled(False)
        page_layout.addWidget(self.page_range_edit)

        self.page_all_radio.toggled.connect(
            lambda checked: self.page_range_edit.setEnabled(not checked and self.page_range_radio.isChecked())
        )
        self.page_range_radio.toggled.connect(
            lambda checked: self.page_range_edit.setEnabled(checked)
        )

        page_group.setLayout(page_layout)
        left_panel.addWidget(page_group)

        export_group, _ = self._create_export_group()
        left_panel.addWidget(export_group)

        self.start_btn = QPushButton('开始转换')
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self._start_convert)
        self.start_btn.setEnabled(False)
        left_panel.addWidget(self.start_btn)

        content_layout.addLayout(left_panel, 1)

        self.preview = PreviewWidget()
        self.preview.setMinimumWidth(PREVIEW_MIN_WIDTH)
        content_layout.addWidget(self.preview, 2)

        main_layout.addLayout(content_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.set_drag_target_callback(self._on_files_dropped)

    def _on_format_changed(self, index: int):
        self.jpg_quality_widget.setVisible(index == 1)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择 PDF 文件', '', 'PDF Files (*.pdf)'
        )
        if path:
            self._load_file(Path(path))

    def _load_file(self, path: Path):
        if path.suffix.lower() != '.pdf':
            Dialogs.show_error(self, '错误', '请选择 PDF 文件')
            return

        self._current_file = path
        self.file_path_edit.setText(str(path))
        self.start_btn.setEnabled(True)
        self.status_label.setText(f'已加载: {path.name} ({path.stat().st_size // 1024} KB)')
        self.preview.load_pdf(path)

    def _on_files_dropped(self, file_paths: list):
        if file_paths:
            self._load_file(Path(file_paths[0]))

    def _start_convert(self):
        if not self._current_file:
            return

        output_dir, proceed = self._get_output_dir('pdf_to_image', is_folder_mode=True)
        if not proceed:
            return

        format_index = self.format_combo.currentIndex()
        fmt = 'png' if format_index == 0 else 'jpg'

        dpi_map = {0: 72, 1: 150, 2: 300, 3: 600}
        dpi = dpi_map[self.dpi_combo.currentIndex()]

        if self.page_range_radio.isChecked():
            page_spec = self.page_range_edit.text().strip()
        else:
            page_spec = None

        self._worker = PDFToImageWorker(
            self._current_file,
            output_dir,
            fmt,
            dpi,
            page_spec
        )

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.status_label.setText('正在转换...')

        self._worker.status.connect(self._on_status)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_status(self, status: str):
        self.status_label.setText(status)

    def _on_progress(self, value: int):
        self.progress_bar.setValue(value)

    def _on_finished(self, success: bool, result):
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)

        if success:
            output_paths = result.output_paths
            output_folder = output_paths[0].parent if output_paths else self._config.default_export_path
            self.status_label.setText(f'转换完成! 共生成 {len(output_paths)} 张图片')

            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(
                __import__('PySide6.QtCore', fromlist=['QUrl']).QUrl.fromLocalFile(str(output_folder))
            )

            Dialogs.show_success(
                self, '完成',
                f'转换完成！\n共生成 {len(output_paths)} 张图片\n'
                f'保存在: {output_folder}'
            )
        else:
            Dialogs.show_error(self, '错误', str(result.error_message) if hasattr(result, 'error_message') else str(result))
            self.status_label.setText('转换失败')

    def reset(self):
        self._current_file = None
        self.file_path_edit.clear()
        self.format_combo.setCurrentIndex(0)
        self.dpi_combo.setCurrentIndex(1)
        self.page_all_radio.setChecked(True)
        self.page_range_edit.clear()
        self.start_btn.setEnabled(False)
        self.status_label.clear()
        self.progress_bar.setVisible(False)
        self.preview.clear()

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
