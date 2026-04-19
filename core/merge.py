from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

from pypdf import PdfReader, PdfWriter

from . import PDFOperationBase, PDFOperationResult


@dataclass
class MergeItem:
    file_path: Path
    page_spec: Optional[str] = None

    def get_page_indices(self) -> List[int]:
        if not self.page_spec:
            reader = PdfReader(str(self.file_path))
            return list(range(len(reader.pages)))

        indices = []
        for part in self.page_spec.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                indices.extend(range(start - 1, end))
            else:
                indices.append(int(part) - 1)
        return indices


class PDFMerger(PDFOperationBase):
    def execute(
            self,
            output_dir: Path,
            merge_items: List[MergeItem] = None,
            output_name: str = None
    ) -> PDFOperationResult:
        if merge_items is None:
            merge_items = []

        writer = PdfWriter()
        total_input_size = 0
        all_indices = []

        try:
            for item in merge_items:
                if not self.validate_pdf(item.file_path):
                    continue
                total_input_size += item.file_path.stat().st_size
                reader = PdfReader(str(item.file_path))

                for page_idx in item.get_page_indices():
                    if 0 <= page_idx < len(reader.pages):
                        writer.add_page(reader.pages[page_idx])
                        all_indices.append((item.file_path, page_idx))

            output_name = output_name or f'{self.input_path.stem}_merged'
            output_path = output_dir / f'{output_name}.pdf'

            with open(output_path, 'wb') as f:
                writer.write(f)

            return PDFOperationResult(
                success=True,
                output_paths=[output_path],
                original_size=total_input_size,
                output_size=output_path.stat().st_size
            )

        except Exception as e:
            return PDFOperationResult(
                success=False,
                error_message=str(e)
            )

    def merge_files(
            self,
            output_dir: Path,
            file_paths: List[Path],
            output_name: str = None
    ) -> PDFOperationResult:
        merge_items = [MergeItem(fp) for fp in file_paths]
        return self.execute(output_dir, merge_items=merge_items, output_name=output_name)

    def merge_with_page_spec(
            self,
            output_dir: Path,
            merge_items: List[MergeItem],
            output_name: str = None
    ) -> PDFOperationResult:
        return self.execute(output_dir, merge_items=merge_items, output_name=output_name)
