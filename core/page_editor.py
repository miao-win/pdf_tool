from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader, PdfWriter

from . import PDFOperationBase, PDFOperationResult
from utils.pdf_cache import get_pdf_cache
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PageEditorOperation(PDFOperationBase):
    def execute(
            self,
            output_dir: Path,
            operation_type: str,
            angle: Optional[int] = None,
            page_spec: Optional[str] = None,
            clockwise: bool = True,
            output_name: str = None
    ) -> PDFOperationResult:
        try:
            reader = PdfReader(str(self.input_path))
        except Exception as e:
            logger.error("Failed to open PDF %s: %s", self.input_path, e, exc_info=True)
            return PDFOperationResult(success=False, error_message=f'无法打开PDF文件: {e}')

        total_pages = len(reader.pages)

        try:
            if operation_type == 'rotate':
                result = self._rotate_pages(reader, output_dir, angle, page_spec, clockwise, total_pages, output_name)
            elif operation_type == 'delete':
                result = self._delete_pages(reader, output_dir, page_spec, total_pages, output_name)
            else:
                return PDFOperationResult(success=False, error_message=f'未知操作类型: {operation_type}')

            return result

        except Exception as e:
            logger.error("Page editor operation failed: %s", e, exc_info=True)
            return PDFOperationResult(success=False, error_message=str(e))

    def _rotate_pages(
            self,
            reader: PdfReader,
            output_dir: Path,
            angle: int,
            page_spec: Optional[str],
            clockwise: bool,
            total_pages: int,
            output_name: Optional[str]
    ) -> PDFOperationResult:
        writer = PdfWriter()

        if page_spec:
            page_indices = set(self._parse_page_spec(page_spec, total_pages))
        else:
            page_indices = set(range(total_pages))

        rotation_angle = angle if clockwise else -angle

        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if i in page_indices:
                existing_rotation = writer.pages[-1].get('/Rotate', 0)
                if isinstance(existing_rotation, int):
                    total_rotation = existing_rotation + rotation_angle
                else:
                    total_rotation = rotation_angle
                writer.pages[-1]['/Rotate'] = total_rotation

        base_name = output_name if output_name else f'{self.input_path.stem}_rotated'
        output_path = output_dir / f'{base_name}.pdf'

        with open(output_path, 'wb') as f:
            writer.write(f)

        return PDFOperationResult(
            success=True,
            output_paths=[output_path],
            original_size=self.input_path.stat().st_size,
            output_size=output_path.stat().st_size
        )

    def _delete_pages(
            self,
            reader: PdfReader,
            output_dir: Path,
            page_spec: str,
            total_pages: int,
            output_name: Optional[str]
    ) -> PDFOperationResult:
        writer = PdfWriter()
        delete_indices = set(self._parse_page_spec(page_spec, total_pages))

        for i, page in enumerate(reader.pages):
            if i not in delete_indices:
                writer.add_page(page)

        base_name = output_name if output_name else f'{self.input_path.stem}_edited'
        output_path = output_dir / f'{base_name}.pdf'

        with open(output_path, 'wb') as f:
            writer.write(f)

        return PDFOperationResult(
            success=True,
            output_paths=[output_path],
            original_size=self.input_path.stat().st_size,
            output_size=output_path.stat().st_size
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

    def rotate_pages(
            self,
            output_dir: Path,
            angle: int,
            page_spec: Optional[str] = None,
            clockwise: bool = True,
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, 'rotate', angle, page_spec, clockwise, output_name)

    def delete_pages(
            self,
            output_dir: Path,
            page_spec: str,
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, 'delete', page_spec=page_spec, output_name=output_name)

    def get_page_count(self) -> int:
        cache = get_pdf_cache()
        cached = cache.get_page_count(self.input_path)
        if cached is not None:
            return cached

        try:
            reader = PdfReader(str(self.input_path))
            count = len(reader.pages)
            return count
        except Exception as e:
            logger.warning("Failed to get page count for %s: %s", self.input_path, e)
            return 0
