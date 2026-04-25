"""
主题管理器
加载 QSS → 广播 themeChanged → 组件 update() 重绘
"""
from PySide6.QtCore import QObject, Signal, QSettings, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QColor

from ui.styles.minimal import MINIMAL_QSS
from ui.styles.ink import INK_QSS
from ui.styles.scifi import SCIFI_QSS


class ThemeManager(QObject):
    theme_changed = Signal(str)

    THEMES = {
        'minimal': {
            'name': '简约',
            'qss': MINIMAL_QSS,
            'bg': '#FAFAFA',
            'card': '#FFFFFF',
            'sidebar': '#F2F2F4',
            'text_primary': '#1F2328',
            'text_secondary': '#57606A',
            'accent': '#2E6BE6',
            'accent_secondary': '#3B82F6',
            'danger': '#DC2626',
            'success': '#22C55E',
            'font_main': '"Inter", "PingFang SC", "Microsoft YaHei", sans-serif',
            'font_mono': '"JetBrains Mono", monospace',
            'radius_card': 10,
            'radius_button': 6,
        },
        'ink': {
            'name': '水墨',
            'qss': INK_QSS,
            'bg': '#F4EEDF',
            'card': '#FBF6E9',
            'sidebar': '#EBE3CF',
            'text_primary': '#1C1B1A',
            'text_secondary': '#5C5650',
            'accent': '#8B2B2B',
            'accent_secondary': '#3E5E5A',
            'danger': '#8B2B2B',
            'success': '#3E5E5A',
            'font_main': '"LXGW WenKai", "Noto Serif SC", "PingFang SC", serif',
            'font_mono': '"Cormorant Garamond", serif',
            'radius_card': 4,
            'radius_button': 4,
        },
        'scifi': {
            'name': '科幻',
            'qss': SCIFI_QSS,
            'bg': '#0A0E14',
            'card': '#111826',
            'sidebar': '#0D131D',
            'text_primary': '#E2F3FF',
            'text_secondary': '#6D8299',
            'accent': '#00E5FF',
            'accent_secondary': '#FF2E9A',
            'danger': '#FF2E9A',
            'success': '#00E5FF',
            'font_main': '"Rajdhani", "Orbitron", "PingFang SC", sans-serif',
            'font_mono': '"Share Tech Mono", monospace',
            'radius_card': 2,
            'radius_button': 2,
        }
    }

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self._current_theme = 'minimal'
        self._app = None
        self._settings = QSettings('PDFTool', 'PDFTool')
        self._load_saved_theme()

    def _load_saved_theme(self):
        saved = self._settings.value('theme', 'minimal')
        if saved in self.THEMES:
            self._current_theme = saved

    def init_app(self, app: QApplication):
        self._app = app
        self.apply(self._current_theme)

    @property
    def current_theme(self) -> str:
        return self._current_theme

    @property
    def current_config(self) -> dict:
        return self.THEMES.get(self._current_theme, self.THEMES['minimal'])

    def apply(self, theme_name: str):
        if theme_name not in self.THEMES:
            theme_name = 'minimal'

        self._current_theme = theme_name
        self._settings.setValue('theme', theme_name)

        if self._app:
            self._app.setStyleSheet(self.THEMES[theme_name]['qss'])

        self.theme_changed.emit(theme_name)

    def toggle(self):
        themes = list(self.THEMES.keys())
        idx = themes.index(self._current_theme)
        next_theme = themes[(idx + 1) % len(themes)]
        self.apply(next_theme)
        return next_theme

    def get_color(self, color_name: str) -> QColor:
        config = self.current_config
        hex_color = config.get(color_name, '#000000')
        return QColor(hex_color)


def get_theme_manager() -> ThemeManager:
    return ThemeManager()


def apply_theme_to_widget(widget: QWidget, theme_name: str):
    """递归应用主题到所有子组件"""
    if hasattr(widget, 'set_theme'):
        widget.set_theme(theme_name)
    for child in widget.findChildren(QWidget):
        if hasattr(child, 'set_theme'):
            child.set_theme(theme_name)
