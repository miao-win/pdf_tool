from pathlib import Path

from core.compress import PDFCompressor
from . import BaseWorker
from utils.log_helper import get_logger

logger = get_logger(__name__)


class CompressWorker(BaseWorker):
    def __init__(
            self,
            input_path: Path,
            output_dir: Path,
            compression_level: str = 'medium',
            output_name: str = None,
            operation: PDFCompressor = None,
            parent=None
    ):
        super().__init__(parent)
        self.input_path = input_path
        self.output_dir = output_dir
        self.compression_level = compression_level
        self.output_name = output_name
        self._operation = operation

    def run(self):
        try:
            self.status.emit('正在压缩 PDF...')
            compressor = self._operation or PDFCompressor(self.input_path)
            result = compressor.compress(self.output_dir, self.compression_level, self.output_name)
            self.finished.emit(result.success, result)

        except Exception as e:
            logger.error("CompressWorker error: %s", e, exc_info=True)
            self.finished.emit(False, str(e))
