from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QGroupBox,
    QProgressBar, QTextEdit, QFileDialog, QRadioButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices

from .preview_widget import PreviewWidget
from .drag_drop_mixin import DragDropMixin
from .dialogs import Dialogs
from workers.split_worker import SplitWorker
from utils import get_config_manager, ExportPathMode


class SplitPage(DragDropMixin, QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file = None
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

        mode_group = QGroupBox('拆分模式')
        mode_layout = QVBoxLayout()

        self.range_mode = QRadioButton('按页码范围拆分')
        self.range_mode.setChecked(True)
        mode_layout.addWidget(self.range_mode)

        self.fixed_mode = QRadioButton('按固定页数拆分')
        mode_layout.addWidget(self.fixed_mode)

        # 移除 QButtonGroup，使用默认的单选按钮行为
        # self.mode_button_group = QButtonGroup()
        # self.mode_button_group.addButton(self.range_mode)
        # self.mode_button_group.addButton(self.fixed_mode)
        # self.mode_button_group.setExclusive(True)

        mode_group.setLayout(mode_layout)
        left_panel.addWidget(mode_group)

        spec_group = QGroupBox('拆分参数')
        spec_layout = QVBoxLayout()

        self.range_edit = QLineEdit()
        self.range_edit.setPlaceholderText('例如: 1-3, 5, 7-9')
        spec_layout.addWidget(QLabel('页码范围:'))
        spec_layout.addWidget(self.range_edit)

        self.pages_per_file_edit = QLineEdit()
        self.pages_per_file_edit.setPlaceholderText('每 N 页一个文件')
        self.pages_per_file_edit.setEnabled(False)
        spec_layout.addWidget(QLabel('每 N 页:'))
        spec_layout.addWidget(self.pages_per_file_edit)

        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText('留空则自动生成')
        spec_layout.addWidget(QLabel('输出文件名:'))
        spec_layout.addWidget(self.output_name_edit)

        self.range_mode.toggled.connect(
            lambda checked: self.range_edit.setEnabled(checked)
        )
        self.fixed_mode.toggled.connect(
            lambda checked: self.pages_per_file_edit.setEnabled(checked)
        )

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

        self.start_btn = QPushButton('开始拆分')
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self._start_split)
        self.start_btn.setEnabled(False)
        left_panel.addWidget(self.start_btn)

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
        func_mode = self._config.get_function_export_mode('split')
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
        self.preview.load_pdf(path)
        self.start_btn.setEnabled(True)
        self.status_label.setText(f'已加载: {path.name} ({path.stat().st_size // 1024} KB)')

    def _on_files_dropped(self, file_paths: list):
        if file_paths:
            self._load_file(Path(file_paths[0]))

    def _start_split(self):
        if not self._current_file:
            return

        output_dir, proceed = self._get_output_dir()
        if not proceed:
            return

        if self.range_mode.isChecked():
            page_spec = self.range_edit.text().strip()
            if not page_spec:
                Dialogs.show_error(self, '错误', '请输入页码范围')
                return
            split_mode = 'range'
            pages_per_file = None
        else:
            page_spec = None
            split_mode = 'fixed'
            try:
                pages_per_file = int(self.pages_per_file_edit.text().strip())
                if pages_per_file <= 0:
                    raise ValueError()
            except ValueError:
                Dialogs.show_error(self, '错误', '请输入有效的页数')
                return

        self._worker = SplitWorker(
            self._current_file,
            output_dir,
            split_mode,
            page_spec,
            pages_per_file,
            self.output_name_edit.text().strip() or None
        )

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.start_btn.setEnabled(False)
        self.status_label.setText('正在处理...')

        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, success: bool, result):
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)

        if success:
            output_paths = result.output_paths
            self.status_label.setText(f'拆分完成! 生成 {len(output_paths)} 个文件')

            open_folder_btn = QPushButton(f'打开所在文件夹')
            open_folder_btn.clicked.connect(
                lambda: QDesktopServices.openUrl(
                    __import__('PySide6.QtCore', fromlist=['QUrl']).QUrl.fromLocalFile(str(output_paths[0].parent))
                )
            )
            self.status_label.setText(f'拆分完成! 生成 {len(output_paths)} 个文件')

            Dialogs.show_success(
                self, '完成',
                f'成功生成 {len(output_paths)} 个文件\n{output_paths[0].parent}'
            )
        else:
            Dialogs.show_error(self, '错误', str(result))
            self.status_label.setText('处理失败')

    def refresh_export_settings(self):
        self.default_path_label.setText(self._truncate_path(self._config.default_export_path))

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
        self.preview.close_pdf()
