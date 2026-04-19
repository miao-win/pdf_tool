from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QIcon


class Dialogs:
    @staticmethod
    def show_error(parent: QWidget, title: str, message: str):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    @staticmethod
    def show_success(parent: QWidget, title: str, message: str):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    @staticmethod
    def show_confirmation(parent: QWidget, title: str, message: str) -> bool:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        return msg_box.exec() == QMessageBox.StandardButton.Ok

    @staticmethod
    def show_info(parent: QWidget, title: str, message: str):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
