from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QGroupBox, QComboBox,
    QProgressBar, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices

from core.compress import PDFCompressor
from .drag_drop_mixin import DragDropMixin
from .dialogs import Dialogs
from workers.compress_worker import CompressWorker
from utils import format_file_size


class CompressPage(DragDropMixin, QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file = None
        self._worker = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        back_btn = QPushButton('← 返回')
        back_btn.setObjectName('backBtn')
        back_btn.clicked.connect(self.back_clicked.emit)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

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

        est_low = '10-20%'
        est_medium = '30-50%'
        est_high = '50-70%'

        est_label = QLabel(
            f'预估压缩率: 低 {est_low} | 中 {est_medium} | 高 {est_high}'
        )
        est_label.setObjectName('estimateLabel')
        level_layout.addWidget(est_label)

        level_group.setLayout(level_layout)
        left_panel.addWidget(level_group)

        self.start_btn = QPushButton('开始压缩')
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self._start_compress)
        self.start_btn.setEnabled(False)
        left_panel.addWidget(self.start_btn)

        content_layout.addLayout(left_panel, 1)

        info_panel = QVBoxLayout()
        info_panel.addWidget(QLabel('拖拽 PDF 文件到此处'))
        info_panel.addStretch()
        content_layout.addLayout(info_panel, 1)

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

    def _on_files_dropped(self, file_paths: list):
        if file_paths:
            self._load_file(Path(file_paths[0]))

    def _start_compress(self):
        if not self._current_file:
            return

        output_dir = self._current_file.parent / 'output'
        output_dir.mkdir(exist_ok=True)

        level_map = {0: 'low', 1: 'medium', 2: 'high'}
        compression_level = level_map[self.level_combo.currentIndex()]

        self._worker = CompressWorker(
            self._current_file,
            output_dir,
            compression_level
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

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
