"""
主窗口：标题栏+侧边栏+内容区+状态栏
三主题一键切换，全部自绘
"""
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QFrame, QSizePolicy, QApplication, QGraphicsOpacityEffect,
    QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QLinearGradient

from utils.theme_manager import get_theme_manager, apply_theme_to_widget
from ui.widgets.icon import IconWidget
from ui.widgets.painters import CinnabarSeal, CornerMarks, NeonProgressBar
from ui.widgets.textures import RicePaperTexture, SciFiGridTexture, MinimalTexture


class TitleBar(QFrame):
    """自定义标题栏 44px"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setObjectName('titleBar')
        self.theme = 'minimal'
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # Logo
        self.logo_widget = QWidget(self)
        self.logo_widget.setFixedSize(28, 28)
        self.logo_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.logo_widget.setAutoFillBackground(False)
        layout.addWidget(self.logo_widget)

        self.title_label = QLabel('PDF 工具箱')
        self.title_label.setObjectName('title')
        layout.addWidget(self.title_label)

        layout.addStretch()

        # 主题切换按钮
        self.theme_btn = QWidget(self)
        self.theme_btn.setFixedSize(28, 28)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.theme_btn.setAutoFillBackground(False)
        layout.addWidget(self.theme_btn)

        # 窗口控制按钮
        self.min_btn = QWidget(self)
        self.min_btn.setFixedSize(28, 28)
        self.min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.min_btn.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.min_btn.setAutoFillBackground(False)
        layout.addWidget(self.min_btn)

        self.max_btn = QWidget(self)
        self.max_btn.setFixedSize(28, 28)
        self.max_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.max_btn.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.max_btn.setAutoFillBackground(False)
        layout.addWidget(self.max_btn)

        self.close_btn = QWidget(self)
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.close_btn.setAutoFillBackground(False)
        layout.addWidget(self.close_btn)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制 Logo
        if self.theme == 'ink':
            seal = CinnabarSeal('工', 24)
            seal.set_theme('ink')
            seal.render(p, QPoint(2, 10))
        elif self.theme == 'scifi':
            # 六边形 + PDF
            cx, cy = 14, 22
            r = 10
            path = QPainterPath()
            for i in range(6):
                angle = (i * 60 - 30) * 3.14159 / 180
                x = cx + r * (1 if angle > -1.57 and angle < 1.57 else -1) * abs(0.866 if abs(angle) > 0.1 else 1)
                y = cy + r * (1 if angle > 0 else -1) * abs(0.5 if abs(abs(angle) - 1.57) < 0.1 else 1)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            pen = QPen(QColor('#00E5FF'), 1.5)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)
            font = QFont("Orbitron", 7)
            p.setFont(font)
            p.setPen(QColor('#00E5FF'))
            p.drawText(6, 26, 'PDF')
        else:
            # 简约：圆角方块+蓝线
            pen = QPen(QColor('#2E6BE6'), 2)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(4, 10, 20, 20, 4, 4)
            p.drawLine(8, 18, 20, 18)

        # 绘制主题切换按钮
        btn_x = self.width() - 112
        if self.theme == 'ink':
            p.setPen(QPen(QColor('#8B2B2B'), 2))
            p.setBrush(QColor('#8B2B2B') if self.theme == 'ink' else Qt.BrushStyle.NoBrush)
            p.drawEllipse(btn_x + 8, 10, 12, 12)
        elif self.theme == 'scifi':
            cx = btn_x + 14
            cy = 22
            r = 8
            path = QPainterPath()
            for i in range(6):
                angle = (i * 60 - 30) * 3.14159 / 180
                x = cx + r * (1 if angle > -1.57 and angle < 1.57 else -1) * abs(0.866 if abs(angle) > 0.1 else 1)
                y = cy + r * (1 if angle > 0 else -1) * abs(0.5 if abs(abs(angle) - 1.57) < 0.1 else 1)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            p.setPen(QPen(QColor('#00E5FF'), 1.5))
            p.setBrush(QColor(0, 229, 255, 40))
            p.drawPath(path)
        else:
            p.setPen(QPen(QColor('#2E6BE6'), 2))
            p.setBrush(QColor('#2E6BE6'))
            p.drawRoundedRect(btn_x + 6, 10, 16, 16, 3, 3)

        # 最小化按钮
        p.setPen(QPen(QColor('#57606A' if self.theme == 'minimal' else '#5C5650' if self.theme == 'ink' else '#8FAEC8'), 2))
        p.drawLine(self.width() - 80, 22, self.width() - 64, 22)

        # 最大化按钮
        p.setPen(QPen(QColor('#57606A' if self.theme == 'minimal' else '#5C5650' if self.theme == 'ink' else '#8FAEC8'), 2))
        p.drawRect(self.width() - 52, 14, 12, 12)

        # 关闭按钮
        p.setPen(QPen(QColor('#DC2626' if self.theme == 'minimal' else '#8B2B2B' if self.theme == 'ink' else '#FF2E9A'), 2))
        p.drawLine(self.width() - 28, 14, self.width() - 12, 30)
        p.drawLine(self.width() - 12, 14, self.width() - 28, 30)


class SidebarItem(QFrame):
    """侧边栏项目"""
    clicked = Signal(str)

    def __init__(self, icon_name: str, text: str, item_id: str, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.text = text
        self.icon_name = icon_name
        self.theme = 'minimal'
        self._selected = False
        self._hovered = False
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit(self.item_id)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        if self.theme == 'minimal':
            if self._selected:
                p.fillRect(0, 0, 3, h, QColor('#2E6BE6'))
                p.fillRect(3, 0, w-3, h, QColor(46, 107, 230, 8))
            elif self._hovered:
                p.fillRect(0, 0, w, h, QColor(0, 0, 0, 5))
        elif self.theme == 'ink':
            if self._selected:
                p.setBrush(QColor('#8B2B2B'))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(16, h//2 - 5, 10, 10)
                p.setPen(QColor('#8B2B2B'))
                font = QFont("LXGW WenKai", 13)
                font.setBold(True)
                p.setFont(font)
            elif self._hovered:
                # 墨线波浪
                pen = QPen(QColor('#B8A88A'), 1)
                pen.setCapStyle(Qt.PenCapStyle.FlatCap)
                p.setPen(pen)
                for i in range(3):
                    y = h//2 - 4 + i * 4
                    p.drawLine(40, y, w - 12, y)
            p.setPen(QColor('#1C1B1A'))
        elif self.theme == 'scifi':
            if self._selected:
                p.fillRect(0, 0, 3, h, QColor('#00E5FF'))
                glow = QPen(QColor(0, 229, 255, 60), 4)
                p.setPen(glow)
                p.drawLine(0, 0, 0, h)
                p.setPen(QColor('#00E5FF'))
                font = QFont("Rajdhani", 13)
                font.setBold(True)
                p.setFont(font)
                # ▸ 符号
                p.drawText(w - 20, h//2 + 5, '▸')
            elif self._hovered:
                p.fillRect(0, 0, w, h, QColor(0, 229, 255, 8))
            p.setPen(QColor('#E2F3FF'))

        # 图标
        icon = IconWidget(self.icon_name, 20, self.theme)
        icon.render(p, QPoint(16, h//2 - 10))

        # 文字
        if not getattr(self.parent(), '_collapsed', False):
            font = QFont()
            font.setPointSize(13)
            p.setFont(font)
            text_color = QColor('#1F2328' if self.theme == 'minimal' else '#1C1B1A' if self.theme == 'ink' else '#E2F3FF')
            if self.theme == 'ink' and self._selected:
                text_color = QColor('#8B2B2B')
            elif self.theme == 'scifi' and self._selected:
                text_color = QColor('#00E5FF')
            p.setPen(text_color)
            p.drawText(48, h//2 + 5, self.text)


class Sidebar(QFrame):
    """侧边栏 220px"""
    item_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('sidebar')
        self.setFixedWidth(220)
        self.theme = 'minimal'
        self._collapsed = False
        self._items = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)

        items = [
            ('home', '主页', 'home'),
            ('split', '拆分 PDF', 'split'),
            ('merge', '合并 PDF', 'merge'),
            ('compress', '压缩 PDF', 'compress'),
            ('edit', '页面编辑', 'page_editor'),
            ('pdf_to_image', 'PDF 转图片', 'pdf_to_image'),
            ('to_pdf', '转为 PDF', 'to_pdf'),
        ]

        for icon_name, text, item_id in items:
            item = SidebarItem(icon_name, text, item_id)
            item.clicked.connect(self.item_clicked.emit)
            layout.addWidget(item)
            self._items[item_id] = item

        layout.addStretch()

        self.theme_btn = QPushButton('切换主题')
        self.theme_btn.setObjectName('textBtn')
        self.theme_btn.setFixedHeight(36)
        layout.addWidget(self.theme_btn)

        # 设置项
        settings_item = SidebarItem('settings', '设置', 'settings')
        settings_item.clicked.connect(self.item_clicked.emit)
        layout.addWidget(settings_item)
        self._items['settings'] = settings_item

    def set_theme(self, theme: str):
        self.theme = theme
        for item in self._items.values():
            item.set_theme(theme)
        self.update()

    def set_selected(self, item_id: str):
        for id_, item in self._items.items():
            item.set_selected(id_ == item_id)

    def set_collapsed(self, collapsed: bool):
        self._collapsed = collapsed
        self.setFixedWidth(56 if collapsed else 220)
        for item in self._items.values():
            item.update()


class ContentArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('contentArea')
        self.theme = 'minimal'
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def add_page(self, widget, name: str):
        self.stack.addWidget(widget)

    def set_page(self, index: int):
        current = self.stack.currentWidget()
        if current:
            effect_out = QGraphicsOpacityEffect(current)
            current.setGraphicsEffect(effect_out)
            self._anim_out = QPropertyAnimation(effect_out, b'opacity')
            self._anim_out.setDuration(100)
            self._anim_out.setStartValue(1.0)
            self._anim_out.setEndValue(0.0)
            self._anim_out.start()

        self.stack.setCurrentIndex(index)

        new_widget = self.stack.currentWidget()
        if new_widget:
            if hasattr(new_widget, 'reset'):
                new_widget.reset()
            effect_in = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(effect_in)
            effect_in.setOpacity(0.0)
            self._anim_in = QPropertyAnimation(effect_in, b'opacity')
            self._anim_in.setDuration(150)
            self._anim_in.setStartValue(0.0)
            self._anim_in.setEndValue(1.0)
            self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim_in.start()


class StatusBar(QFrame):
    """状态栏 28px"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setObjectName('statusBar')
        self.theme = 'minimal'
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        self.status_label = QLabel('就绪')
        self.status_label.setObjectName('caption')
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.progress = NeonProgressBar()
        self.progress.setFixedWidth(200)
        layout.addWidget(self.progress)

    def set_theme(self, theme: str):
        self.theme = theme
        self.progress.set_theme(theme)
        self.update()

    def set_status(self, text: str):
        self.status_label.setText(text)

    def set_progress(self, value: int):
        self.progress.set_value(value)


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PDF 工具箱')
        self.setMinimumSize(1100, 700)
        self.resize(1440, 860)

        self.theme_manager = get_theme_manager()
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self.theme = self.theme_manager.current_theme

        self._init_ui()
        self._setup_textures()
        self._connect_signals()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 主体
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # 侧边栏
        self.sidebar = Sidebar()
        self.sidebar.item_clicked.connect(self._on_sidebar_item_clicked)
        body.addWidget(self.sidebar)

        # 内容区
        self.content = ContentArea()
        body.addWidget(self.content, 1)

        layout.addLayout(body, 1)

        # 状态栏
        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)

    def _setup_textures(self):
        central = self.centralWidget()
        self.rice_paper = RicePaperTexture(central)
        self.scifi_grid = SciFiGridTexture(central)
        self.minimal_tex = MinimalTexture(central)
        self.rice_paper.lower()
        self.scifi_grid.lower()
        self.minimal_tex.lower()

    def _connect_signals(self):
        self.sidebar.theme_btn.clicked.connect(self._toggle_theme)

    def _toggle_theme(self):
        theme_manager = get_theme_manager()
        theme_manager.toggle()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        sb_h = 28
        content_h = h - sb_h

        self.rice_paper.setGeometry(0, 0, w, content_h)
        self.scifi_grid.setGeometry(0, 0, w, content_h)
        self.minimal_tex.setGeometry(0, 0, w, content_h)

        if w < 1100 and not self.sidebar._collapsed:
            self.sidebar.set_collapsed(True)
        elif w >= 1100 and self.sidebar._collapsed:
            self.sidebar.set_collapsed(False)

    def _on_theme_changed(self, theme_name: str):
        self.theme = theme_name
        self.sidebar.set_theme(theme_name)
        self.content.set_theme(theme_name)
        self.status_bar.set_theme(theme_name)

        # 纹理可见性
        self.rice_paper.setVisible(theme_name == 'ink')
        self.scifi_grid.setVisible(theme_name == 'scifi')
        self.minimal_tex.setVisible(theme_name == 'minimal')

        # 递归应用主题
        apply_theme_to_widget(self, theme_name)

    def _on_sidebar_item_clicked(self, item_id: str):
        self.sidebar.set_selected(item_id)
        if item_id == 'settings':
            from ui.dialogs import SettingsDialog
            dialog = SettingsDialog(self)
            dialog.exec()
        else:
            # 切换页面
            page_map = {
                'home': 0,
                'split': 1,
                'merge': 2,
                'compress': 3,
                'page_editor': 4,
                'pdf_to_image': 5,
                'to_pdf': 6,
            }
            if item_id in page_map:
                self.content.set_page(page_map[item_id])

    def add_page(self, widget, name: str):
        self.content.add_page(widget, name)

    def set_page(self, index: int):
        self.content.set_page(index)

    def showEvent(self, event):
        super().showEvent(event)
        self._on_theme_changed(self.theme)
