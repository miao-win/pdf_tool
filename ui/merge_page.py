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
from .drag_drop_mixin import DragDropMixin
from .dialogs import Dialogs
from workers.merge_worker import MergeWorker
from utils import get_config_manager, ExportPathMode


class MergePage(DragDropMixin, QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._merge_items: List[MergeItem] = []
        self._worker = None
        self._config = get_config_manager()
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

        export_group = QGroupBox('导出位置')
        export_layout = QVBoxLayout()

        default_path_layout = QHBoxLayout()
        default_path_layout.addWidget(QLabel('默认路径:'))
        self.default_path_label = QLabel(self._truncate_path(self._config.default_export_path))
        self.default_path_label.setObjectName('pathLabel')
        default_path_layout.addWidget(self.default_path_label, 1)

        settings_btn = QPushButton('设置...')
        settings_btn.clicked.connect(self._show_export_settings)
        default_path_layout.addWidget(settings_btn)
        export_layout.addLayout(default_path_layout)

        export_group.setLayout(export_layout)
        left_panel.addWidget(export_group)

        self.start_btn = QPushButton('开始合并')
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self._start_merge)
        self.start_btn.setEnabled(False)
        left_panel.addWidget(self.start_btn)

        content_layout.addLayout(left_panel, 1)

        info_label = QLabel(
            '提示: 拖拽文件到此处导入\n'
            '支持多文件导入\n'
            '拖拽列表中的项目可调整顺序'
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setObjectName('infoLabel')
        content_layout.addWidget(info_label, 1)

        main_layout.addLayout(content_layout)

        self.progress_bar = QLabel()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.set_drag_target_callback(self._on_files_dropped)

    def _truncate_path(self, path: Path, max_len: int = 30) -> str:
        path_str = str(path)
        if len(path_str) <= max_len:
            return path_str
        return '...' + path_str[-(max_len - 3):]

    def _show_export_settings(self):
        from PySide6.QtWidgets import QInputDialog
        current_path = str(self._config.default_export_path)
        new_path, ok = QInputDialog.getText(
            self, '设置默认导出路径',
            '请输入默认导出路径:',
            QLineEdit.EchoMode.Normal,
            current_path
        )
        if ok and new_path:
            new_path_obj = Path(new_path)
            if not new_path_obj.parent.exists():
                Dialogs.show_error(self, '错误', '路径无效或上级目录不存在')
                return
            self._config.default_export_path = new_path_obj
            self.default_path_label.setText(self._truncate_path(new_path_obj))
            Dialogs.show_success(self, '设置成功', f'默认导出路径已设置为:\n{new_path_obj}')

    def _get_output_dir(self) -> tuple[Path, bool]:
        func_mode = self._config.get_function_export_mode('merge')
        if func_mode == ExportPathMode.ASK_USER:
            path, chosen = QFileDialog.getSaveFileName(
                self, '选择导出位置', '', 'PDF Files (*.pdf)'
            )
            if not chosen:
                return None, False
            output_path = Path(path)
            return output_path.parent, True
        else:
            if not self._config.is_valid_export_path(self._config.default_export_path):
                Dialogs.show_error(
                    self, '路径无效',
                    f'默认导出路径无效:\n{self._config.default_export_path}\n\n请重新设置有效的导出路径。'
                )
                return None, False
            success, output_dir = self._config.ensure_export_path_exists()
            if not success:
                Dialogs.show_error(self, '错误', f'无法创建导出目录:\n{output_dir}')
                return None, False
            return output_dir, True

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

        output_dir, proceed = self._get_output_dir()
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

    def refresh_export_settings(self):
        self.default_path_label.setText(self._truncate_path(self._config.default_export_path))

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
