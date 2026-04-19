from pathlib import Path
from typing import List, Optional
import subprocess
import sys

from . import PDFOperationResult


class ToPDFConverter:
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp'}
    WORD_EXTENSIONS = {'.docx', '.doc'}
    PPT_EXTENSIONS = {'.pptx', '.ppt'}

    def __init__(self, input_paths: List[Path]):
        self.input_paths = input_paths

    def convert_images(
            self,
            output_dir: Path,
            output_name: Optional[str] = None,
            dpi: int = 150
    ) -> PDFOperationResult:
        from PIL import Image
        from pypdf import PdfWriter

        if not self.input_paths:
            return PDFOperationResult(success=False, error_message='没有选择图片文件')

        for path in self.input_paths:
            if not path.exists():
                return PDFOperationResult(success=False, error_message=f'文件不存在: {path.name}')
            if path.suffix.lower() not in self.IMAGE_EXTENSIONS:
                return PDFOperationResult(
                    success=False,
                    error_message=f'不支持的图片格式: {path.suffix}，支持的格式: PNG, JPG, BMP, TIFF, WebP'
                )

        try:
            writer = PdfWriter()
            temp_pdf_paths = []

            for img_path in self.input_paths:
                with Image.open(img_path) as img:
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')

                    temp_pdf_path = output_dir / f'_temp_{img_path.stem}.pdf'
                    img.save(
                        str(temp_pdf_path),
                        'PDF',
                        resolution=dpi,
                        quality=95
                    )
                    temp_pdf_paths.append(temp_pdf_path)

                    from pypdf import PdfReader
                    reader = PdfReader(temp_pdf_path)
                    for page in reader.pages:
                        writer.add_page(page)

            base_name = output_name if output_name else self.input_paths[0].stem
            output_path = output_dir / f'{base_name}.pdf'

            counter = 1
            while output_path.exists():
                output_path = output_dir / f'{base_name}_{counter}.pdf'
                counter += 1

            with open(output_path, 'wb') as f:
                writer.write(f)

            for temp_path in temp_pdf_paths:
                if temp_path.exists():
                    temp_path.unlink()

            return PDFOperationResult(
                success=True,
                output_paths=[output_path],
                original_size=sum(p.stat().st_size for p in self.input_paths),
                output_size=output_path.stat().st_size
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=f'图片转PDF失败: {str(e)}')

    def convert_word(
            self,
            output_dir: Path,
            output_name: Optional[str] = None
    ) -> PDFOperationResult:
        if not self.input_paths:
            return PDFOperationResult(success=False, error_message='没有选择Word文件')

        for path in self.input_paths:
            if not path.exists():
                return PDFOperationResult(success=False, error_message=f'文件不存在: {path.name}')
            if path.suffix.lower() not in self.WORD_EXTENSIONS:
                return PDFOperationResult(
                    success=False,
                    error_message=f'不支持的Word格式: {path.suffix}，支持的格式: DOCX, DOC'
                )

        base_name = output_name if output_name else self.input_paths[0].stem
        output_path = output_dir / f'{base_name}.pdf'

        counter = 1
        while output_path.exists():
            output_path = output_dir / f'{base_name}_{counter}.pdf'
            counter += 1

        try:
            if sys.platform == 'win32':
                return self._convert_word_com(path, output_dir, output_path)
            else:
                return self._convert_word_libreoffice(path, output_dir, output_path)
        except Exception as e:
            return PDFOperationResult(success=False, error_message=f'Word转PDF失败: {str(e)}')

    def _convert_word_com(self, input_path: Path, output_dir: Path, output_path: Path) -> PDFOperationResult:
        try:
            import docx2pdf
            docx2pdf.convert(str(input_path), str(output_path))
            if output_path.exists():
                return PDFOperationResult(
                    success=True,
                    output_paths=[output_path],
                    original_size=input_path.stat().st_size,
                    output_size=output_path.stat().st_size
                )
            else:
                return PDFOperationResult(success=False, error_message='转换后未找到输出文件')
        except ImportError:
            return PDFOperationResult(
                success=False,
                error_message='docx2pdf 未安装。请运行: pip install docx2pdf\n或者使用支持COM的Microsoft Word/WPS'
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=f'COM调用失败: {str(e)}')

    def _convert_word_libreoffice(self, input_path: Path, output_dir: Path, output_path: Path) -> PDFOperationResult:
        try:
            result = subprocess.run(
                ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', str(output_dir), str(input_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                expected = output_dir / f'{input_path.stem}.pdf'
                if expected.exists():
                    if expected != output_path:
                        expected.rename(output_path)
                    return PDFOperationResult(
                        success=True,
                        output_paths=[output_path],
                        original_size=input_path.stat().st_size,
                        output_size=output_path.stat().st_size
                    )
            return PDFOperationResult(success=False, error_message=f'LibreOffice转换失败: {result.stderr}')
        except FileNotFoundError:
            return PDFOperationResult(
                success=False,
                error_message='LibreOffice 未安装。请安装 LibreOffice 或使用 Windows/Mac 上的 Microsoft Word/WPS'
            )
        except subprocess.TimeoutExpired:
            return PDFOperationResult(success=False, error_message='LibreOffice 转换超时')
        except Exception as e:
            return PDFOperationResult(success=False, error_message=f'LibreOffice 转换失败: {str(e)}')

    def convert_ppt(
            self,
            output_dir: Path,
            output_name: Optional[str] = None
    ) -> PDFOperationResult:
        if not self.input_paths:
            return PDFOperationResult(success=False, error_message='没有选择PPT文件')

        for path in self.input_paths:
            if not path.exists():
                return PDFOperationResult(success=False, error_message=f'文件不存在: {path.name}')
            if path.suffix.lower() not in self.PPT_EXTENSIONS:
                return PDFOperationResult(
                    success=False,
                    error_message=f'不支持的PPT格式: {path.suffix}，支持的格式: PPTX, PPT'
                )

        base_name = output_name if output_name else self.input_paths[0].stem
        output_path = output_dir / f'{base_name}.pdf'

        counter = 1
        while output_path.exists():
            output_path = output_dir / f'{base_name}_{counter}.pdf'
            counter += 1

        try:
            if sys.platform == 'win32':
                return self._convert_ppt_com(path, output_dir, output_path)
            else:
                return self._convert_ppt_libreoffice(path, output_dir, output_path)
        except Exception as e:
            return PDFOperationResult(success=False, error_message=f'PPT转PDF失败: {str(e)}')

    def _convert_ppt_com(self, input_path: Path, output_dir: Path, output_path: Path) -> PDFOperationResult:
        try:
            import comtypes.client
            import os

            powerpoint = comtypes.client.CreateObject('Powerpoint.Application')
            powerpoint.Visible = 1

            try:
                deck = powerpoint.Presentations.Open(str(input_path))
                deck.SaveAs(str(output_path), 32)
                deck.Close()
            finally:
                powerpoint.Quit()

            if output_path.exists():
                return PDFOperationResult(
                    success=True,
                    output_paths=[output_path],
                    original_size=input_path.stat().st_size,
                    output_size=output_path.stat().st_size
                )
            else:
                return PDFOperationResult(success=False, error_message='转换后未找到输出文件')
        except ImportError:
            return PDFOperationResult(
                success=False,
                error_message='comtypes 未安装。请运行: pip install comtypes\n或者使用支持COM的Microsoft PowerPoint/WPS'
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=f'COM调用失败: {str(e)}')

    def _convert_ppt_libreoffice(self, input_path: Path, output_dir: Path, output_path: Path) -> PDFOperationResult:
        try:
            result = subprocess.run(
                ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', str(output_dir), str(input_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                expected = output_dir / f'{input_path.stem}.pdf'
                if expected.exists():
                    if expected != output_path:
                        expected.rename(output_path)
                    return PDFOperationResult(
                        success=True,
                        output_paths=[output_path],
                        original_size=input_path.stat().st_size,
                        output_size=output_path.stat().st_size
                    )
            return PDFOperationResult(success=False, error_message=f'LibreOffice转换失败: {result.stderr}')
        except FileNotFoundError:
            return PDFOperationResult(
                success=False,
                error_message='LibreOffice 未安装。请安装 LibreOffice 或使用 Windows/Mac 上的 Microsoft PowerPoint/WPS'
            )
        except subprocess.TimeoutExpired:
            return PDFOperationResult(success=False, error_message='LibreOffice 转换超时')
        except Exception as e:
            return PDFOperationResult(success=False, error_message=f'LibreOffice 转换失败: {str(e)}')

    @staticmethod
    def detect_format(paths: List[Path]) -> str:
        if not paths:
            return 'unknown'

        extensions = {p.suffix.lower() for p in paths}
        image_exts = ToPDFConverter.IMAGE_EXTENSIONS
        word_exts = ToPDFConverter.WORD_EXTENSIONS
        ppt_exts = ToPDFConverter.PPT_EXTENSIONS

        if extensions.issubset(image_exts):
            return 'images'
        elif extensions.issubset(word_exts):
            return 'word'
        elif extensions.issubset(ppt_exts):
            return 'ppt'
        elif extensions.issubset(image_exts | word_exts):
            return 'mixed_image_word'
        else:
            return 'unknown'
