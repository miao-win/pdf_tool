import threading
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from utils.log_helper import get_logger

logger = get_logger(__name__)

MAX_CACHE_SIZE = 10


class PDFDocumentCache:
    def __init__(self, max_size: int = MAX_CACHE_SIZE):
        self._cache: OrderedDict[str, tuple] = OrderedDict()
        self._max_size = max_size
        self._lock = threading.Lock()

    def _make_key(self, path: Path) -> str:
        try:
            mtime = path.stat().st_mtime
            size = path.stat().st_size
            return f"{path}|{mtime}|{size}"
        except OSError:
            return str(path)

    def get_page_count(self, path: Path) -> Optional[int]:
        key = self._make_key(path)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                doc_info = self._cache[key]
                return doc_info['page_count']
        return None

    def get_page_count_or_load(self, path: Path) -> int:
        cached = self.get_page_count(path)
        if cached is not None:
            return cached

        try:
            import pymupdf
            doc = pymupdf.open(str(path))
            page_count = doc.page_count
            doc.close()

            key = self._make_key(path)
            with self._lock:
                self._cache[key] = {'page_count': page_count, 'path': str(path)}
                self._cache.move_to_end(key)
                if len(self._cache) > self._max_size:
                    self._cache.popitem(last=False)

            return page_count
        except Exception as e:
            logger.warning("Failed to get page count for %s: %s", path, e)
            return 0

    def invalidate(self, path: Path):
        key = self._make_key(path)
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)


_cache_instance: Optional[PDFDocumentCache] = None


def get_pdf_cache() -> PDFDocumentCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = PDFDocumentCache()
    return _cache_instance
