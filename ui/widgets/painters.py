"""
自定义自绘控件集合
InkLine / CinnabarSeal / ChamferedButton / CornerMarks / BrushArrow / NeonProgressBar
"""
import random
from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRectF, QSize
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QLinearGradient, QFontMetrics


class InkLine(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.setFixedHeight(2 if orientation == Qt.Orientation.Horizontal else 20)
        self.theme = 'ink'
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self._segment_offsets = []
        self._ink_dots = []
        self._regenerate()

    def _regenerate(self):
        rng = random.Random(42)
        self._segment_offsets = [rng.uniform(-0.8, 0.8) for _ in range(200)]
        self._ink_dots = [
            (rng.uniform(0.1, 0.9), rng.uniform(-2, 2), rng.uniform(0.5, 1.5))
            for _ in range(3)
        ]

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        if self.theme != 'ink':
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        path = QPainterPath()
        if self.orientation == Qt.Orientation.Horizontal:
            y = h / 2
            path.moveTo(0, y)
            segments = max(3, w // 30)
            for i in range(segments):
                x = (i + 1) * w / segments
                dy = self._segment_offsets[i % len(self._segment_offsets)]
                path.lineTo(x, y + dy)
        else:
            x = w / 2
            path.moveTo(x, 0)
            path.lineTo(x, h)

        pen = QPen(QColor('#B8A88A'), 1.5)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.strokePath(path, pen)

        if self.orientation == Qt.Orientation.Horizontal:
            for rx, ry_offset, r in self._ink_dots:
                px = w * rx
                py = h / 2 + ry_offset
                p.setBrush(QColor('#A09070'))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPoint(int(px), int(py)), int(r), int(r))


class CinnabarSeal(QWidget):
    def __init__(self, text: str = '工', size: int = 40, parent=None):
        super().__init__(parent)
        self.text = text
        self.size = size
        self.setFixedSize(QSize(size, size))
        self.theme = 'ink'
        self._scale = 1.0
        self._glow_alpha = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def set_scale(self, scale: float):
        self._scale = scale
        self.update()

    def set_glow(self, alpha: int):
        self._glow_alpha = alpha
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = self.size
        cx, cy = s/2, s/2
        rect_size = s * 0.85 * self._scale
        x = cx - rect_size/2
        y = cy - rect_size/2

        if self.theme == 'ink':
            # 外发光
            if self._glow_alpha > 0:
                glow_pen = QPen(QColor(139, 43, 43, self._glow_alpha), 4)
                p.setPen(glow_pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(QRectF(x-2, y-2, rect_size+4, rect_size+4), 2, 2)

            # 印章边框
            pen = QPen(QColor('#8B2B2B'), 2.5)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(x, y, rect_size, rect_size), 2, 2)

            # 文字
            font = QFont("Noto Serif SC", int(s*0.35*self._scale))
            font.setBold(True)
            p.setFont(font)
            p.setPen(QColor('#8B2B2B'))
            fm = QFontMetrics(font)
            tw = fm.horizontalAdvance(self.text)
            th = fm.height()
            p.drawText(int(cx - tw/2), int(cy + th*0.35), self.text)
        elif self.theme == 'scifi':
            pen = QPen(QColor('#FF2E9A'), 1.5)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(x, y, rect_size, rect_size), 2, 2)
            font = QFont("Orbitron", int(s*0.25*self._scale))
            p.setFont(font)
            p.setPen(QColor('#FF2E9A'))
            fm = QFontMetrics(font)
            tw = fm.horizontalAdvance(self.text)
            th = fm.height()
            p.drawText(int(cx - tw/2), int(cy + th*0.35), self.text)
        else:
            pen = QPen(QColor('#2E6BE6'), 2)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(x, y, rect_size, rect_size), 4, 4)
            font = QFont("Inter", int(s*0.3*self._scale))
            p.setFont(font)
            p.setPen(QColor('#2E6BE6'))
            fm = QFontMetrics(font)
            tw = fm.horizontalAdvance(self.text)
            th = fm.height()
            p.drawText(int(cx - tw/2), int(cy + th*0.35), self.text)


class ChamferedButton(QPushButton):
    """切角按钮（科幻风）"""
    def __init__(self, text: str = '', parent=None):
        super().__init__(text, parent)
        self.theme = 'scifi'
        self._pressed = False
        self._hover = False
        self._chamfer = 8

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        c = self._chamfer

        if self.theme == 'scifi':
            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(w - c, 0)
            path.lineTo(w, c)
            path.lineTo(w, h)
            path.lineTo(c, h)
            path.lineTo(0, h - c)
            path.closeSubpath()

            if self._pressed:
                p.fillPath(path, QColor('#0F1A2E'))
            elif self._hover:
                p.fillPath(path, QColor('#1A2A4A'))
            else:
                p.fillPath(path, QColor('#162236'))

            pen = QPen(QColor('#00E5FF'), 1.5)
            p.strokePath(path, pen)

            if self._hover:
                glow = QPen(QColor(0, 229, 255, 80), 3)
                p.strokePath(path, glow)

            p.setPen(QColor('#00E5FF'))
            font = QFont("Rajdhani", 13)
            font.setWeight(QFont.Weight.Medium)
            p.setFont(font)
            fm = QFontMetrics(font)
            tw = fm.horizontalAdvance(self.text())
            th = fm.height()
            p.drawText(int((w - tw)/2), int((h + th*0.7)/2), self.text())
        else:
            super().paintEvent(event)


class CornerMarks(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = 'scifi'
        self._active = False
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def paintEvent(self, event):
        if self.theme != 'scifi':
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        length = min(w, h) * 0.12
        thickness = 2

        color = QColor('#00E5FF') if self._active else QColor('#1A3A5C')
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        p.setPen(pen)

        # 左上
        p.drawLine(0, length, 0, 0)
        p.drawLine(0, 0, length, 0)
        # 右上
        p.drawLine(w - length, 0, w, 0)
        p.drawLine(w, 0, w, length)
        # 左下
        p.drawLine(0, h - length, 0, h)
        p.drawLine(0, h, length, h)
        # 右下
        p.drawLine(w - length, h, w, h)
        p.drawLine(w, h - length, w, h)


class BrushArrow(QWidget):
    def __init__(self, direction=Qt.ArrowType.RightArrow, parent=None):
        super().__init__(parent)
        self.direction = direction
        self.theme = 'ink'
        self.setFixedSize(QSize(32, 24))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        if self.theme != 'ink':
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        path = QPainterPath()
        if self.direction == Qt.ArrowType.RightArrow:
            path.moveTo(w*0.1, h*0.5)
            path.lineTo(w*0.7, h*0.5)
            path.moveTo(w*0.55, h*0.25)
            path.lineTo(w*0.75, h*0.5)
            path.lineTo(w*0.55, h*0.75)
        else:
            path.moveTo(w*0.9, h*0.5)
            path.lineTo(w*0.3, h*0.5)
            path.moveTo(w*0.45, h*0.25)
            path.lineTo(w*0.25, h*0.5)
            path.lineTo(w*0.45, h*0.75)

        pen = QPen(QColor('#3E5E5A'), 2.2)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
        p.strokePath(path, pen)

        # 飞白效果
        pen2 = QPen(QColor(62, 94, 90, 120), 1.0)
        pen2.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.strokePath(path, pen2)


class NeonProgressBar(QWidget):
    """霓虹进度条（科幻风）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = 'scifi'
        self._value = 0
        self._maximum = 100
        self.setFixedHeight(8)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def set_value(self, value: int):
        self._value = max(0, min(value, self._maximum))
        self.update()

    def set_maximum(self, maximum: int):
        self._maximum = max(1, maximum)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        if self.theme == 'scifi':
            # 背景
            p.fillRect(0, 0, w, h, QColor('#162236'))

            # 进度
            if self._maximum > 0:
                pw = int(w * self._value / self._maximum)
                if pw > 0:
                    gradient = QLinearGradient(0, 0, pw, 0)
                    gradient.setColorAt(0, QColor('#00E5FF'))
                    gradient.setColorAt(1, QColor('#00E5FF'))
                    p.fillRect(0, 0, pw, h, gradient)

                    # 发光效果
                    glow = QPen(QColor(0, 229, 255, 60), 2)
                    p.setPen(glow)
                    p.drawLine(pw, 0, pw, h)

            # 边框
            p.setPen(QPen(QColor('#1A3A5C'), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(0, 0, w-1, h-1)

            # 滚动字符
            if self._value > 0 and self._value < self._maximum:
                font = QFont("Share Tech Mono", 8)
                p.setFont(font)
                p.setPen(QColor('#00E5FF'))
                blocks = int(self._value / self._maximum * 10)
                text = '▮' * blocks + '░' * (10 - blocks)
                p.drawText(4, h + 12, text)
        elif self.theme == 'ink':
            p.fillRect(0, 0, w, h, QColor('#E0D5C0'))
            if self._maximum > 0:
                pw = int(w * self._value / self._maximum)
                if pw > 0:
                    p.fillRect(0, 0, pw, h, QColor('#8B2B2B'))
                    # 飞白渐变
                    gradient = QLinearGradient(pw - 20, 0, pw, 0)
                    gradient.setColorAt(0, QColor('#8B2B2B'))
                    gradient.setColorAt(1, QColor(139, 43, 43, 0))
                    p.fillRect(max(0, pw - 20), 0, min(20, pw), h, gradient)
            p.setPen(QPen(QColor('#C4B9A0'), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(0, 0, w-1, h-1)
        else:
            p.fillRect(0, 0, w, h, QColor('#E5E7EB'))
            if self._maximum > 0:
                pw = int(w * self._value / self._maximum)
                if pw > 0:
                    p.fillRect(0, 0, pw, h, QColor('#2E6BE6'))
            p.setPen(QPen(QColor('#D1D5DB'), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(0, 0, w-1, h-1)
