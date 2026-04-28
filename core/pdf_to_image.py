from pathlib import Path
from typing import List, Optional

import pymupdf

from . import PDFOperationBase, PDFOperationResult
from utils.pdf_cache import get_pdf_cache
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PDFToImageConverter(PDFOperationBase):
    SUPPORTED_FORMATS = ('png', 'jpg', 'jpeg', 'tiff', 'bmp')

    def execute(
            self,
            output_dir: Path,
            format: str = 'png',
            dpi: int = 150,
            page_spec: Optional[str] = None
    ) -> PDFOperationResult:
        if format.lower() not in self.SUPPORTED_FORMATS:
            return PDFOperationResult(
                success=False,
                error_message=f'不支持的格式: {format}'
            )

        try:
            doc = pymupdf.open(str(self.input_path))
        except Exception as e:
            logger.error("Failed to open PDF %s: %s", self.input_path, e, exc_info=True)
            return PDFOperationResult(success=False, error_message=f'无法打开PDF文件: {e}')

        total_pages = doc.page_count
        output_files = []

        try:
            if page_spec:
                page_indices = self._parse_page_spec(page_spec, total_pages)
            else:
                page_indices = list(range(total_pages))

            zoom = dpi / 72.0
            mat = pymupdf.Matrix(zoom, zoom)

            for page_idx in page_indices:
                if page_idx < 0 or page_idx >= total_pages:
                    continue

                page = doc[page_idx]
                pix = page.get_pixmap(matrix=mat, alpha=(format == 'png'))

                output_path = output_dir / f'{self.input_path.stem}_page_{page_idx + 1}.{format}'
                pix.save(str(output_path))
                output_files.append(output_path)

            doc.close()

            return PDFOperationResult(
                success=True,
                output_paths=output_files,
                original_size=self.input_path.stat().st_size,
                output_size=sum(p.stat().st_size for p in output_files)
            )

        except Exception as e:
            logger.error("PDF to image conversion failed: %s", e, exc_info=True)
            doc.close()
            return PDFOperationResult(
                success=False,
                error_message=str(e)
            )

    def _parse_page_spec(self, spec: str, total_pages: int) -> List[int]:
        indices = []
        for part in spec.split(','):
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                start, end = part.split('-', 1)
                start_idx = int(start.strip()) - 1
                end_idx = int(end.strip()) - 1
                if start_idx < 0 or end_idx >= total_pages:
                    raise ValueError(f'页码超出范围: {part} (总页数: {total_pages})')
                indices.extend(range(start_idx, end_idx + 1))
            else:
                idx = int(part) - 1
                if idx < 0 or idx >= total_pages:
                    raise ValueError(f'页码超出范围: {part} (总页数: {total_pages})')
                indices.append(idx)
        return indices

    def convert(
            self,
            output_dir: Path,
            format: str = 'png',
            dpi: int = 150,
            page_spec: Optional[str] = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, format, dpi, page_spec)

    def get_page_count(self) -> int:
        cache = get_pdf_cache()
        return cache.get_page_count_or_load(self.input_path)
