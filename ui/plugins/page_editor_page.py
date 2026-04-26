from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QProgressBar,
    QFileDialog, QComboBox, QCheckBox, QButtonGroup,
    QRadioButton, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QDesktopServices, QPixmap, QImage

from ..preview_widget import PreviewWidget
from ..drag_drop_mixin import DragDropMixin
from ..dialogs import Dialogs
from workers.page_editor_worker import PageEditorWorker
from core.page_editor import PageEditorOperation
from utils import get_config_manager, ExportPathMode


class CheckableThumbnailItem(QListWidgetItem):
    def __init__(self, page_num: int):
        super().__init__()
        self.page_num = page_num
        self.setData(Qt.ItemDataRole.UserRole, page_num)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(Qt.CheckState.Unchecked)


class PageEditorPage(DragDropMixin, QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file = None
        self._worker = None
        self._config = get_config_manager()
        self._selected_pages = set()
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

        title_label = QLabel('页面旋转与删除')
        title_label.setObjectName('pageTitle')
        main_layout.addWidget(title_label)

        desc_label = QLabel('选择 PDF 文件后，可在缩略图上勾选页面，或直接输入页码范围进行操作')
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

        rotate_group = QGroupBox('旋转设置')
        rotate_layout = QVBoxLayout()

        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel('旋转角度:'))
        self.angle_combo = QComboBox()
        self.angle_combo.addItems(['90°', '180°', '270°'])
        self.angle_combo.setCurrentIndex(0)
        angle_layout.addWidget(self.angle_combo)
        angle_layout.addStretch()
        rotate_layout.addLayout(angle_layout)

        direction_layout = QHBoxLayout()
        self.clockwise_btn = QRadioButton('顺时针')
        self.clockwise_btn.setChecked(True)
        direction_layout.addWidget(self.clockwise_btn)
        self.counterclockwise_btn = QRadioButton('逆时针')
        direction_layout.addWidget(self.counterclockwise_btn)
        direction_layout.addStretch()
        rotate_layout.addLayout(direction_layout)

        self.rotate_all_pages = QCheckBox('旋转全部页面')
        self.rotate_all_pages.setChecked(True)
        rotate_layout.addWidget(self.rotate_all_pages)

        self.rotate_range_edit = QLineEdit()
        self.rotate_range_edit.setPlaceholderText('例如: 1-3, 5, 7-9 (留空表示全部)')
        self.rotate_range_edit.setEnabled(False)
        rotate_layout.addWidget(QLabel('或指定页码:'))
        rotate_layout.addWidget(self.rotate_range_edit)

        self.rotate_all_pages.toggled.connect(
            lambda checked: self.rotate_range_edit.setEnabled(not checked)
        )

        rotate_group.setLayout(rotate_layout)
        left_panel.addWidget(rotate_group)

        delete_group = QGroupBox('删除页面')
        delete_layout = QVBoxLayout()

        self.delete_range_edit = QLineEdit()
        self.delete_range_edit.setPlaceholderText('例如: 1-3, 5, 7-9')
        delete_layout.addWidget(QLabel('删除页码:'))
        delete_layout.addWidget(self.delete_range_edit)

        delete_hint = QLabel('提示: 勾选缩略图也会自动填充页码')
        delete_hint.setObjectName('hintLabel')
        delete_layout.addWidget(delete_hint)

        delete_group.setLayout(delete_layout)
        left_panel.addWidget(delete_group)

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

        btn_layout = QHBoxLayout()
        self.rotate_btn = QPushButton('旋转页面')
        self.rotate_btn.setObjectName('primaryBtn')
        self.rotate_btn.clicked.connect(self._start_rotate)
        self.rotate_btn.setEnabled(False)
        btn_layout.addWidget(self.rotate_btn)

        self.delete_btn = QPushButton('删除页面')
        self.delete_btn.setObjectName('dangerBtn')
        self.delete_btn.clicked.connect(self._start_delete)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)

        left_panel.addLayout(btn_layout)

        content_layout.addLayout(left_panel, 1)

        self.preview = PreviewWidget()
        self.preview.setMinimumWidth(500)
        content_layout.addWidget(self.preview)

        main_layout.addLayout(content_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.set_drag_target_callback(self._on_files_dropped)

    def _truncate_path(self, path: Path, max_len: int = 30) -> str:
        path_str = str(path)
        if len(path_str) <= max_len:
            return path_str
        return '...' + path_str[-(max_len - 3):]

    def _show_export_settings(self):
        current_path = str(self._config.default_export_path)
        new_dir = QFileDialog.getExistingDirectory(
            self, '选择默认导出路径', current_path
        )
        if new_dir:
            new_path_obj = Path(new_dir)
            self._config.default_export_path = new_path_obj
            self.default_path_label.setText(self._truncate_path(new_path_obj))
            Dialogs.show_success(self, '设置成功', f'默认导出路径已设置为:\n{new_path_obj}')

    def _get_output_dir(self) -> tuple[Path, bool]:
        func_mode = self._config.get_function_export_mode('page_editor')
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
        self.rotate_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.status_label.setText(f'已加载: {path.name} ({path.stat().st_size // 1024} KB)')

    def _on_files_dropped(self, file_paths: list):
        if file_paths:
            self._load_file(Path(file_paths[0]))

    def _validate_page_spec(self, page_spec: str, total_pages: int) -> tuple[bool, str]:
        if not page_spec or not page_spec.strip():
            return True, ''

        editor = PageEditorOperation(self._current_file)
        try:
            indices = editor._parse_page_spec(page_spec, total_pages)
            return True, ''
        except ValueError as e:
            return False, str(e)

    def _start_rotate(self):
        if not self._current_file:
            return

        output_dir, proceed = self._get_output_dir()
        if not proceed:
            return

        angle_str = self.angle_combo.currentText().replace('°', '')
        angle = int(angle_str)
        clockwise = self.clockwise_btn.isChecked()

        if self.rotate_all_pages.isChecked():
            page_spec = None
        else:
            page_spec = self.rotate_range_edit.text().strip()
            if page_spec:
                editor = PageEditorOperation(self._current_file)
                total = editor.get_page_count()
                valid, err = self._validate_page_spec(page_spec, total)
                if not valid:
                    Dialogs.show_error(self, '页码超出范围', err)
                    return
            else:
                page_spec = None

        self._worker = PageEditorWorker(
            self._current_file,
            output_dir,
            'rotate',
            angle,
            page_spec,
            clockwise
        )

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.rotate_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.status_label.setText('正在旋转页面...')

        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _start_delete(self):
        if not self._current_file:
            return

        output_dir, proceed = self._get_output_dir()
        if not proceed:
            return

        page_spec = self.delete_range_edit.text().strip()
        if not page_spec:
            Dialogs.show_error(self, '错误', '请输入要删除的页码')
            return

        editor = PageEditorOperation(self._current_file)
        total = editor.get_page_count()
        valid, err = self._validate_page_spec(page_spec, total)
        if not valid:
            Dialogs.show_error(self, '页码超出范围', err)
            return

        if not Dialogs.show_confirmation(
            self, '确认删除',
            f'确定要删除页码 {page_spec} 吗？\n删除后无法恢复。'
        ):
            return

        self._worker = PageEditorWorker(
            self._current_file,
            output_dir,
            'delete',
            None,
            page_spec,
            True
        )

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.rotate_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.status_label.setText('正在删除页面...')

        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, success: bool, result):
        self.progress_bar.setVisible(False)
        self.rotate_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        if success:
            output_path = result.output_paths[0]
            self.status_label.setText(f'操作完成: {output_path.name}')

            open_folder_btn = QPushButton('打开所在文件夹')
            open_folder_btn.clicked.connect(
                lambda: QDesktopServices.openUrl(
                    __import__('PySide6.QtCore', fromlist=['QUrl']).QUrl.fromLocalFile(str(output_path.parent))
                )
            )

            Dialogs.show_success(
                self, '完成',
                f'操作完成！\n{output_path.name}\n大小: {output_path.stat().st_size // 1024} KB'
            )
        else:
            Dialogs.show_error(self, '错误', str(result.error_message) if hasattr(result, 'error_message') else str(result))
            self.status_label.setText('操作失败')

    def refresh_export_settings(self):
        self.default_path_label.setText(self._truncate_path(self._config.default_export_path))

    def reset(self):
        self._current_file = None
        self._selected_pages.clear()
        self.file_path_edit.clear()
        self.rotate_range_edit.clear()
        self.delete_range_edit.clear()
        self.angle_combo.setCurrentIndex(0)
        self.clockwise_btn.setChecked(True)
        self.rotate_all_pages.setChecked(True)
        self.rotate_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.status_label.clear()
        self.progress_bar.setVisible(False)

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
