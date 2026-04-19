from pathlib import Path
from typing import List, Optional

from core.to_pdf import ToPDFConverter
from . import BaseWorker


class ToPDFWorker(BaseWorker):
    def __init__(
            self,
            input_paths: List[Path],
            output_dir: Path,
            source_type: str,
            output_name: Optional[str] = None,
            dpi: int = 150,
            parent=None
    ):
        super().__init__(parent)
        self.input_paths = input_paths
        self.output_dir = output_dir
        self.source_type = source_type
        self.output_name = output_name
        self.dpi = dpi

    def run(self):
        try:
            self.status.emit('正在转换...')
            self.progress.emit(10)

            converter = ToPDFConverter(self.input_paths)
            self.progress.emit(30)

            if self.source_type == 'images':
                self.status.emit('正在将图片合成为 PDF...')
                result = converter.convert_images(
                    self.output_dir,
                    self.output_name,
                    self.dpi
                )
            elif self.source_type == 'word':
                self.status.emit('正在将 Word 转换为 PDF...')
                result = converter.convert_word(
                    self.output_dir,
                    self.output_name
                )
            elif self.source_type == 'ppt':
                self.status.emit('正在将 PPT 转换为 PDF...')
                result = converter.convert_ppt(
                    self.output_dir,
                    self.output_name
                )
            else:
                self.finished.emit(False, '未知的文件类型')
                return

            self.progress.emit(100)

            if result.success:
                self.status.emit('转换完成')
            else:
                self.status.emit('转换失败')

            self.finished.emit(result.success, result)

        except Exception as e:
            self.finished.emit(False, str(e))
