"""
科幻风主题 QSS 字符串常量
主背景 #0A0E14，卡片 #111826，侧边栏 #0D131D
主/次文字 #E2F3FF/#6D8299，强调 #00E5FF，辅色 #FF2E9A
"""

SCIFI_QSS = """
QMainWindow {
    background-color: #0F1923;
}
QWidget {
    background-color: #0F1923;
    color: #E2F3FF;
    font-family: "Rajdhani", "Orbitron", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}
QWidget#card {
    background-color: #162236;
    border-radius: 2px;
    border: 1px solid #1E3450;
}
QWidget#contentArea {
    background-color: transparent;
}
QWidget#sidebar {
    background-color: #121D2B;
    border-right: 1px solid #1E3450;
}
QWidget#titleBar {
    background-color: #162236;
    border-bottom: 1px solid #1E3450;
}
QWidget#statusBar {
    background-color: #121D2B;
    border-top: 1px solid #1E3450;
}
QLabel {
    background-color: transparent;
    color: #E2F3FF;
}
QLabel#title {
    font-size: 20px;
    font-weight: 600;
    color: #E2F3FF;
    font-family: "Orbitron", "Rajdhani", sans-serif;
}
QLabel#subtitle {
    font-size: 15px;
    color: #8FAEC8;
    font-family: "Rajdhani", sans-serif;
}
QLabel#caption {
    font-size: 12px;
    color: #8FAEC8;
    font-family: "Share Tech Mono", monospace;
}
QPushButton {
    background-color: #1A2D44;
    color: #E2F3FF;
    border: 1px solid #1E3A5C;
    border-radius: 2px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    font-family: "Rajdhani", sans-serif;
}
QPushButton:hover {
    background-color: #1E3A5A;
    border-color: #00E5FF;
}
QPushButton:pressed {
    background-color: #142438;
}
QPushButton#primaryBtn {
    background-color: rgba(0, 229, 255, 0.12);
    color: #00E5FF;
    border: 1px solid #00E5FF;
}
QPushButton#primaryBtn:hover {
    background-color: rgba(0, 229, 255, 0.2);
}
QPushButton#primaryBtn:pressed {
    background-color: rgba(0, 229, 255, 0.08);
}
QPushButton#dangerBtn {
    background-color: rgba(255, 46, 154, 0.12);
    color: #FF2E9A;
    border: 1px solid #FF2E9A;
}
QPushButton#dangerBtn:hover {
    background-color: rgba(255, 46, 154, 0.2);
}
QPushButton#textBtn {
    background-color: transparent;
    border: none;
    color: #00E5FF;
}
QPushButton#textBtn:hover {
    background-color: rgba(0, 229, 255, 0.08);
}
QLineEdit {
    background-color: #162236;
    color: #E2F3FF;
    border: 1px solid #1E3A5C;
    border-radius: 2px;
    padding: 8px 12px;
    font-size: 13px;
    font-family: "Share Tech Mono", monospace;
}
QLineEdit:focus {
    border: 1px solid #00E5FF;
}
QComboBox {
    background-color: #162236;
    color: #E2F3FF;
    border: 1px solid #1E3A5C;
    border-radius: 2px;
    padding: 8px 12px;
    font-size: 13px;
}
QComboBox:focus {
    border: 1px solid #00E5FF;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QProgressBar {
    background-color: #1A2D44;
    border: 1px solid #1E3A5C;
    border-radius: 2px;
    height: 8px;
    text-align: center;
    font-size: 12px;
    color: #00E5FF;
    font-family: "Share Tech Mono", monospace;
}
QProgressBar::chunk {
    background-color: #00E5FF;
    border-radius: 1px;
}
QScrollBar:vertical {
    background-color: #121D2B;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background-color: #1E3A5C;
    border-radius: 3px;
    min-height: 32px;
}
QScrollBar::handle:vertical:hover {
    background-color: #00E5FF;
}
QScrollBar:horizontal {
    background-color: #121D2B;
    height: 6px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background-color: #1E3A5C;
    border-radius: 3px;
    min-width: 32px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #00E5FF;
}
QGroupBox {
    background-color: #162236;
    border: 1px solid #1E3450;
    border-radius: 2px;
    margin-top: 8px;
    padding-top: 8px;
    font-size: 13px;
    font-weight: 500;
}
QGroupBox::title {
    color: #E2F3FF;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QListWidget {
    background-color: #162236;
    border: 1px solid #1E3450;
    border-radius: 2px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    border-radius: 2px;
    padding: 8px;
    margin: 2px 4px;
}
QListWidget::item:selected {
    background-color: rgba(0, 229, 255, 0.08);
    color: #00E5FF;
    border: 1px solid rgba(0, 229, 255, 0.3);
}
QListWidget::item:hover {
    background-color: #1A2D44;
}
QSlider::groove:horizontal {
    height: 4px;
    background-color: #1A2D44;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 14px;
    height: 14px;
    background-color: #00E5FF;
    border-radius: 2px;
    margin: -5px 0;
}
QSlider::sub-page:horizontal {
    background-color: #00E5FF;
    border-radius: 2px;
}
QCheckBox {
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #1E3A5C;
    border-radius: 2px;
    background-color: #162236;
}
QCheckBox::indicator:checked {
    background-color: rgba(0, 229, 255, 0.15);
    border-color: #00E5FF;
}
QLabel#previewPlaceholder {
    color: #3A5A7C;
    font-size: 14px;
}
QWidget#previewNavBar {
    background-color: #111826;
    border-top: 1px solid #1E3450;
}
QPushButton#navBtn {
    background-color: #1A2D44;
    border: 1px solid #1E3A5C;
    border-radius: 2px;
    padding: 4px 8px;
    font-size: 14px;
    min-width: 32px;
    color: #00E5FF;
}
QPushButton#navBtn:hover {
    background-color: #1E3A5A;
    border-color: #00E5FF;
}
QPushButton#navBtn:disabled {
    background-color: #0F1923;
    color: #1E3A5C;
    border-color: #1E3450;
}
QLabel#previewPageLabel {
    color: #6D8299;
    font-size: 13px;
    font-weight: 500;
    font-family: "Share Tech Mono", monospace;
}
QSpinBox#previewPageSpin {
    background-color: #162236;
    border: 1px solid #1E3A5C;
    border-radius: 2px;
    padding: 2px 4px;
    font-size: 13px;
    color: #00E5FF;
    font-family: "Share Tech Mono", monospace;
}
QSpinBox#previewPageSpin:focus {
    border: 1px solid #00E5FF;
}
QScrollArea#previewScrollArea {
    background-color: #0A0E14;
    border: none;
}
QToolTip {
    background-color: #162236;
    color: #00E5FF;
    border: 1px solid #00E5FF;
    border-radius: 2px;
    padding: 6px 10px;
    font-size: 12px;
    font-family: "Share Tech Mono", monospace;
}
"""
