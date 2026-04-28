from PySide6.QtCore import QThread, Signal

from utils.log_helper import get_logger

logger = get_logger(__name__)


class BaseWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool, object)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False

    def run(self):
        raise NotImplementedError('Subclasses must implement run()')

    def cancel(self):
        self._is_cancelled = True
        self.cancelled.emit()


class OperationWorker(BaseWorker):
    def __init__(self, operation, method_name: str, method_kwargs: dict = None, parent=None):
        super().__init__(parent)
        self._operation = operation
        self._method_name = method_name
        self._method_kwargs = method_kwargs or {}

    def run(self):
        try:
            method = getattr(self._operation, self._method_name)
            self.status.emit(f'正在执行 {self._method_name}...')
            result = method(**self._method_kwargs)
            self.finished.emit(result.success, result)
        except Exception as e:
            logger.error("OperationWorker error in %s: %s", self._method_name, e, exc_info=True)
            self.finished.emit(False, str(e))
