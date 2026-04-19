from pathlib import Path

from core.compress import PDFCompressor
from . import BaseWorker


class CompressWorker(BaseWorker):
    def __init__(
            self,
            input_path: Path,
            output_dir: Path,
            compression_level: str = 'medium',
            parent=None
    ):
        super().__init__(parent)
        self.input_path = input_path
        self.output_dir = output_dir
        self.compression_level = compression_level

    def run(self):
        try:
            self.status.emit('正在压缩 PDF...')
            compressor = PDFCompressor(self.input_path)
            result = compressor.compress(self.output_dir, self.compression_level)
            self.finished.emit(result.success, result)

        except Exception as e:
            self.finished.emit(False, str(e))
