from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QProgressBar,
    QFileDialog, QComboBox, QCheckBox, QListWidget,
    QListWidgetItem, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from ..preview_widget import PreviewWidget
from ..drag_drop_mixin import DragDropMixin
from ..base_page import ExportPathMixin, BackButtonMixin
from ..dialogs import Dialogs
from workers.to_pdf_worker import ToPDFWorker
from core.to_pdf import ToPDFConverter
from utils import get_config_manager
from utils.constants import PREVIEW_MIN_WIDTH
from utils.log_helper import get_logger

logger = get_logger(__name__)


class ToPDFPage(ExportPathMixin, BackButtonMixin, DragDropMixin, QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_files: List[Path] = []
        self._worker = None
        self._config = get_config_manager()
        self._source_type = 'images'
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.addLayout(self._create_top_bar())

        title_label = QLabel('转换为 PDF')
        title_label.setObjectName('pageTitle')
        main_layout.addWidget(title_label)

        self.desc_label = QLabel('选择图片文件，将它们合成为一个 PDF')
        self.desc_label.setObjectName('pageDesc')
        main_layout.addWidget(self.desc_label)

        warning_label = QLabel(
            '⚠️ Word/PPT 转换需要系统安装 Microsoft Office、WPS 或 LibreOffice'
        )
        warning_label.setObjectName('warningLabel')
        warning_label.setVisible(False)
        main_layout.addWidget(warning_label)

        content_layout = QHBoxLayout()

        left_panel = QVBoxLayout()

        file_group = QGroupBox('选择文件')
        file_layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.file_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        file_layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('添加文件')
        add_btn.clicked.connect(self._add_files)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton('移除选中')
        remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(remove_btn)

        clear_btn = QPushButton('清空')
        clear_btn.clicked.connect(self._clear_list)
        btn_layout.addWidget(clear_btn)

        file_layout.addLayout(btn_layout)
        file_group.setLayout(file_layout)
        left_panel.addWidget(file_group, 1)

        settings_group = QGroupBox('转换设置')
        settings_layout = QVBoxLayout()

        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText('留空则自动生成')
        settings_layout.addWidget(QLabel('输出文件名:'))
        settings_layout.addWidget(self.output_name_edit)

        self.dpi_widget = QWidget()
        dpi_layout = QHBoxLayout(self.dpi_widget)
        dpi_layout.addWidget(QLabel('DPI:'))
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItems(['72', '150', '300'])
        self.dpi_combo.setCurrentIndex(1)
        dpi_layout.addWidget(self.dpi_combo)
        dpi_layout.addStretch()
        settings_layout.addWidget(self.dpi_widget)

        settings_group.setLayout(settings_layout)
        left_panel.addWidget(settings_group)

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

    def _update_ui_for_source_type(self):
        if self._source_type == 'images':
            self.desc_label.setText('选择图片文件，将它们合成为一个 PDF')
            self.dpi_widget.setVisible(True)
        elif self._source_type == 'word':
            self.desc_label.setText('将 Word 文档转换为 PDF')
            self.dpi_widget.setVisible(False)
        elif self._source_type == 'ppt':
            self.desc_label.setText('将 PowerPoint 演示文稿转换为 PDF')
            self.dpi_widget.setVisible(False)

    def _update_preview(self):
        if not self._current_files:
            self.preview.clear()
            if self._source_type == 'images':
                self.preview._placeholder.setText(
                    '🖼️ 拖拽图片文件到左侧区域\n\n'
                    '支持格式: PNG, JPG, BMP, TIFF, WebP\n'
                    '多图合并时，拖拽调整列表顺序'
                )
            elif self._source_type == 'word':
                self.preview._placeholder.setText(
                    '📄 Word 文件\n\n'
                    '支持 .docx 和 .doc 格式\n'
                    '需要 Microsoft Office / WPS / LibreOffice'
                )
            elif self._source_type == 'ppt':
                self.preview._placeholder.setText(
                    '📊 PPT 文件\n\n'
                    '支持 .pptx 和 .ppt 格式\n'
                    '需要 Microsoft Office / WPS / LibreOffice'
                )
            self.preview._placeholder.setVisible(True)
            return

        if self._source_type == 'images':
            self.preview.load_images(self._current_files)
        else:
            self.preview.clear()
            if self._source_type == 'word':
                self.preview._placeholder.setText(
                    f'📄 已选择 {len(self._current_files)} 个 Word 文件\n\n'
                    'Word 文件无法直接预览\n转换完成后可查看生成的 PDF'
                )
            elif self._source_type == 'ppt':
                self.preview._placeholder.setText(
                    f'📊 已选择 {len(self._current_files)} 个 PPT 文件\n\n'
                    'PPT 文件无法直接预览\n转换完成后可查看生成的 PDF'
                )
            self.preview._placeholder.setVisible(True)

    def _add_files(self):
        if self._source_type == 'images':
            filters = '图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp)'
        elif self._source_type == 'word':
            filters = 'Word 文档 (*.docx *.doc)'
        elif self._source_type == 'ppt':
            filters = 'PowerPoint 文件 (*.pptx *.ppt)'
        else:
            filters = '所有文件 (*.*)'

        paths, _ = QFileDialog.getOpenFileNames(
            self, '选择文件', '', filters
        )
        if paths:
            for path in paths:
                self._add_file(Path(path))

    def _add_file(self, path: Path):
        item = QListWidgetItem(path.name)
        item.setData(Qt.ItemDataRole.UserRole, path)
        self.file_list.addItem(item)
        self._current_files.append(path)
        self._update_start_button()
        self._update_preview()

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            if row < len(self._current_files):
                self._current_files.pop(row)
        self._update_start_button()
        self._update_preview()

    def _clear_list(self):
        self.file_list.clear()
        self._current_files.clear()
        self._update_start_button()
        self._update_preview()

    def _update_start_button(self):
        self.start_btn.setEnabled(len(self._current_files) > 0)

    def _on_files_dropped(self, file_paths: list):
        detected_type = ToPDFConverter.detect_format([Path(p) for p in file_paths])

        if detected_type == 'unknown':
            Dialogs.show_error(self, '错误', '不支持的文件格式')
            return

        effective_type = detected_type if detected_type != 'mixed_image_word' else 'images'

        if effective_type != self._source_type:
            self._clear_list()
            self._source_type = effective_type
            self._update_ui_for_source_type()

        for path in file_paths:
            p = Path(path)
            if self._source_type == 'images' and p.suffix.lower() in ToPDFConverter.IMAGE_EXTENSIONS:
                self._add_file(p)
            elif self._source_type == 'word' and p.suffix.lower() in ToPDFConverter.WORD_EXTENSIONS:
                self._add_file(p)
            elif self._source_type == 'ppt' and p.suffix.lower() in ToPDFConverter.PPT_EXTENSIONS:
                self._add_file(p)

    def _reorder_files(self):
        files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            path = item.getData(Qt.ItemDataRole.UserRole)
            if path:
                files.append(path)
        self._current_files = files

    def _start_convert(self):
        if not self._current_files:
            return

        output_dir, proceed = self._get_output_dir('to_pdf', is_folder_mode=True)
        if not proceed:
            return

        self._reorder_files()

        output_name = self.output_name_edit.text().strip() or None
        dpi = int(self.dpi_combo.currentText())

        self._worker = ToPDFWorker(
            self._current_files,
            output_dir,
            self._source_type,
            output_name,
            dpi
        )

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(10)
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
            output_path = result.output_paths[0]
            self.status_label.setText(f'转换完成: {output_path.name}')

            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(
                __import__('PySide6.QtCore', fromlist=['QUrl']).QUrl.fromLocalFile(str(output_path.parent))
            )

            Dialogs.show_success(
                self, '完成',
                f'转换完成！\n{output_path.name}\n'
                f'大小: {output_path.stat().st_size // 1024} KB'
            )
        else:
            Dialogs.show_error(self, '错误', str(result.error_message) if hasattr(result, 'error_message') else str(result))
            self.status_label.setText('转换失败')

    def reset(self):
        self._current_files.clear()
        self._source_type = 'images'
        self.file_list.clear()
        self.output_name_edit.clear()
        self.dpi_combo.setCurrentIndex(1)
        self.start_btn.setEnabled(False)
        self.status_label.clear()
        self.progress_bar.setVisible(False)
        self._update_ui_for_source_type()
        self.preview.clear()

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
