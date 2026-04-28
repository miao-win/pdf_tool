from pathlib import Path
from typing import List, Union

from pypdf import PdfReader, PdfWriter

from . import PDFOperationBase, PDFOperationResult
from utils.pdf_cache import get_pdf_cache
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PDFSplitter(PDFOperationBase):
    def execute(
            self,
            output_dir: Path,
            split_mode: str = 'range',
            page_spec: str = None,
            pages_per_file: int = None,
            output_name: str = None
    ) -> PDFOperationResult:
        try:
            reader = PdfReader(str(self.input_path))
        except Exception as e:
            logger.error("Failed to open PDF %s: %s", self.input_path, e, exc_info=True)
            return PDFOperationResult(success=False, error_message=f'无法打开PDF文件: {e}')

        total_pages = len(reader.pages)
        output_files = []

        base_name = output_name if output_name else self.input_path.stem

        output_subdir = output_dir / base_name
        output_subdir.mkdir(parents=True, exist_ok=True)

        try:
            if split_mode == 'range':
                ranges = self.parse_page_ranges(page_spec, total_pages)
                for idx, page_indices in enumerate(ranges):
                    writer = PdfWriter()
                    for page_idx in page_indices:
                        if 0 <= page_idx < total_pages:
                            writer.add_page(reader.pages[page_idx])

                    output_path = output_subdir / f'{base_name}_part{idx + 1}.pdf'
                    with open(output_path, 'wb') as f:
                        writer.write(f)
                    output_files.append(output_path)

            elif split_mode == 'fixed':
                pages_per_file = pages_per_file or 1
                for idx in range(0, total_pages, pages_per_file):
                    writer = PdfWriter()
                    end_idx = min(idx + pages_per_file, total_pages)
                    for page_idx in range(idx, end_idx):
                        writer.add_page(reader.pages[page_idx])

                    output_path = output_subdir / f'{base_name}_p{idx + 1}_to_p{end_idx}.pdf'
                    with open(output_path, 'wb') as f:
                        writer.write(f)
                    output_files.append(output_path)

            return PDFOperationResult(
                success=True,
                output_paths=output_files,
                original_size=self.input_path.stat().st_size,
                output_size=sum(p.stat().st_size for p in output_files)
            )

        except Exception as e:
            logger.error("Split operation failed: %s", e, exc_info=True)
            return PDFOperationResult(
                success=False,
                error_message=str(e)
            )

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

    def split_by_ranges(
            self,
            output_dir: Path,
            page_spec: str,
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, split_mode='range', page_spec=page_spec, output_name=output_name)

    def split_by_fixed(
            self,
            output_dir: Path,
            pages_per_file: int,
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(
            output_dir,
            split_mode='fixed',
            pages_per_file=pages_per_file,
            output_name=output_name
        )
