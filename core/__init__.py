from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class PDFOperationResult:
    success: bool
    output_paths: List[Path] = None
    error_message: str = None
    original_size: int = 0
    output_size: int = 0

    @property
    def compression_ratio(self) -> float:
        if self.original_size and self.output_size:
            return (1 - self.output_size / self.original_size) * 100
        return 0.0


class PDFOperationBase(ABC):
    def __init__(self, input_path: Path):
        self.input_path = input_path

    @abstractmethod
    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        pass

    @staticmethod
    def parse_page_ranges(
            page_spec: str,
            total_pages: int
    ) -> List[List[int]]:
        pages = []
        for part in page_spec.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                pages.append(list(range(start - 1, end)))
            else:
                pages.append([int(part) - 1])
        return pages

    @staticmethod
    def validate_pdf(path: Path) -> bool:
        if not path.exists() or path.suffix.lower() != '.pdf':
            return False
        if path.stat().st_size == 0:
            return False
        return True
