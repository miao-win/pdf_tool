import io
from enum import Enum
from pathlib import Path

import pikepdf
from pikepdf import Pdf, Dictionary
from PIL import Image

from . import PDFOperationBase, PDFOperationResult
from utils.log_helper import get_logger

logger = get_logger(__name__)


class CompressionLevel(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class PDFCompressor(PDFOperationBase):
    JPEG_QUALITIES = {
        CompressionLevel.LOW: 85,
        CompressionLevel.MEDIUM: 65,
        CompressionLevel.HIGH: 40,
    }

    DPI_SETTINGS = {
        CompressionLevel.LOW: 150,
        CompressionLevel.MEDIUM: 120,
        CompressionLevel.HIGH: 72,
    }

    def execute(
            self,
            output_dir: Path,
            compression_level: str = 'medium',
            output_name: str = None
    ) -> PDFOperationResult:
        level = CompressionLevel(compression_level)
        original_size = self.input_path.stat().st_size

        try:
            with Pdf.open(self.input_path) as pdf:
                self._compress_pdf(pdf, level)
                base_name = output_name if output_name else f'{self.input_path.stem}_compressed'
                output_path = output_dir / f'{base_name}.pdf'
                pdf.save(
                    output_path,
                    compress_streams=True,
                )

            output_size = output_path.stat().st_size

            return PDFOperationResult(
                success=True,
                output_paths=[output_path],
                original_size=original_size,
                output_size=output_size
            )

        except Exception as e:
            logger.error("Compress operation failed for %s: %s", self.input_path, e, exc_info=True)
            return PDFOperationResult(
                success=False,
                error_message=str(e)
            )

    def _compress_pdf(self, pdf: Pdf, level: CompressionLevel):
        if pdf.is_linearized:
            pdf.remove_metadata()

        for page in pdf.pages:
            self._process_page_resources(page, level)

        pdf.remove_unreferenced_resources()

        self._rewrite_object_streams(pdf)

    def _process_page_resources(self, page: Dictionary, level: CompressionLevel):
        resources = page.get('/Resources')
        if not isinstance(resources, Dictionary):
            return

        xobject = resources.get('/XObject')
        if not isinstance(xobject, Dictionary):
            return

        for name, xobj_ref in xobject.items():
            if not isinstance(xobj_ref, pikepdf._core.Object):
                continue

            try:
                xobj = xobj_ref
                if xobj.get('/Subtype') == '/Image' and xobj.get('/Filter') == '/DCTDecode':
                    self._recompress_jpeg(xobj, level)
            except Exception as e:
                logger.warning("Failed to process XObject %s: %s", name, e)
                continue

    def _recompress_jpeg(self, xobj: pikepdf._core.Object, level: CompressionLevel):
        try:
            image_data = bytes(xobj.get('/DecodeParms', {}).get_stream())
            if not image_data:
                return

            with Image.open(io.BytesIO(image_data)) as img:
                quality = self.JPEG_QUALITIES[level]
                output_buffer = io.BytesIO()
                img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                new_data = output_buffer.getvalue()

            xobj._write_hint = None
            xobj.unbind()
        except Exception as e:
            logger.warning("Failed to recompress JPEG: %s", e)

    def _rewrite_object_streams(self, pdf: Pdf):
        try:
            pdf.allow_multiple_images_objects = True
        except Exception as e:
            logger.debug("allow_multiple_images_objects not supported: %s", e)

    def compress(
            self,
            output_dir: Path,
            level: str = 'medium',
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, compression_level=level, output_name=output_name)

    def get_compression_estimate(self, level: str) -> str:
        estimates = {
            'low': '10-20%',
            'medium': '30-50%',
            'high': '50-70%',
        }
        return estimates.get(level, 'unknown')
