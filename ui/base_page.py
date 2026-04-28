from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QFileDialog, QWidget
from PySide6.QtCore import Signal

from utils.config_manager import ConfigManager, ExportPathMode
from utils.constants import PATH_TRUNCATE_MAX_LEN
from utils.log_helper import get_logger
from .dialogs import Dialogs

logger = get_logger(__name__)


class ExportPathMixin:
    _config: ConfigManager
    default_path_label: QWidget

    def _truncate_path(self, path: Path, max_len: int = PATH_TRUNCATE_MAX_LEN) -> str:
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

    def _get_output_dir(self, func_name: str, is_folder_mode: bool = False) -> tuple[Optional[Path], bool]:
        func_mode = self._config.get_function_export_mode(func_name)
        if func_mode == ExportPathMode.ASK_USER:
            if is_folder_mode:
                path = QFileDialog.getExistingDirectory(self, '选择导出文件夹')
                if not path:
                    return None, False
                return Path(path), True
            else:
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

    def refresh_export_settings(self):
        self.default_path_label.setText(self._truncate_path(self._config.default_export_path))


class BackButtonMixin:
    back_clicked = Signal()

    def _create_back_button(self) -> 'QPushButton':
        from PySide6.QtWidgets import QPushButton
        back_btn = QPushButton('← 返回')
        back_btn.setObjectName('backBtn')
        back_btn.clicked.connect(self.back_clicked.emit)
        return back_btn

    def _create_top_bar(self) -> 'QHBoxLayout':
        from PySide6.QtWidgets import QHBoxLayout
        top_bar = QHBoxLayout()
        top_bar.addWidget(self._create_back_button())
        top_bar.addStretch()
        return top_bar

    def _create_export_group(self) -> 'tuple[QGroupBox, QLabel]':
        from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
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
        return export_group, self.default_path_label
