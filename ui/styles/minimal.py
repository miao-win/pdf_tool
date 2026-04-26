"""
简约风主题 QSS 字符串常量
主背景 #FAFAFA，卡片 #FFFFFF，侧边栏 #F2F2F4
主/次文字 #1F2328/#57606A，强调 #2E6BE6
"""

MINIMAL_QSS = """
QMainWindow {
    background-color: #FAFAFA;
}
QWidget {
    background-color: #FAFAFA;
    color: #1F2328;
    font-family: "Inter", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}
QWidget#card {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
}
QWidget#contentArea {
    background-color: transparent;
}
QWidget#sidebar {
    background-color: #F2F2F4;
    border-right: 1px solid #E5E7EB;
}
QWidget#titleBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
}
QWidget#statusBar {
    background-color: #F2F2F4;
    border-top: 1px solid #E5E7EB;
}
QLabel {
    background-color: transparent;
    color: #1F2328;
}
QLabel#title {
    font-size: 20px;
    font-weight: 600;
    color: #1F2328;
}
QLabel#subtitle {
    font-size: 15px;
    color: #57606A;
}
QLabel#caption {
    font-size: 12px;
    color: #57606A;
}
QPushButton {
    background-color: #F3F4F6;
    color: #1F2328;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #E5E7EB;
}
QPushButton:pressed {
    background-color: #D1D5DB;
}
QPushButton#primaryBtn {
    background-color: #2E6BE6;
    color: #FFFFFF;
    border: none;
}
QPushButton#primaryBtn:hover {
    background-color: #1D5ED8;
}
QPushButton#primaryBtn:pressed {
    background-color: #1A4DB5;
}
QPushButton#dangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    border: none;
}
QPushButton#dangerBtn:hover {
    background-color: #B91C1C;
}
QPushButton#textBtn {
    background-color: transparent;
    border: none;
    color: #2E6BE6;
}
QPushButton#textBtn:hover {
    background-color: rgba(46, 107, 230, 0.08);
}
QLineEdit {
    background-color: #FFFFFF;
    color: #1F2328;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}
QLineEdit:focus {
    border: 2px solid #2E6BE6;
}
QComboBox {
    background-color: #FFFFFF;
    color: #1F2328;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}
QComboBox:focus {
    border: 2px solid #2E6BE6;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QProgressBar {
    background-color: #E5E7EB;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    font-size: 12px;
}
QProgressBar::chunk {
    background-color: #2E6BE6;
    border-radius: 4px;
}
QScrollBar:vertical {
    background-color: #F2F2F4;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #D1D5DB;
    border-radius: 4px;
    min-height: 32px;
}
QScrollBar::handle:vertical:hover {
    background-color: #9CA3AF;
}
QScrollBar:horizontal {
    background-color: #F2F2F4;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #D1D5DB;
    border-radius: 4px;
    min-width: 32px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #9CA3AF;
}
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    margin-top: 8px;
    padding-top: 8px;
    font-size: 13px;
    font-weight: 500;
}
QGroupBox::title {
    color: #1F2328;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    border-radius: 6px;
    padding: 8px;
    margin: 2px 4px;
}
QListWidget::item:selected {
    background-color: rgba(46, 107, 230, 0.1);
    color: #1F2328;
}
QListWidget::item:hover {
    background-color: #F3F4F6;
}
QSlider::groove:horizontal {
    height: 4px;
    background-color: #E5E7EB;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 16px;
    height: 16px;
    background-color: #2E6BE6;
    border-radius: 8px;
    margin: -6px 0;
}
QSlider::sub-page:horizontal {
    background-color: #2E6BE6;
    border-radius: 2px;
}
QCheckBox {
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #D1D5DB;
    border-radius: 4px;
    background-color: #FFFFFF;
}
QCheckBox::indicator:checked {
    background-color: #2E6BE6;
    border-color: #2E6BE6;
}
QLabel#previewPlaceholder {
    color: #9CA3AF;
    font-size: 14px;
}
QWidget#previewNavBar {
    background-color: #FFFFFF;
    border-top: 1px solid #E5E7EB;
}
QPushButton#navBtn {
    background-color: #F3F4F6;
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 14px;
    min-width: 32px;
}
QPushButton#navBtn:hover {
    background-color: #E5E7EB;
}
QPushButton#navBtn:disabled {
    background-color: #F9FAFB;
    color: #D1D5DB;
    border-color: #E5E7EB;
}
QLabel#previewPageLabel {
    color: #57606A;
    font-size: 13px;
    font-weight: 500;
}
QSpinBox#previewPageSpin {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 13px;
}
QSpinBox#previewPageSpin:focus {
    border: 2px solid #2E6BE6;
}
QScrollArea#previewScrollArea {
    background-color: #F9FAFB;
    border: none;
}
QToolTip {
    background-color: #1F2328;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""
