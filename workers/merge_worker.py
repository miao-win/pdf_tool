from pathlib import Path
from typing import List

from core.merge import PDFMerger, MergeItem
from . import BaseWorker
from utils.log_helper import get_logger

logger = get_logger(__name__)


class MergeWorker(BaseWorker):
    def __init__(
            self,
            output_dir: Path,
            merge_items: List[MergeItem],
            output_name: str = None,
            operation: PDFMerger = None,
            parent=None
    ):
        super().__init__(parent)
        self.output_dir = output_dir
        self.merge_items = merge_items
        self.output_name = output_name
        self._operation = operation

    def run(self):
        try:
            self.status.emit('正在合并 PDF...')
            input_path = self.merge_items[0].file_path if self.merge_items else Path('')
            merger = self._operation or PDFMerger(input_path)

            if self.merge_items:
                result = merger.merge_with_page_spec(
                    self.output_dir,
                    self.merge_items,
                    self.output_name
                )
            else:
                result = merger.merge_files(
                    self.output_dir,
                    [item.file_path for item in self.merge_items],
                    self.output_name
                )

            self.finished.emit(result.success, result)

        except Exception as e:
            logger.error("MergeWorker error: %s", e, exc_info=True)
            self.finished.emit(False, str(e))
