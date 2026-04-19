import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from utils.theme_manager import ThemeManager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PDF Tool')
    app.setOrganizationName('PDFTool')

    theme_manager = ThemeManager(app)

    main_window = MainWindow()

    app.setStyle('Fusion')

    try:
        from PySide6.QtCore import QSettings
        settings = QSettings('PDFTool', 'PDFTool')
        is_dark = settings.value('dark_theme', False, type=bool)
    except Exception:
        is_dark = False

    theme_manager.load_theme(is_dark)

    def toggle_theme():
        new_is_dark = theme_manager.toggle_theme()
        try:
            from PySide6.QtCore import QSettings
            settings = QSettings('PDFTool', 'PDFTool')
            settings.setValue('dark_theme', new_is_dark)
        except Exception:
            pass

    main_window.theme_changed.connect(lambda dark: theme_manager.load_theme(dark))

    # Add menu bar to main window
    menu_bar = main_window.menuBar()
    view_menu = menu_bar.addMenu('视图')

    theme_action = view_menu.addAction('切换主题')
    theme_action.triggered.connect(toggle_theme)

    view_menu.addSeparator()

    exit_action = view_menu.addAction('退出')
    exit_action.triggered.connect(app.quit)

    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
