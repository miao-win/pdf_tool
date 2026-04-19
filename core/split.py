from pathlib import Path
from typing import List, Union

from pypdf import PdfReader, PdfWriter

from . import PDFOperationBase, PDFOperationResult


class PDFSplitter(PDFOperationBase):
    def execute(
            self,
            output_dir: Path,
            split_mode: str = 'range',
            page_spec: str = None,
            pages_per_file: int = None
    ) -> PDFOperationResult:
        reader = PdfReader(str(self.input_path))
        total_pages = len(reader.pages)
        output_files = []

        try:
            if split_mode == 'range':
                ranges = self.parse_page_ranges(page_spec, total_pages)
                for idx, page_indices in enumerate(ranges):
                    writer = PdfWriter()
                    for page_idx in page_indices:
                        if 0 <= page_idx < total_pages:
                            writer.add_page(reader.pages[page_idx])

                    output_path = output_dir / f'{self.input_path.stem}_part{idx + 1}.pdf'
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

                    output_path = output_dir / f'{self.input_path.stem}_p{idx + 1}_to_p{end_idx}.pdf'
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
            return PDFOperationResult(
                success=False,
                error_message=str(e)
            )

    def get_page_count(self) -> int:
        reader = PdfReader(str(self.input_path))
        return len(reader.pages)

    def split_by_ranges(
            self,
            output_dir: Path,
            page_spec: str
    ) -> PDFOperationResult:
        return self.execute(output_dir, split_mode='range', page_spec=page_spec)

    def split_by_fixed(
            self,
            output_dir: Path,
            pages_per_file: int
    ) -> PDFOperationResult:
        return self.execute(
            output_dir,
            split_mode='fixed',
            pages_per_file=pages_per_file
        )
