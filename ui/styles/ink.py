"""
水墨风主题 QSS 字符串常量
主背景 #F4EEDF，卡片 #FBF6E9，侧边栏 #EBE3CF
主/次文字 #1C1B1A/#5C5650，强调 #8B2B2B，辅色 #3E5E5A
"""

INK_QSS = """
QMainWindow {
    background-color: #F4EEDF;
}
QWidget {
    background-color: #F4EEDF;
    color: #1C1B1A;
    font-family: "LXGW WenKai", "Noto Serif SC", "PingFang SC", "Microsoft YaHei", serif;
    font-size: 13px;
}
QWidget#card {
    background-color: #FBF6E9;
    border-radius: 4px;
    border: 1px solid #D4C9B0;
}
QWidget#contentArea {
    background-color: transparent;
}
QWidget#sidebar {
    background-color: #EBE3CF;
    border-right: 1px solid #D4C9B0;
}
QWidget#titleBar {
    background-color: #FBF6E9;
    border-bottom: 1px solid #D4C9B0;
}
QWidget#statusBar {
    background-color: #EBE3CF;
    border-top: 1px solid #D4C9B0;
}
QLabel {
    background-color: transparent;
    color: #1C1B1A;
}
QLabel#title {
    font-size: 20px;
    font-weight: 600;
    color: #1C1B1A;
}
QLabel#subtitle {
    font-size: 15px;
    color: #5C5650;
}
QLabel#caption {
    font-size: 12px;
    color: #5C5650;
}
QPushButton {
    background-color: #F0E9D8;
    color: #1C1B1A;
    border: 1px solid #C4B9A0;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #E8DFC8;
}
QPushButton:pressed {
    background-color: #D4C9B0;
}
QPushButton#primaryBtn {
    background-color: #8B2B2B;
    color: #FFFFFF;
    border: none;
}
QPushButton#primaryBtn:hover {
    background-color: #7A2525;
}
QPushButton#primaryBtn:pressed {
    background-color: #691F1F;
}
QPushButton#dangerBtn {
    background-color: #8B2B2B;
    color: #FFFFFF;
    border: none;
}
QPushButton#dangerBtn:hover {
    background-color: #7A2525;
}
QPushButton#textBtn {
    background-color: transparent;
    border: none;
    color: #3E5E5A;
}
QPushButton#textBtn:hover {
    background-color: rgba(62, 94, 90, 0.08);
}
QLineEdit {
    background-color: #FBF6E9;
    color: #1C1B1A;
    border: none;
    border-bottom: 2px solid #B8A88A;
    border-radius: 0px;
    padding: 8px 4px;
    font-size: 13px;
}
QLineEdit:focus {
    border-bottom: 2px solid #8B2B2B;
}
QComboBox {
    background-color: #FBF6E9;
    color: #1C1B1A;
    border: none;
    border-bottom: 2px solid #B8A88A;
    border-radius: 0px;
    padding: 8px 4px;
    font-size: 13px;
}
QComboBox:focus {
    border-bottom: 2px solid #8B2B2B;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QProgressBar {
    background-color: #E0D5C0;
    border: none;
    border-radius: 2px;
    height: 6px;
    text-align: center;
    font-size: 12px;
    color: #1C1B1A;
}
QProgressBar::chunk {
    background-color: #8B2B2B;
    border-radius: 2px;
}
QScrollBar:vertical {
    background-color: #EBE3CF;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background-color: #C4B9A0;
    border-radius: 3px;
    min-height: 32px;
}
QScrollBar::handle:vertical:hover {
    background-color: #A89B80;
}
QScrollBar:horizontal {
    background-color: #EBE3CF;
    height: 6px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background-color: #C4B9A0;
    border-radius: 3px;
    min-width: 32px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #A89B80;
}
QGroupBox {
    background-color: #FBF6E9;
    border: 1px solid #D4C9B0;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
    font-size: 13px;
    font-weight: 500;
}
QGroupBox::title {
    color: #1C1B1A;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QListWidget {
    background-color: #FBF6E9;
    border: 1px solid #D4C9B0;
    border-radius: 4px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    border-radius: 2px;
    padding: 8px;
    margin: 2px 4px;
}
QListWidget::item:selected {
    background-color: rgba(139, 43, 43, 0.08);
    color: #1C1B1A;
}
QListWidget::item:hover {
    background-color: #F0E9D8;
}
QSlider::groove:horizontal {
    height: 4px;
    background-color: #E0D5C0;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 14px;
    height: 14px;
    background-color: #8B2B2B;
    border-radius: 7px;
    margin: -5px 0;
}
QSlider::sub-page:horizontal {
    background-color: #8B2B2B;
    border-radius: 2px;
}
QCheckBox {
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #B8A88A;
    border-radius: 2px;
    background-color: #FBF6E9;
}
QCheckBox::indicator:checked {
    background-color: #8B2B2B;
    border-color: #8B2B2B;
}
QToolTip {
    background-color: #1C1B1A;
    color: #F4EEDF;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}
"""
