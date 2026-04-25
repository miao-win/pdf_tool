import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from ui.pages.home_page import HomePage
from ui.split_page import SplitPage
from ui.merge_page import MergePage
from ui.compress_page import CompressPage
from ui.plugins.page_editor_page import PageEditorPage
from ui.plugins.pdf_to_image_page import PDFToImagePage
from ui.plugins.to_pdf_page import ToPDFPage
from utils.theme_manager import get_theme_manager


def get_app_icon() -> QIcon:
    icon_path = Path(__file__).parent / 'assets' / 'app_icon.ico'
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PDF Tool')
    app.setOrganizationName('PDFTool')
    app.setStyle('Fusion')

    # 初始化主题管理器
    theme_manager = get_theme_manager()
    theme_manager.init_app(app)

    main_window = MainWindow()
    app.main_window = main_window
    main_window.setWindowIcon(get_app_icon())

    # 创建页面
    home_page = HomePage()
    split_page = SplitPage()
    merge_page = MergePage()
    compress_page = CompressPage()
    page_editor_page = PageEditorPage()
    pdf_to_image_page = PDFToImagePage()
    to_pdf_page = ToPDFPage()

    # 添加页面到主窗口
    main_window.add_page(home_page, 'home')
    main_window.add_page(split_page, 'split')
    main_window.add_page(merge_page, 'merge')
    main_window.add_page(compress_page, 'compress')
    main_window.add_page(page_editor_page, 'page_editor')
    main_window.add_page(pdf_to_image_page, 'pdf_to_image')
    main_window.add_page(to_pdf_page, 'to_pdf')

    # 连接信号
    home_page.split_clicked.connect(lambda: main_window.set_page(1))
    home_page.merge_clicked.connect(lambda: main_window.set_page(2))
    home_page.compress_clicked.connect(lambda: main_window.set_page(3))
    home_page.page_editor_clicked.connect(lambda: main_window.set_page(4))
    home_page.pdf_to_image_clicked.connect(lambda: main_window.set_page(5))
    home_page.to_pdf_clicked.connect(lambda: main_window.set_page(6))

    # 返回主页
    split_page.back_clicked.connect(lambda: main_window.set_page(0))
    merge_page.back_clicked.connect(lambda: main_window.set_page(0))
    compress_page.back_clicked.connect(lambda: main_window.set_page(0))
    page_editor_page.back_clicked.connect(lambda: main_window.set_page(0))
    pdf_to_image_page.back_clicked.connect(lambda: main_window.set_page(0))
    to_pdf_page.back_clicked.connect(lambda: main_window.set_page(0))

    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
