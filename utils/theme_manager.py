from pathlib import Path
from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QApplication


class ThemeManager(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self._app = app
        self._is_dark = False
        self._theme_file_light = Path(__file__).parent.parent / 'assets' / 'styles' / 'light_theme.qss'
        self._theme_file_dark = Path(__file__).parent.parent / 'assets' / 'styles' / 'dark_theme.qss'
        self._system_theme_changed = False

    def _replace_css_variables(self, css_content: str, is_dark: bool) -> str:
        # 定义主题变量
        if is_dark:
            variables = {
                '--primary-color': '#3B82F6',
                '--primary-hover': '#60A5FA',
                '--primary-disabled': '#475569',
                '--background': '#0F172A',
                '--surface': '#1E293B',
                '--surface-hover': '#334155',
                '--text-primary': '#F1F5F9',
                '--text-secondary': '#94A3B8',
                '--border-color': '#334155',
                '--border-focus': '#3B82F6',
                '--danger-color': '#EF4444',
                '--danger-hover': '#F87171',
                '--success-color': '#22C55E',
                '--shadow': 'rgba(0, 0, 0, 0.3)'
            }
        else:
            variables = {
                '--primary-color': '#2563EB',
                '--primary-hover': '#3B82F6',
                '--primary-disabled': '#94A3B8',
                '--background': '#F8FAFC',
                '--surface': '#FFFFFF',
                '--surface-hover': '#F1F5F9',
                '--text-primary': '#1E293B',
                '--text-secondary': '#64748B',
                '--border-color': '#E2E8F0',
                '--border-focus': '#2563EB',
                '--danger-color': '#EF4444',
                '--danger-hover': '#DC2626',
                '--success-color': '#22C55E',
                '--shadow': 'rgba(0, 0, 0, 0.1)'
            }
        
        # 替换CSS变量
        for var, value in variables.items():
            css_content = css_content.replace(var, value)
        
        # 移除:root块
        import re
        css_content = re.sub(r':root \{[^}]*\}', '', css_content)
        
        return css_content

    def load_theme(self, is_dark: bool):
        self._is_dark = is_dark
        theme_file = self._theme_file_dark if is_dark else self._theme_file_light
        if theme_file.exists():
            with open(theme_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
                # 替换CSS变量
                css_content = self._replace_css_variables(css_content, is_dark)
                self._app.setStyleSheet(css_content)
        else:
            self._apply_default_theme(is_dark)

    def _apply_default_theme(self, is_dark: bool):
        if is_dark:
            self._app.setStyleSheet('''
                QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton#primaryBtn {
                    background-color: #4a90d9;
                    color: white;
                    border: none;
                }
                QPushButton#primaryBtn:hover {
                    background-color: #5ba0e9;
                }
                QPushButton#backBtn {
                    background-color: transparent;
                    border: none;
                    color: #4a90d9;
                }
                QLineEdit, QTextEdit, QListWidget {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 4px;
                }
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 8px;
                }
                QGroupBox::title {
                    color: #e0e0e0;
                }
                QProgressBar {
                    border: 1px solid #555;
                    border-radius: 4px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4a90d9;
                }
            ''')
        else:
            self._app.setStyleSheet('''
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    border: 1px solid #ccc;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton#primaryBtn {
                    background-color: #4a90d9;
                    color: white;
                    border: none;
                }
                QPushButton#primaryBtn:hover {
                    background-color: #5ba0e9;
                }
                QPushButton#backBtn {
                    background-color: transparent;
                    border: none;
                    color: #4a90d9;
                }
                QLineEdit, QTextEdit, QListWidget {
                    background-color: white;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 4px;
                }
                QGroupBox {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 8px;
                }
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4a90d9;
                }
            ''')

    def toggle_theme(self):
        self.load_theme(not self._is_dark)
        return self._is_dark

    @property
    def is_dark(self) -> bool:
        return self._is_dark
