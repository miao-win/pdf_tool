from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader, PdfWriter

from . import PDFOperationBase, PDFOperationResult
from utils.pdf_cache import get_pdf_cache
from utils.log_helper import get_logger

logger = get_logger(__name__)


class MergeItem:
    def __init__(self, file_path: Path, page_spec: Optional[str] = None):
        self.file_path = file_path
        self.page_spec = page_spec


class PDFMerger(PDFOperationBase):
    def execute(
            self,
            output_dir: Path,
            merge_items: List[MergeItem] = None,
            file_paths: List[Path] = None,
            output_name: str = None
    ) -> PDFOperationResult:
        writer = PdfWriter()

        try:
            if merge_items:
                for item in merge_items:
                    try:
                        reader = PdfReader(str(item.file_path))
                        if item.page_spec:
                            page_indices = self._parse_page_spec(item.page_spec, len(reader.pages))
                            for idx in page_indices:
                                if 0 <= idx < len(reader.pages):
                                    writer.add_page(reader.pages[idx])
                        else:
                            for page in reader.pages:
                                writer.add_page(page)
                    except Exception as e:
                        logger.warning("Failed to merge %s: %s", item.file_path, e)
                        continue

            elif file_paths:
                for path in file_paths:
                    try:
                        reader = PdfReader(str(path))
                        for page in reader.pages:
                            writer.add_page(page)
                    except Exception as e:
                        logger.warning("Failed to merge %s: %s", path, e)
                        continue

            base_name = output_name if output_name else 'merged'
            output_path = output_dir / f'{base_name}.pdf'

            with open(output_path, 'wb') as f:
                writer.write(f)

            return PDFOperationResult(
                success=True,
                output_paths=[output_path],
                original_size=sum(p.stat().st_size for p in (file_paths or [item.file_path for item in merge_items])),
                output_size=output_path.stat().st_size
            )

        except Exception as e:
            logger.error("Merge operation failed: %s", e, exc_info=True)
            return PDFOperationResult(
                success=False,
                error_message=str(e)
            )

    def _parse_page_spec(self, spec: str, total_pages: int) -> List[int]:
        indices = []
        for part in spec.split(','):
            part = part.strip()
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

    def merge_files(
            self,
            output_dir: Path,
            file_paths: List[Path],
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, file_paths=file_paths, output_name=output_name)

    def merge_with_page_spec(
            self,
            output_dir: Path,
            merge_items: List[MergeItem],
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, merge_items=merge_items, output_name=output_name)
