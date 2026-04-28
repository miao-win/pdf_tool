from pathlib import Path
from typing import Optional

from core.pdf_to_image import PDFToImageConverter
from . import BaseWorker
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PDFToImageWorker(BaseWorker):
    def __init__(
            self,
            input_path: Path,
            output_dir: Path,
            format: str = 'png',
            dpi: int = 150,
            page_spec: Optional[str] = None,
            operation: PDFToImageConverter = None,
            parent=None
    ):
        super().__init__(parent)
        self.input_path = input_path
        self.output_dir = output_dir
        self.format = format
        self.dpi = dpi
        self.page_spec = page_spec
        self._operation = operation

    def run(self):
        try:
            self.status.emit('正在转换 PDF 为图片...')
            converter = self._operation or PDFToImageConverter(self.input_path)

            total_pages = converter.get_page_count()
            self.progress.emit(0)

            result = converter.convert(
                self.output_dir,
                self.format,
                self.dpi,
                self.page_spec
            )

            if result.success:
                self.progress.emit(100)
                self.status.emit('转换完成')
            else:
                self.status.emit('转换失败')

            self.finished.emit(result.success, result)

        except Exception as e:
            logger.error("PDFToImageWorker error: %s", e, exc_info=True)
            self.finished.emit(False, str(e))
