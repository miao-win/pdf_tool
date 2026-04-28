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
from utils.log_helper import get_logger

logger = get_logger(__name__)


def get_app_icon() -> QIcon:
    icon_path = Path(__file__).parent / 'assets' / 'app_icon.ico'
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


PAGE_DEFINITIONS = [
    ('home', HomePage),
    ('split', SplitPage),
    ('merge', MergePage),
    ('compress', CompressPage),
    ('page_editor', PageEditorPage),
    ('pdf_to_image', PDFToImagePage),
    ('to_pdf', ToPDFPage),
]


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PDF Tool')
    app.setOrganizationName('PDFTool')
    app.setStyle('Fusion')

    theme_manager = get_theme_manager()
    theme_manager.init_app(app)

    main_window = MainWindow()
    app.main_window = main_window
    main_window.setWindowIcon(get_app_icon())

    pages = {}
    for page_id, page_class in PAGE_DEFINITIONS:
        page = page_class()
        main_window.add_page(page, page_id)
        pages[page_id] = page

    home_page = pages['home']
    for page_id in ['split', 'merge', 'compress', 'page_editor', 'pdf_to_image', 'to_pdf']:
        signal = getattr(home_page, f'{page_id}_clicked', None)
        if signal:
            signal.connect(lambda pid=page_id: main_window.set_page(pid))

    for page_id, page in pages.items():
        if page_id == 'home':
            continue
        if hasattr(page, 'back_clicked'):
            page.back_clicked.connect(lambda: main_window.set_page('home'))

    main_window.show()
    logger.info("PDF Tool started successfully")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
