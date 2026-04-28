from pathlib import Path
from typing import Optional

from core.page_editor import PageEditorOperation
from . import BaseWorker
from utils.log_helper import get_logger

logger = get_logger(__name__)


class PageEditorWorker(BaseWorker):
    def __init__(
            self,
            input_path: Path,
            output_dir: Path,
            operation_type: str,
            angle: Optional[int] = None,
            page_spec: Optional[str] = None,
            clockwise: bool = True,
            operation: PageEditorOperation = None,
            parent=None
    ):
        super().__init__(parent)
        self.input_path = input_path
        self.output_dir = output_dir
        self.operation_type = operation_type
        self.angle = angle
        self.page_spec = page_spec
        self.clockwise = clockwise
        self._operation = operation

    def run(self):
        try:
            self.status.emit('正在处理页面...')
            editor = self._operation or PageEditorOperation(self.input_path)

            if self.operation_type == 'rotate':
                self.status.emit('正在旋转页面...')
                result = editor.rotate_pages(
                    self.output_dir,
                    self.angle,
                    self.page_spec,
                    self.clockwise
                )
            elif self.operation_type == 'delete':
                self.status.emit('正在删除页面...')
                result = editor.delete_pages(
                    self.output_dir,
                    self.page_spec
                )
            else:
                self.finished.emit(False, '未知操作')
                return

            self.finished.emit(result.success, result)

        except Exception as e:
            logger.error("PageEditorWorker error: %s", e, exc_info=True)
            self.finished.emit(False, str(e))
