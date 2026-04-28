from typing import Dict, Optional, Type
from PySide6.QtCore import Signal, QObject
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PageRegistry(QObject):
    page_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pages: Dict[str, object] = {}
        self._page_order: list = []
        self._page_index_map: Dict[str, int] = {}

    def register(self, page_id: str, page_widget: object):
        if page_id in self._pages:
            logger.warning("Page '%s' already registered, replacing", page_id)
            self._pages[page_id] = page_widget
            return

        self._pages[page_id] = page_widget
        self._page_order.append(page_id)
        self._rebuild_index_map()
        logger.debug("Registered page: %s", page_id)

    def get_page(self, page_id: str) -> Optional[object]:
        return self._pages.get(page_id)

    def get_index(self, page_id: str) -> int:
        return self._page_index_map.get(page_id, -1)

    def get_page_id(self, index: int) -> Optional[str]:
        if 0 <= index < len(self._page_order):
            return self._page_order[index]
        return None

    @property
    def page_count(self) -> int:
        return len(self._pages)

    @property
    def page_ids(self) -> list:
        return list(self._page_order)

    def navigate_to(self, page_id: str):
        if page_id in self._pages:
            self.page_requested.emit(page_id)
        else:
            logger.warning("Attempted to navigate to unregistered page: %s", page_id)

    def _rebuild_index_map(self):
        self._page_index_map = {
            page_id: idx for idx, page_id in enumerate(self._page_order)
        }
