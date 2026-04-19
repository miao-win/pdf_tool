from PySide6.QtCore import QThread, Signal


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
