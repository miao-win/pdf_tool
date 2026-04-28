from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QGroupBox, QLineEdit, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices

from core.merge import MergeItem
from .preview_widget import PreviewWidget
from .drag_drop_mixin import DragDropMixin
from .base_page import ExportPathMixin, BackButtonMixin
from .dialogs import Dialogs
from workers.merge_worker import MergeWorker
from utils import get_config_manager
from utils.constants import PREVIEW_MIN_WIDTH
from utils.log_helper import get_logger

logger = get_logger(__name__)


class MergePage(ExportPathMixin, BackButtonMixin, DragDropMixin, QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._merge_items: List[MergeItem] = []
        self._worker = None
        self._config = get_config_manager()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.addLayout(self._create_top_bar())

        content_layout = QHBoxLayout()

        left_panel = QVBoxLayout()

        file_group = QGroupBox('PDF 文件列表（拖拽调整顺序）')
        file_layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
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
        left_panel.addWidget(file_group)

        spec_group = QGroupBox('页码范围（可选）')
        spec_layout = QVBoxLayout()
        spec_layout.addWidget(QLabel('格式: 1-3, 5, 7-9 或留空（全部页）'))
        self.page_spec_edit = QLineEdit()
        self.page_spec_edit.setPlaceholderText('例如: 1-3, 5, 7-9')
        spec_layout.addWidget(self.page_spec_edit)

        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText('留空则自动生成')
        spec_layout.addWidget(QLabel('输出文件名:'))
        spec_layout.addWidget(self.output_name_edit)

        spec_group.setLayout(spec_layout)
        left_panel.addWidget(spec_group)

        export_group, _ = self._create_export_group()
        left_panel.addWidget(export_group)

        self.start_btn = QPushButton('开始合并')
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self._start_merge)
        self.start_btn.setEnabled(False)
        left_panel.addWidget(self.start_btn)

        content_layout.addLayout(left_panel, 1)

        self.preview = PreviewWidget()
        self.preview.setMinimumWidth(PREVIEW_MIN_WIDTH)
        content_layout.addWidget(self.preview, 2)

        main_layout.addLayout(content_layout)

        self.progress_bar = QLabel()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.set_drag_target_callback(self._on_files_dropped)

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, '选择 PDF 文件', '', 'PDF Files (*.pdf)'
        )
        if paths:
            for path in paths:
                self._add_file(Path(path))

    def _add_file(self, path: Path):
        if path.suffix.lower() != '.pdf':
            return

        item = QListWidgetItem(path.name)
        item.setData(Qt.ItemDataRole.UserRole, path)
        self.file_list.addItem(item)

        merge_item = MergeItem(path)
        self._merge_items.append(merge_item)
        self._update_start_button()
        self.preview.load_pdf(path)

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            if row < len(self._merge_items):
                self._merge_items.pop(row)
        self._update_start_button()

    def _clear_list(self):
        self.file_list.clear()
        self._merge_items.clear()
        self._update_start_button()

    def _update_start_button(self):
        self.start_btn.setEnabled(len(self._merge_items) > 0)

    def _on_files_dropped(self, file_paths: list):
        for path in file_paths:
            p = Path(path)
            if p.suffix.lower() == '.pdf':
                self._add_file(p)

    def _reorder_items(self):
        paths = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                paths.append(path)

        self.file_list.clear()
        self._merge_items.clear()

        for path in paths:
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.file_list.addItem(item)
            self._merge_items.append(MergeItem(path))

    def _start_merge(self):
        if not self._merge_items:
            return

        output_dir, proceed = self._get_output_dir('merge')
        if not proceed:
            return

        self._reorder_items()

        page_spec = self.page_spec_edit.text().strip()

        if page_spec:
            for i, merge_item in enumerate(self._merge_items):
                merge_item.page_spec = page_spec

        self._worker = MergeWorker(
            output_dir,
            self._merge_items,
            self.output_name_edit.text().strip() or None
        )

        self.progress_bar.setVisible(True)
        self.progress_bar.setText('正在合并...')
        self.start_btn.setEnabled(False)

        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, success: bool, result):
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)

        if success:
            output_path = result.output_paths[0]
            Dialogs.show_success(
                self, '完成',
                f'合并完成！\n{output_path.name}\n大小: {output_path.stat().st_size // 1024} KB'
            )
            QDesktopServices.openUrl(
                __import__('PySide6.QtCore', fromlist=['QUrl']).QUrl.fromLocalFile(str(output_path.parent))
            )
        else:
            Dialogs.show_error(self, '错误', str(result))

    def reset(self):
        self._merge_items.clear()
        self.file_list.clear()
        self.page_spec_edit.clear()
        self.output_name_edit.clear()
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.preview.clear()

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
