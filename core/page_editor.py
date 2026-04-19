from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader, PdfWriter

from . import PDFOperationBase, PDFOperationResult


class PageEditorOperation(PDFOperationBase):
    def __init__(self, input_path: Path):
        super().__init__(input_path)

    def rotate_pages(
            self,
            output_dir: Path,
            angle: int,
            page_spec: Optional[str] = None,
            clockwise: bool = True
    ) -> PDFOperationResult:
        total_pages = self.get_page_count()
        target_pages = self._parse_page_spec(page_spec, total_pages) if page_spec else None

        actual_angle = angle if clockwise else -angle

        try:
            reader = PdfReader(str(self.input_path))
            writer = PdfWriter()

            for idx, page in enumerate(reader.pages):
                if target_pages is None or idx in target_pages:
                    page.rotate(actual_angle)
                writer.add_page(page)

            output_path = output_dir / f'{self.input_path.stem}_rotated.pdf'
            with open(output_path, 'wb') as f:
                writer.write(f)

            return PDFOperationResult(
                success=True,
                output_paths=[output_path],
                original_size=self.input_path.stat().st_size,
                output_size=output_path.stat().st_size
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=str(e))

    def delete_pages(
            self,
            output_dir: Path,
            page_spec: str
    ) -> PDFOperationResult:
        total_pages = self.get_page_count()

        try:
            delete_indices = self._parse_page_spec(page_spec, total_pages)
        except ValueError as e:
            return PDFOperationResult(success=False, error_message=f'页码语法错误: {e}')

        if not delete_indices:
            return PDFOperationResult(success=False, error_message='请指定要删除的页码')

        all_indices = set(range(total_pages))
        keep_indices = sorted(all_indices - set(delete_indices))

        if len(keep_indices) == 0:
            return PDFOperationResult(success=False, error_message='删除后PDF将没有页面，操作已取消')

        try:
            reader = PdfReader(str(self.input_path))
            writer = PdfWriter()

            for idx in keep_indices:
                writer.add_page(reader.pages[idx])

            output_path = output_dir / f'{self.input_path.stem}_trimmed.pdf'
            with open(output_path, 'wb') as f:
                writer.write(f)

            return PDFOperationResult(
                success=True,
                output_paths=[output_path],
                original_size=self.input_path.stat().st_size,
                output_size=output_path.stat().st_size
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=str(e))

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
                try:
                    start, end = part.split('-', 1)
                    start, end = int(start.strip()), int(end.strip())
                    if start < 1 or end > total_pages or start > end:
                        raise ValueError(f'页码 {start}-{end} 超出范围 (1-{total_pages})')
                    indices.extend(range(start - 1, end))
                except ValueError as e:
                    if 'too many values' not in str(e).lower():
                        raise ValueError(str(e))
                    raise
            else:
                try:
                    page_num = int(part)
                    if page_num < 1 or page_num > total_pages:
                        raise ValueError(f'页码 {page_num} 超出范围 (1-{total_pages})')
                    indices.append(page_num - 1)
                except ValueError as e:
                    raise ValueError(f'无效的页码: {part}') from e

        return indices

    def get_page_count(self) -> int:
        reader = PdfReader(str(self.input_path))
        return len(reader.pages)

    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        operation = kwargs.get('operation', 'rotate')
        if operation == 'rotate':
            angle = kwargs.get('angle', 90)
            page_spec = kwargs.get('page_spec', None)
            clockwise = kwargs.get('clockwise', True)
            return self.rotate_pages(output_dir, angle, page_spec, clockwise)
        elif operation == 'delete':
            page_spec = kwargs.get('page_spec', '')
            return self.delete_pages(output_dir, page_spec)
        else:
            return PDFOperationResult(success=False, error_message='未知的操作类型')
