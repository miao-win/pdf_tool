from pathlib import Path
from typing import List, Optional

from . import PDFOperationBase, PDFOperationResult
from utils.log_helper import get_logger

logger = get_logger(__name__)


class ToPDFConverter:
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp'}
    WORD_EXTENSIONS = {'.docx', '.doc'}
    PPT_EXTENSIONS = {'.pptx', '.ppt'}

    def __init__(self, input_paths: List[Path] = None):
        self.input_paths = input_paths or []

    @staticmethod
    def detect_format(paths: List[Path]) -> str:
        if not paths:
            return 'unknown'

        exts = {p.suffix.lower() for p in paths}
        if exts <= ToPDFConverter.IMAGE_EXTENSIONS:
            return 'images'
        elif exts <= ToPDFConverter.WORD_EXTENSIONS:
            return 'word'
        elif exts <= ToPDFConverter.PPT_EXTENSIONS:
            return 'ppt'
        else:
            return 'unknown'

    def convert_images(
            self,
            output_dir: Path,
            output_name: Optional[str] = None,
            dpi: int = 150
    ) -> PDFOperationResult:
        try:
            from PIL import Image as PILImage
        except ImportError:
            return PDFOperationResult(success=False, error_message='Pillow 未安装')

        if not self.input_paths:
            return PDFOperationResult(success=False, error_message='没有输入文件')

        try:
            images = []
            for path in self.input_paths:
                if path.suffix.lower() not in self.IMAGE_EXTENSIONS:
                    logger.warning("Skipping non-image file: %s", path)
                    continue
                img = PILImage.open(str(path))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)

            if not images:
                return PDFOperationResult(success=False, error_message='没有有效的图片文件')

            base_name = output_name if output_name else self.input_paths[0].stem
            output_path = output_dir / f'{base_name}.pdf'

            first = images[0]
            rest = images[1:] if len(images) > 1 else []
            first.save(
                str(output_path),
                'PDF',
                resolution=dpi,
                save_all=True,
                append_images=rest
            )

            return PDFOperationResult(
                success=True,
                output_paths=[output_path],
                original_size=sum(p.stat().st_size for p in self.input_paths),
                output_size=output_path.stat().st_size
            )

        except Exception as e:
            logger.error("Image to PDF conversion failed: %s", e, exc_info=True)
            return PDFOperationResult(success=False, error_message=str(e))

    def convert_word(
            self,
            output_dir: Path,
            output_name: Optional[str] = None
    ) -> PDFOperationResult:
        try:
            import subprocess
            import platform

            if not self.input_paths:
                return PDFOperationResult(success=False, error_message='没有输入文件')

            output_files = []

            for path in self.input_paths:
                if path.suffix.lower() not in self.WORD_EXTENSIONS:
                    logger.warning("Skipping non-Word file: %s", path)
                    continue

                base_name = output_name if output_name else path.stem
                output_path = output_dir / f'{base_name}.pdf'

                try:
                    if platform.system() == 'Windows':
                        self._convert_office_windows(str(path), str(output_path))
                    else:
                        self._convert_office_libreoffice(str(path), str(output_dir))

                    if output_path.exists():
                        output_files.append(output_path)
                    else:
                        logger.warning("Output file not created: %s", output_path)

                except Exception as e:
                    logger.warning("Failed to convert %s: %s", path, e)
                    continue

            if not output_files:
                return PDFOperationResult(
                    success=False,
                    error_message='转换失败，请确保已安装 Microsoft Office 或 LibreOffice'
                )

            return PDFOperationResult(
                success=True,
                output_paths=output_files,
                original_size=sum(p.stat().st_size for p in self.input_paths),
                output_size=sum(p.stat().st_size for p in output_files)
            )

        except Exception as e:
            logger.error("Word to PDF conversion failed: %s", e, exc_info=True)
            return PDFOperationResult(success=False, error_message=str(e))

    def convert_ppt(
            self,
            output_dir: Path,
            output_name: Optional[str] = None
    ) -> PDFOperationResult:
        try:
            import subprocess
            import platform

            if not self.input_paths:
                return PDFOperationResult(success=False, error_message='没有输入文件')

            output_files = []

            for path in self.input_paths:
                if path.suffix.lower() not in self.PPT_EXTENSIONS:
                    logger.warning("Skipping non-PPT file: %s", path)
                    continue

                base_name = output_name if output_name else path.stem
                output_path = output_dir / f'{base_name}.pdf'

                try:
                    if platform.system() == 'Windows':
                        self._convert_office_windows(str(path), str(output_path))
                    else:
                        self._convert_office_libreoffice(str(path), str(output_dir))

                    if output_path.exists():
                        output_files.append(output_path)
                    else:
                        logger.warning("Output file not created: %s", output_path)

                except Exception as e:
                    logger.warning("Failed to convert %s: %s", path, e)
                    continue

            if not output_files:
                return PDFOperationResult(
                    success=False,
                    error_message='转换失败，请确保已安装 Microsoft Office 或 LibreOffice'
                )

            return PDFOperationResult(
                success=True,
                output_paths=output_files,
                original_size=sum(p.stat().st_size for p in self.input_paths),
                output_size=sum(p.stat().st_size for p in output_files)
            )

        except Exception as e:
            logger.error("PPT to PDF conversion failed: %s", e, exc_info=True)
            return PDFOperationResult(success=False, error_message=str(e))

    def _convert_office_windows(self, input_path: str, output_path: str):
        import subprocess
        try:
            import win32com.client
            import pythoncom

            pythoncom.CoInitialize()

            if input_path.lower().endswith(('.docx', '.doc')):
                app = win32com.client.Dispatch('Word.Application')
                doc_type = 17
            elif input_path.lower().endswith(('.pptx', '.ppt')):
                app = win32com.client.Dispatch('PowerPoint.Application')
                doc_type = 32
            else:
                raise ValueError(f'Unsupported file type: {input_path}')

            app.Visible = False

            if input_path.lower().endswith(('.docx', '.doc')):
                doc = app.Documents.Open(input_path)
                doc.SaveAs(output_path, FileFormat=doc_type)
                doc.Close()
            else:
                pres = app.Presentations.Open(input_path)
                pres.SaveAs(output_path, doc_type)
                pres.Close()

            app.Quit()
            pythoncom.CoUninitialize()

        except ImportError:
            logger.info("win32com not available, trying LibreOffice")
            self._convert_office_libreoffice(input_path, str(Path(output_path).parent))

    def _convert_office_libreoffice(self, input_path: str, output_dir: str):
        import subprocess
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f'LibreOffice conversion failed: {result.stderr}')
