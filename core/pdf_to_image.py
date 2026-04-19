from pathlib import Path
from typing import List, Optional

import pymupdf

from . import PDFOperationBase, PDFOperationResult


class PDFToImageConverter(PDFOperationBase):
    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg']
    DPI_OPTIONS = [72, 150, 300, 600]

    def __init__(self, input_path: Path):
        super().__init__(input_path)

    def convert(
            self,
            output_dir: Path,
            format: str = 'png',
            dpi: int = 150,
            page_spec: Optional[str] = None
    ) -> PDFOperationResult:
        if format.lower() not in self.SUPPORTED_FORMATS:
            return PDFOperationResult(
                success=False,
                error_message=f'不支持的格式: {format}，支持的格式: {", ".join(self.SUPPORTED_FORMATS)}'
            )

        if dpi not in self.DPI_OPTIONS:
            return PDFOperationResult(
                success=False,
                error_message=f'不支持的DPI: {dpi}，支持的DPI: {", ".join(map(str, self.DPI_OPTIONS))}'
            )

        total_pages = self.get_page_count()
        target_pages = self._parse_page_spec(page_spec, total_pages) if page_spec else None

        output_paths = []

        try:
            doc = pymupdf.open(str(self.input_path))

            for page_num in range(doc.page_count):
                if target_pages is not None and page_num not in target_pages:
                    continue

                page = doc[page_num]
                mat = pymupdf.Matrix(dpi / 72.0, dpi / 72.0)
                pix = page.get_pixmap(matrix=mat)

                output_path = output_dir / f'{self.input_path.stem}_page_{page_num + 1}.{format.lower()}'
                pix.save(str(output_path))
                output_paths.append(output_path)

            doc.close()

            return PDFOperationResult(
                success=True,
                output_paths=output_paths,
                original_size=self.input_path.stat().st_size,
                output_size=sum(p.stat().st_size for p in output_paths)
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=str(e))

    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        format = kwargs.get('format', 'png')
        dpi = kwargs.get('dpi', 150)
        page_spec = kwargs.get('page_spec', None)
        return self.convert(output_dir, format, dpi, page_spec)

    def _parse_page_spec(self, page_spec: str, total_pages: int) -> List[int]:
        if not page_spec or not page_spec.strip():
            return []

        indices = []
        parts = page_spec.split(',')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > total_pages or start > end:
                    raise ValueError(f'页码 {start}-{end} 超出范围 (1-{total_pages})')
                indices.extend(range(start - 1, end))
            else:
                page_num = int(part)
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f'页码 {page_num} 超出范围 (1-{total_pages})')
                indices.append(page_num - 1)

        return indices

    def get_page_count(self) -> int:
        doc = pymupdf.open(str(self.input_path))
        count = doc.page_count
        doc.close()
        return count
