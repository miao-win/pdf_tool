from PySide6.QtWidgets import (
    QWidget, QStackedWidget, QMessageBox, QApplication, QMainWindow
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from .home_page import HomePage
from .split_page import SplitPage
from .merge_page import MergePage
from .compress_page import CompressPage


class MainWindow(QMainWindow):
    theme_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self._is_dark_theme = False
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.setWindowTitle('PDF 工具箱')
        self.setMinimumSize(1000, 700)

        # Create stacked widget as central widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.home_page = HomePage()
        self.stacked_widget.addWidget(self.home_page)

        self.split_page = SplitPage()
        self.stacked_widget.addWidget(self.split_page)

        self.merge_page = MergePage()
        self.stacked_widget.addWidget(self.merge_page)

        self.compress_page = CompressPage()
        self.stacked_widget.addWidget(self.compress_page)

        self.stacked_widget.setCurrentWidget(self.home_page)

    def _connect_signals(self):
        self.home_page.split_clicked.connect(lambda: self._switch_page(self.split_page))
        self.home_page.merge_clicked.connect(lambda: self._switch_page(self.merge_page))
        self.home_page.compress_clicked.connect(lambda: self._switch_page(self.compress_page))

        self.home_page.files_dropped.connect(self._on_files_dropped_home)

        self.split_page.back_clicked.connect(lambda: self._switch_page(self.home_page))
        self.merge_page.back_clicked.connect(lambda: self._switch_page(self.home_page))
        self.compress_page.back_clicked.connect(lambda: self._switch_page(self.home_page))

    def _switch_page(self, page: QWidget):
        if page == self.split_page:
            self.split_page.cleanup()
        elif page == self.merge_page:
            self.merge_page.cleanup()
        elif page == self.compress_page:
            self.compress_page.cleanup()
        self.stacked_widget.setCurrentWidget(page)

    def _on_files_dropped_home(self, file_paths: list, source: str):
        if not file_paths:
            return

        from pathlib import Path
        path = Path(file_paths[0])

        if path.suffix.lower() != '.pdf':
            QMessageBox.warning(self, '提示', '请拖拽 PDF 文件')
            return

        msg = QMessageBox(self)
        msg.setWindowTitle('选择功能')
        msg.setText(f'已识别文件: {path.name}\n请选择要执行的操作:')
        msg.setIcon(QMessageBox.Icon.Question)

        split_btn = msg.addButton('拆分', QMessageBox.ButtonRole.AcceptRole)
        merge_btn = msg.addButton('合并', QMessageBox.ButtonRole.AcceptRole)
        compress_btn = msg.addButton('压缩', QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg.addButton('取消', QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        clicked = msg.clickedButton()
        if clicked == split_btn:
            self.split_page._load_file(path)
            self._switch_page(self.split_page)
        elif clicked == merge_btn:
            self.merge_page._add_file(path)
            self._switch_page(self.merge_page)
        elif clicked == compress_btn:
            self.compress_page._load_file(path)
            self._switch_page(self.compress_page)

    def set_theme(self, is_dark: bool):
        self._is_dark_theme = is_dark
        self.theme_changed.emit(is_dark)

    def toggle_theme(self):
        self.set_theme(not self._is_dark_theme)
