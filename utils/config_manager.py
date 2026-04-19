from pathlib import Path
from PySide6.QtCore import QSettings


class ExportPathMode:
    USE_DEFAULT = 'default'
    ASK_USER = 'ask'


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._settings = QSettings('PDFTool', 'PDFTool')
        self._setup_defaults()

    def _setup_defaults(self):
        if not self._settings.contains('export_path_mode'):
            self._settings.setValue('export_path_mode', ExportPathMode.USE_DEFAULT)

        if not self._settings.contains('default_export_path'):
            default_path = Path.home() / 'Documents' / 'PDFTool_Output'
            self._settings.setValue('default_export_path', str(default_path))

        if not self._settings.contains('split_export_mode'):
            self._settings.setValue('split_export_mode', ExportPathMode.USE_DEFAULT)

        if not self._settings.contains('merge_export_mode'):
            self._settings.setValue('merge_export_mode', ExportPathMode.USE_DEFAULT)

        if not self._settings.contains('compress_export_mode'):
            self._settings.setValue('compress_export_mode', ExportPathMode.USE_DEFAULT)

    @property
    def export_path_mode(self) -> str:
        return self._settings.value('export_path_mode', ExportPathMode.USE_DEFAULT)

    @export_path_mode.setter
    def export_path_mode(self, mode: str):
        self._settings.setValue('export_path_mode', mode)

    @property
    def default_export_path(self) -> Path:
        path_str = self._settings.value('default_export_path', '')
        if path_str:
            return Path(path_str)
        return Path.home() / 'Documents' / 'PDFTool_Output'

    @default_export_path.setter
    def default_export_path(self, path: Path):
        self._settings.setValue('default_export_path', str(path))

    def get_function_export_mode(self, func_name: str) -> str:
        key = f'{func_name}_export_mode'
        return self._settings.value(key, ExportPathMode.USE_DEFAULT)

    def set_function_export_mode(self, func_name: str, mode: str):
        key = f'{func_name}_export_mode'
        self._settings.setValue(key, mode)

    def is_valid_export_path(self, path: Path) -> bool:
        if path is None:
            return False
        try:
            parent = path.parent
            if not parent.exists():
                return False
            return parent.is_dir() and parent.exists()
        except (OSError, ValueError):
            return False

    def ensure_export_path_exists(self, path: Path = None) -> tuple[bool, Path]:
        target = path if path else self.default_export_path
        try:
            target.mkdir(parents=True, exist_ok=True)
            return True, target
        except (OSError, PermissionError):
            return False, target

    @staticmethod
    def get_default_output_dir(input_path: Path) -> Path:
        return input_path.parent / 'output'


_config_manager = None


def get_config_manager() -> ConfigManager:
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
