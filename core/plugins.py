from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from dataclasses import dataclass


@dataclass
class PDFOperationResult:
    success: bool
    output_paths: List[Path] = None
    error_message: str = None
    original_size: int = 0
    output_size: int = 0


class PDFOperationPlugin(ABC):
    plugin_name: str = None
    plugin_description: str = None

    def __init__(self, input_path: Path):
        self.input_path = input_path

    @abstractmethod
    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass


class RotatePlugin(PDFOperationPlugin):
    plugin_name = 'rotate'
    plugin_description = '旋转 PDF 页面'

    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        from pypdf import PdfReader, PdfWriter

        angle = kwargs.get('angle', 90)
        pages = kwargs.get('pages', None)

        try:
            reader = PdfReader(str(self.input_path))
            writer = PdfWriter()

            for idx, page in enumerate(reader.pages):
                if pages is None or idx in pages:
                    page.rotate(angle)
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

    def validate(self) -> bool:
        return self.input_path.exists() and self.input_path.suffix.lower() == '.pdf'


class PDFToImagesPlugin(PDFOperationPlugin):
    plugin_name = 'pdf_to_images'
    plugin_description = '将 PDF 转换为图片'

    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        import fitz

        fmt = kwargs.get('format', 'png')
        dpi = kwargs.get('dpi', 150)

        try:
            doc = fitz.open(str(self.input_path))
            output_paths = []

            for page_num in range(doc.page_count):
                page = doc[page_num]
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat)

                output_path = output_dir / f'{self.input_path.stem}_page{page_num + 1}.{fmt}'
                pix.save(str(output_path))
                output_paths.append(output_path)

            doc.close()

            return PDFOperationResult(
                success=True,
                output_paths=output_paths
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=str(e))

    def validate(self) -> bool:
        return self.input_path.exists() and self.input_path.suffix.lower() == '.pdf'


class ImagesToPDFPlugin(PDFOperationPlugin):
    plugin_name = 'images_to_pdf'
    plugin_description = '将图片合成为 PDF'

    def __init__(self, input_paths: List[Path]):
        self.input_paths = input_paths
        self.input_path = input_paths[0] if input_paths else Path('')

    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        from PIL import Image
        from pypdf import PdfWriter

        try:
            writer = PdfWriter()
            output_path = output_dir / 'merged.pdf'

            for img_path in self.input_paths:
                with Image.open(img_path) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    pdf_img_path = output_dir / f'{img_path.stem}_temp.pdf'
                    img.save(pdf_img_path, 'PDF', resolution=kwargs.get('dpi', 150))

                    from pypdf import PdfReader
                    reader = PdfReader(pdf_img_path)
                    for page in reader.pages:
                        writer.add_page(page)

                    pdf_img_path.unlink()

            with open(output_path, 'wb') as f:
                writer.write(f)

            return PDFOperationResult(
                success=True,
                output_paths=[output_path]
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=str(e))

    def validate(self) -> bool:
        if not self.input_paths:
            return False
        return all(p.exists() and p.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'] for p in self.input_paths)


class PasswordPlugin(PDFOperationPlugin):
    plugin_name = 'password'
    plugin_description = '添加或移除 PDF 密码'

    def execute(self, output_dir: Path, **kwargs) -> PDFOperationResult:
        from pikepdf import Pdf, Permissions

        action = kwargs.get('action', 'add')
        password = kwargs.get('password', '')

        try:
            with Pdf.open(self.input_path) as pdf:
                if action == 'add':
                    output_path = output_dir / f'{self.input_path.stem}_protected.pdf'
                    pdf.save(
                        output_path,
                        encryption=kwargs.get('encryption', Pdf.open(self.input_path).encryption),
                        user_password=password,
                        owner_password=kwargs.get('owner_password', password)
                    )
                else:
                    output_path = output_dir / f'{self.input_path.stem}_unlocked.pdf'
                    pdf.save(output_path)

            return PDFOperationResult(
                success=True,
                output_paths=[output_path]
            )
        except Exception as e:
            return PDFOperationResult(success=False, error_message=str(e))

    def validate(self) -> bool:
        return self.input_path.exists() and self.input_path.suffix.lower() == '.pdf'


class PluginRegistry:
    _plugins = {
        'rotate': RotatePlugin,
        'pdf_to_images': PDFToImagesPlugin,
        'images_to_pdf': ImagesToPDFPlugin,
        'password': PasswordPlugin,
    }

    @classmethod
    def register(cls, name: str, plugin_class: type):
        cls._plugins[name] = plugin_class

    @classmethod
    def get_plugin(cls, name: str):
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls):
        return {name: cls._plugins[name].plugin_description for name in cls._plugins}
