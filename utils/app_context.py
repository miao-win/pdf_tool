from utils.config_manager import ConfigManager
from utils.theme_manager import ThemeManager
from utils.pdf_cache import PDFDocumentCache
from utils.log_helper import get_logger

logger = get_logger(__name__)


class AppContext:
    def __init__(self):
        self._theme_manager: ThemeManager = None
        self._config_manager: ConfigManager = None
        self._pdf_cache: PDFDocumentCache = None

    @property
    def theme_manager(self) -> ThemeManager:
        if self._theme_manager is None:
            self._theme_manager = ThemeManager()
        return self._theme_manager

    @property
    def config_manager(self) -> ConfigManager:
        if self._config_manager is None:
            self._config_manager = ConfigManager()
        return self._config_manager

    @property
    def pdf_cache(self) -> PDFDocumentCache:
        if self._pdf_cache is None:
            self._pdf_cache = PDFDocumentCache()
        return self._pdf_cache


_app_context: AppContext = None


def get_app_context() -> AppContext:
    global _app_context
    if _app_context is None:
        _app_context = AppContext()
    return _app_context


def init_app_context() -> AppContext:
    global _app_context
    _app_context = AppContext()
    return _app_context
