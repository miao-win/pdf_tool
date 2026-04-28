from pathlib import Path

from core.split import PDFSplitter
from . import BaseWorker
from utils.log_helper import get_logger

logger = get_logger(__name__)


class SplitWorker(BaseWorker):
    def __init__(
            self,
            input_path: Path,
            output_dir: Path,
            split_mode: str,
            page_spec: str = None,
            pages_per_file: int = None,
            output_name: str = None,
            operation: PDFSplitter = None,
            parent=None
    ):
        super().__init__(parent)
        self.input_path = input_path
        self.output_dir = output_dir
        self.split_mode = split_mode
        self.page_spec = page_spec
        self.pages_per_file = pages_per_file
        self.output_name = output_name
        self._operation = operation

    def run(self):
        try:
            self.status.emit('正在拆分 PDF...')
            splitter = self._operation or PDFSplitter(self.input_path)

            if self.split_mode == 'range':
                result = splitter.split_by_ranges(self.output_dir, self.page_spec, self.output_name)
            else:
                result = splitter.split_by_fixed(self.output_dir, self.pages_per_file, self.output_name)

            self.finished.emit(result.success, result)

        except Exception as e:
            logger.error("SplitWorker error: %s", e, exc_info=True)
            self.finished.emit(False, str(e))
