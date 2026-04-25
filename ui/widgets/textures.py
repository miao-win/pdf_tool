"""
背景纹理生成模块（纯代码绘制，无贴图）
- 水墨宣纸：噪点+纤维线
- 科幻网格：40px 网格+暗角+扫描条
- 简约：纯色
"""
import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QColor, QLinearGradient, QRadialGradient, QPen


class TextureBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = 'minimal'
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()


class RicePaperTexture(TextureBackground):
    """水墨宣纸纹理"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._seed = 42
        self._noise_points = []
        self._fibers = []
        self._generate_texture()

    def _generate_texture(self):
        random.seed(self._seed)
        w, h = 1440, 860
        # 噪点
        count = random.randint(800, 1200)
        self._noise_points = []
        for _ in range(count):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            size = random.uniform(1, 2)
            alpha = random.randint(30, 70)
            color_val = random.choice(['#D9CFB4', '#CFC5A8', '#BFAE8A', '#D4C9B0'])
            self._noise_points.append((x, y, size, alpha, color_val))
        # 纤维线
        self._fibers = []
        for _ in range(random.randint(2, 3)):
            x1 = random.uniform(0, w)
            y1 = random.uniform(0, h)
            cx1 = random.uniform(0, w)
            cy1 = random.uniform(0, h)
            cx2 = random.uniform(0, w)
            cy2 = random.uniform(0, h)
            x2 = random.uniform(0, w)
            y2 = random.uniform(0, h)
            self._fibers.append((x1, y1, cx1, cy1, cx2, cy2, x2, y2))

    def paintEvent(self, event):
        if self.theme != 'ink':
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 噪点
        for x, y, size, alpha, color_val in self._noise_points:
            color = QColor(color_val)
            color.setAlpha(alpha)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawEllipse(QPoint(int(x), int(y)), int(size), int(size))

        # 纤维线
        pen = QPen(QColor(191, 174, 138, 15), 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        for x1, y1, cx1, cy1, cx2, cy2, x2, y2 in self._fibers:
            path = QPainterPath()
            path.moveTo(x1, y1)
            path.cubicTo(cx1, cy1, cx2, cy2, x2, y2)
            p.drawPath(path)


class SciFiGridTexture(TextureBackground):
    """科幻网格纹理"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scan_y = 0
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._update_scan)
        self._scan_timer.start(16)  # ~60fps
        self._scan_speed = 2

    def _update_scan(self):
        self._scan_y += self._scan_speed
        if self._scan_y > self.height():
            self._scan_y = 0
        self.update()

    def paintEvent(self, event):
        if self.theme != 'scifi':
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # 网格
        grid_color = QColor(0, 229, 255, 15)
        pen = QPen(grid_color, 0.5)
        p.setPen(pen)
        step = 40
        for x in range(0, w, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)

        # 径向暗角
        gradient = QRadialGradient(w/2, h/2, max(w, h) * 0.7)
        gradient.setColorAt(0, QColor(15, 25, 35, 0))
        gradient.setColorAt(1, QColor(15, 25, 35, 100))
        p.fillRect(0, 0, w, h, gradient)

        # 扫描条
        if h > 0:
            scan_height = 4
            scan_gradient = QLinearGradient(0, self._scan_y, w, self._scan_y)
            scan_gradient.setColorAt(0, QColor(0, 229, 255, 0))
            scan_gradient.setColorAt(0.3, QColor(0, 229, 255, 40))
            scan_gradient.setColorAt(0.5, QColor(0, 229, 255, 60))
            scan_gradient.setColorAt(0.7, QColor(0, 229, 255, 40))
            scan_gradient.setColorAt(1, QColor(0, 229, 255, 0))
            p.fillRect(0, self._scan_y, w, scan_height, scan_gradient)

            # 扫描线高光
            p.setPen(QPen(QColor(0, 229, 255, 80), 1))
            p.drawLine(0, self._scan_y, w, self._scan_y)


class MinimalTexture(TextureBackground):
    """简约纯色背景"""
    def paintEvent(self, event):
        if self.theme != 'minimal':
            return
        p = QPainter(self)
        p.fillRect(self.rect(), QColor('#FAFAFA'))
