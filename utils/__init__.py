from pathlib import Path


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return '0 B'
    units = ['B', 'KB', 'MB', 'GB']
    unit_idx = 0
    size = float(size_bytes)
    while size >= 1024 and unit_idx < len(units) - 1:
        size /= 1024
        unit_idx += 1
    return f'{size:.2f} {units[unit_idx]}'


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_unique_output_path(output_dir: Path, base_name: str, suffix: str = '.pdf') -> Path:
    counter = 1
    output_path = output_dir / f'{base_name}{suffix}'
    while output_path.exists():
        output_path = output_dir / f'{base_name}_{counter}{suffix}'
        counter += 1
    return output_path


def open_folder(path: Path) -> None:
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtCore import QUrl
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))


from .config_manager import ConfigManager, get_config_manager, ExportPathMode
from .theme_manager import ThemeManager, get_theme_manager, apply_theme_to_widget
from .pdf_cache import PDFDocumentCache, get_pdf_cache
from .page_registry import PageRegistry
from .app_context import AppContext, get_app_context, init_app_context
from .log_helper import get_logger, setup_logging
from .constants import *
