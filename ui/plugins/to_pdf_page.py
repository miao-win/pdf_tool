from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QProgressBar,
    QFileDialog, QComboBox, QCheckBox, QListWidget,
    QListWidgetItem, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from ..drag_drop_mixin import DragDropMixin
from ..dialogs import Dialogs
from workers.to_pdf_worker import ToPDFWorker
from core.to_pdf import ToPDFConverter
from utils import get_config_manager, ExportPathMode


class ToPDFPage(DragDropMixin, QWidget):
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

        top_bar = QHBoxLayout()
        back_btn = QPushButton('← 返回')
        back_btn.setObjectName('backBtn')
        back_btn.clicked.connect(self.back_clicked.emit)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

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

        self.start_btn = QPushButton('开始转换')
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self._start_convert)
        self.start_btn.setEnabled(False)
        left_panel.addWidget(self.start_btn)

        content_layout.addLayout(left_panel, 1)

        self.info_label = QLabel(
            '🖼️ 拖拽图片文件到此处\n\n'
            '支持格式: PNG, JPG, BMP, TIFF, WebP\n'
            '多图合并时，拖拽调整列表顺序'
        )
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setObjectName('infoLabel')
        content_layout.addWidget(self.info_label, 1)

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

    def _update_ui_for_source_type(self):
        if self._source_type == 'images':
            self.desc_label.setText('选择图片文件，将它们合成为一个 PDF')
            self.info_label.setText(
                '🖼️ 拖拽图片文件到此处\n\n'
                '支持格式: PNG, JPG, BMP, TIFF, WebP\n'
                '多图合并时，拖拽调整列表顺序'
            )
            self.dpi_widget.setVisible(True)
        elif self._source_type == 'word':
            self.desc_label.setText('将 Word 文档转换为 PDF')
            self.info_label.setText(
                '📄 Word 文件\n\n'
                '支持 .docx 和 .doc 格式\n'
                '需要 Microsoft Office / WPS / LibreOffice'
            )
            self.dpi_widget.setVisible(False)
        elif self._source_type == 'ppt':
            self.desc_label.setText('将 PowerPoint 演示文稿转换为 PDF')
            self.info_label.setText(
                '📊 PPT 文件\n\n'
                '支持 .pptx 和 .ppt 格式\n'
                '需要 Microsoft Office / WPS / LibreOffice'
            )
            self.dpi_widget.setVisible(False)

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
        func_mode = self._config.get_function_export_mode('to_pdf')
        if func_mode == ExportPathMode.ASK_USER:
            path = QFileDialog.getExistingDirectory(
                self, '选择导出文件夹'
            )
            if not path:
                return None, False
            return Path(path), True
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

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            if row < len(self._current_files):
                self._current_files.pop(row)
        self._update_start_button()

    def _clear_list(self):
        self.file_list.clear()
        self._current_files.clear()
        self._update_start_button()

    def _update_start_button(self):
        self.start_btn.setEnabled(len(self._current_files) > 0)

    def _on_files_dropped(self, file_paths: list):
        detected_type = ToPDFConverter.detect_format([Path(p) for p in file_paths])

        if detected_type == 'unknown':
            Dialogs.show_error(self, '错误', '不支持的文件格式')
            return

        self._source_type = detected_type if detected_type != 'mixed_image_word' else 'images'
        self._clear_list()
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
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                files.append(path)
        self._current_files = files

    def _start_convert(self):
        if not self._current_files:
            return

        output_dir, proceed = self._get_output_dir()
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

    def refresh_export_settings(self):
        self.default_path_label.setText(self._truncate_path(self._config.default_export_path))

    def cleanup(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
