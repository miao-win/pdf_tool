from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QComboBox,
    QProgressBar, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices

from .preview_widget import PreviewWidget
from .drag_drop_mixin import DragDropMixin
from .base_page import ExportPathMixin, BackButtonMixin
from .dialogs import Dialogs
from workers.compress_worker import CompressWorker
from utils import format_file_size, get_config_manager
from utils.constants import PREVIEW_MIN_WIDTH
from utils.log_helper import get_logger

logger = get_logger(__name__)


class CompressPage(ExportPathMixin, BackButtonMixin, DragDropMixin, QWidget):
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

        level_group = QGroupBox('压缩级别')
        level_layout = QVBoxLayout()

        level_desc_layout = QHBoxLayout()
        level_desc_layout.addWidget(QLabel('低压缩'))
        level_desc_layout.addStretch()
        level_desc_layout.addWidget(QLabel('高压缩'))
        level_layout.addLayout(level_desc_layout)

        self.level_combo = QComboBox()
        self.level_combo.addItems(['低 (质量优先)', '中 (平衡)', '高 (体积最小)'])
        self.level_combo.setCurrentIndex(1)
        level_layout.addWidget(self.level_combo)

        est_label = QLabel(
            '预估压缩率: 低 10-20% | 中 30-50% | 高 50-70%'
        )
        est_label.setObjectName('estimateLabel')
        level_layout.addWidget(est_label)

        level_group.setLayout(level_layout)
        left_panel.addWidget(level_group)

        name_group = QGroupBox('输出设置')
        name_layout = QVBoxLayout()
        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText('留空则自动生成')
        name_layout.addWidget(QLabel('输出文件名:'))
        name_layout.addWidget(self.output_name_edit)
        name_group.setLayout(name_layout)
        left_panel.addWidget(name_group)

        export_group, _ = self._create_export_group()
        left_panel.addWidget(export_group)

        self.start_btn = QPushButton('开始压缩')
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self._start_compress)
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

        original_size = path.stat().st_size
        self.status_label.setText(
            f'已加载: {path.name}\n原始大小: {format_file_size(original_size)}'
        )
        self.start_btn.setEnabled(True)
        self.preview.load_pdf(path)

    def _on_files_dropped(self, file_paths: list):
        if file_paths:
            self._load_file(Path(file_paths[0]))

    def _start_compress(self):
        if not self._current_file:
            return

        output_dir, proceed = self._get_output_dir('compress')
        if not proceed:
            return

        level_map = {0: 'low', 1: 'medium', 2: 'high'}
        compression_level = level_map[self.level_combo.currentIndex()]

        self._worker = CompressWorker(
            self._current_file,
            output_dir,
            compression_level,
            self.output_name_edit.text().strip() or None
        )

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.start_btn.setEnabled(False)
        self.status_label.setText('正在压缩...')

        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, success: bool, result):
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)

        if success:
            original = result.original_size
            compressed = result.output_size
            ratio = result.compression_ratio

            msg = (
                f'压缩完成！\n\n'
                f'原始大小: {format_file_size(original)}\n'
                f'压缩后: {format_file_size(compressed)}\n'
                f'减少: {ratio:.1f}%'
            )
            Dialogs.show_success(self, '完成', msg)

            output_path = result.output_paths[0]
            QDesktopServices.openUrl(
                __import__('PySide6.QtCore', fromlist=['QUrl']).QUrl.fromLocalFile(str(output_path.parent))
            )

            self.status_label.setText(f'压缩完成! 减少 {ratio:.1f}%')
        else:
            Dialogs.show_error(self, '错误', str(result))
            self.status_label.setText('压缩失败')

    def reset(self):
        self._current_file = None
        self.file_path_edit.clear()
        self.output_name_edit.clear()
        self.level_combo.setCurrentIndex(1)
        self.start_btn.setEnabled(False)
        self.status_label.clear()
        self.progress_bar.setVisible(False)
        self.preview.clear()

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
