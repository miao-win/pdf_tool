"""
自绘图标系统
14 枚图标统一 IconWidget(name, size, theme)
paintEvent 中 QPainterPath 绘制
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QFont


class IconWidget(QWidget):
    """自绘图标组件"""

    ICONS = {
        'home': '_draw_home',
        'split': '_draw_split',
        'merge': '_draw_merge',
        'compress': '_draw_compress',
        'edit': '_draw_edit',
        'pdf_to_image': '_draw_pdf_to_image',
        'to_pdf': '_draw_to_pdf',
        'settings': '_draw_settings',
        'back': '_draw_back',
        'close': '_draw_close',
        'minimize': '_draw_minimize',
        'maximize': '_draw_maximize',
        'add': '_draw_add',
        'remove': '_draw_remove',
        'folder': '_draw_folder',
        'file': '_draw_file',
        'check': '_draw_check',
        'warning': '_draw_warning',
        'error': '_draw_error',
        'info': '_draw_info',
        'drag': '_draw_drag',
        'scan': '_draw_scan',
        'grid': '_draw_grid',
        'ink_dot': '_draw_ink_dot',
        'hexagon': '_draw_hexagon',
    }

    THEME_COLORS = {
        'minimal': {
            'primary': '#2E6BE6',
            'secondary': '#57606A',
            'accent': '#2E6BE6',
            'text': '#1F2328',
        },
        'ink': {
            'primary': '#1C1B1A',
            'secondary': '#5C5650',
            'accent': '#8B2B2B',
            'text': '#1C1B1A',
        },
        'scifi': {
            'primary': '#00E5FF',
            'secondary': '#6D8299',
            'accent': '#FF2E9A',
            'text': '#E2F3FF',
        }
    }

    def __init__(self, name: str, size: int = 24, theme: str = 'minimal', parent=None):
        super().__init__(parent)
        self.name = name
        self.size = size
        self.theme = theme
        self.setFixedSize(QSize(size, size))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_theme(self, theme: str):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = self.THEME_COLORS.get(self.theme, self.THEME_COLORS['minimal'])
        method_name = self.ICONS.get(self.name, '_draw_home')
        method = getattr(self, method_name)
        method(painter, self.rect(), colors)

    def _draw_home(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.15
        path = QPainterPath()
        path.moveTo(s/2, margin)
        path.lineTo(margin, s*0.45)
        path.lineTo(margin, s*0.85)
        path.lineTo(s*0.38, s*0.85)
        path.lineTo(s*0.38, s*0.65)
        path.lineTo(s*0.62, s*0.65)
        path.lineTo(s*0.62, s*0.85)
        path.lineTo(s*0.85, s*0.85)
        path.lineTo(s*0.85, s*0.45)
        path.closeSubpath()
        self._stroke_path(p, path, colors)

    def _draw_split(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.addRect(margin, margin, s*0.35, s - 2*margin)
        path.addRect(s*0.65, margin, s*0.35, s - 2*margin)
        path2 = QPainterPath()
        path2.moveTo(s*0.5, margin)
        path2.lineTo(s*0.5, s*0.4)
        path2.moveTo(s*0.5, s*0.6)
        path2.lineTo(s*0.5, s - margin)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors, accent=True)

    def _draw_merge(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.moveTo(s*0.5, margin)
        path.lineTo(s*0.5, s*0.35)
        path.lineTo(s*0.25, s*0.35)
        path.lineTo(s*0.25, s*0.65)
        path.lineTo(s*0.5, s*0.65)
        path.lineTo(s*0.5, s - margin)
        path.moveTo(s*0.5, s*0.5)
        path.lineTo(s*0.75, s*0.5)
        self._stroke_path(p, path, colors)

    def _draw_compress(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.addRect(margin, margin, s - 2*margin, s*0.35)
        path2 = QPainterPath()
        path2.moveTo(s*0.35, s*0.55)
        path2.lineTo(s*0.25, s*0.55)
        path2.lineTo(s*0.25, s*0.75)
        path2.lineTo(s*0.45, s*0.75)
        path3 = QPainterPath()
        path3.moveTo(s*0.65, s*0.55)
        path3.lineTo(s*0.75, s*0.55)
        path3.lineTo(s*0.75, s*0.75)
        path3.lineTo(s*0.55, s*0.75)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors)
        self._stroke_path(p, path3, colors)

    def _draw_edit(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.moveTo(s*0.75, margin)
        path.lineTo(s*0.55, s*0.45)
        path.lineTo(s*0.55, s*0.55)
        path.lineTo(s*0.65, s*0.55)
        path.lineTo(s*0.85, s*0.15)
        path.closeSubpath()
        path2 = QPainterPath()
        path2.moveTo(s*0.45, s*0.55)
        path2.lineTo(s*0.25, s*0.55)
        path2.lineTo(s*0.25, s*0.85)
        path2.lineTo(s*0.55, s*0.85)
        path2.lineTo(s*0.55, s*0.65)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors)

    def _draw_pdf_to_image(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.addRect(margin, margin, s*0.5, s*0.6)
        path2 = QPainterPath()
        path2.addRect(s*0.45, s*0.35, s*0.4, s*0.45)
        path3 = QPainterPath()
        path3.moveTo(s*0.55, s*0.15)
        path3.lineTo(s*0.65, s*0.15)
        path3.lineTo(s*0.65, s*0.25)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors, accent=True)
        self._stroke_path(p, path3, colors)

    def _draw_to_pdf(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.addRect(s*0.35, margin, s*0.4, s*0.45)
        path2 = QPainterPath()
        path2.addRect(margin, s*0.4, s*0.5, s*0.4)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors, accent=True)

    def _draw_settings(self, p: QPainter, rect, colors):
        s = rect.width()
        cx, cy = s/2, s/2
        r1, r2 = s*0.12, s*0.28
        path = QPainterPath()
        for i in range(8):
            angle = i * 45 * 3.14159 / 180
            x1 = cx + r1 * 0.5 * (1.2 if i % 2 == 0 else 0.8) * (1 if angle < 3.14 else -1)
            y1 = cy + r1 * 0.5 * (1.2 if i % 2 == 0 else 0.8) * (1 if abs(angle - 1.57) < 1.57 else -1)
            if i == 0:
                path.moveTo(x1, y1)
            else:
                path.lineTo(x1, y1)
        path.closeSubpath()
        path2 = QPainterPath()
        path2.addEllipse(cx - r1*0.5, cy - r1*0.5, r1, r1)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors)

    def _draw_back(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.moveTo(s*0.5, margin)
        path.lineTo(margin, s/2)
        path.lineTo(s*0.5, s - margin)
        path2 = QPainterPath()
        path2.moveTo(margin, s/2)
        path2.lineTo(s - margin, s/2)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors)

    def _draw_close(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.25
        path = QPainterPath()
        path.moveTo(margin, margin)
        path.lineTo(s - margin, s - margin)
        path2 = QPainterPath()
        path2.moveTo(s - margin, margin)
        path2.lineTo(margin, s - margin)
        self._stroke_path(p, path, colors, accent=True)
        self._stroke_path(p, path2, colors, accent=True)

    def _draw_minimize(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.25
        path = QPainterPath()
        path.moveTo(margin, s/2)
        path.lineTo(s - margin, s/2)
        self._stroke_path(p, path, colors)

    def _draw_maximize(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.addRect(margin, margin, s - 2*margin, s - 2*margin)
        self._stroke_path(p, path, colors)

    def _draw_add(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.25
        path = QPainterPath()
        path.moveTo(s/2, margin)
        path.lineTo(s/2, s - margin)
        path2 = QPainterPath()
        path2.moveTo(margin, s/2)
        path2.lineTo(s - margin, s/2)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors)

    def _draw_remove(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.25
        path = QPainterPath()
        path.moveTo(margin, s/2)
        path.lineTo(s - margin, s/2)
        self._stroke_path(p, path, colors)

    def _draw_folder(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.15
        path = QPainterPath()
        path.moveTo(margin, s*0.3)
        path.lineTo(s*0.35, s*0.3)
        path.lineTo(s*0.4, s*0.2)
        path.lineTo(s*0.75, s*0.2)
        path.lineTo(s*0.75, s*0.3)
        path.lineTo(s*0.85, s*0.3)
        path.lineTo(s*0.85, s*0.8)
        path.lineTo(margin, s*0.8)
        path.closeSubpath()
        self._stroke_path(p, path, colors)

    def _draw_file(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.moveTo(margin, margin)
        path.lineTo(s*0.65, margin)
        path.lineTo(s*0.85, s*0.25)
        path.lineTo(s*0.85, s - margin)
        path.lineTo(margin, s - margin)
        path.closeSubpath()
        path2 = QPainterPath()
        path2.moveTo(s*0.65, margin)
        path2.lineTo(s*0.65, s*0.25)
        path2.lineTo(s*0.85, s*0.25)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors)

    def _draw_check(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.moveTo(margin, s*0.55)
        path.lineTo(s*0.4, s*0.8)
        path.lineTo(s*0.85, margin)
        self._stroke_path(p, path, colors, accent=True)

    def _draw_warning(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.moveTo(s/2, margin)
        path.lineTo(s - margin, s*0.8)
        path.lineTo(margin, s*0.8)
        path.closeSubpath()
        path2 = QPainterPath()
        path2.moveTo(s/2, s*0.4)
        path2.lineTo(s/2, s*0.6)
        path3 = QPainterPath()
        path3.moveTo(s/2, s*0.68)
        path3.lineTo(s/2, s*0.72)
        self._stroke_path(p, path, colors, accent=True)
        self._stroke_path(p, path2, colors)
        self._stroke_path(p, path3, colors)

    def _draw_error(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.addEllipse(margin, margin, s - 2*margin, s - 2*margin)
        path2 = QPainterPath()
        path2.moveTo(s*0.35, s*0.35)
        path2.lineTo(s*0.65, s*0.65)
        path3 = QPainterPath()
        path3.moveTo(s*0.65, s*0.35)
        path3.lineTo(s*0.35, s*0.65)
        self._stroke_path(p, path, colors, accent=True)
        self._stroke_path(p, path2, colors)
        self._stroke_path(p, path3, colors)

    def _draw_info(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        path.addEllipse(margin, margin, s - 2*margin, s - 2*margin)
        path2 = QPainterPath()
        path2.moveTo(s/2, s*0.35)
        path2.lineTo(s/2, s*0.4)
        path3 = QPainterPath()
        path3.moveTo(s/2, s*0.48)
        path3.lineTo(s/2, s*0.7)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors)
        self._stroke_path(p, path3, colors)

    def _draw_drag(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.25
        path = QPainterPath()
        for i in range(3):
            y = margin + i * (s - 2*margin) / 2
            path.moveTo(margin, y)
            path.lineTo(s - margin, y)
        self._stroke_path(p, path, colors)

    def _draw_scan(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.15
        path = QPainterPath()
        path.addRect(margin, margin, s - 2*margin, s - 2*margin)
        path2 = QPainterPath()
        path2.moveTo(margin, s*0.5)
        path2.lineTo(s - margin, s*0.5)
        self._stroke_path(p, path, colors)
        self._stroke_path(p, path2, colors, accent=True)

    def _draw_grid(self, p: QPainter, rect, colors):
        s = rect.width()
        margin = s * 0.2
        path = QPainterPath()
        for i in range(4):
            x = margin + i * (s - 2*margin) / 3
            path.moveTo(x, margin)
            path.lineTo(x, s - margin)
        for i in range(4):
            y = margin + i * (s - 2*margin) / 3
            path.moveTo(margin, y)
            path.lineTo(s - margin, y)
        self._stroke_path(p, path, colors)

    def _draw_ink_dot(self, p: QPainter, rect, colors):
        s = rect.width()
        cx, cy = s/2, s/2
        r = s*0.25
        path = QPainterPath()
        path.addEllipse(cx - r, cy - r, r*2, r*2)
        p.fillPath(path, QColor(colors['accent']))

    def _draw_hexagon(self, p: QPainter, rect, colors):
        s = rect.width()
        cx, cy = s/2, s/2
        r = s*0.35
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
        self._stroke_path(p, path, colors, accent=True)

    def _stroke_path(self, p: QPainter, path: QPainterPath, colors: dict, accent: bool = False):
        color = QColor(colors['accent'] if accent else colors['primary'])
        if self.theme == 'ink':
            pen = QPen(color, 1.8)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
            p.strokePath(path, pen)
        elif self.theme == 'scifi':
            pen = QPen(color, 1.2)
            pen.setCapStyle(Qt.PenCapStyle.SquareCap)
            p.strokePath(path, pen)
            glow = QPen(QColor(colors['accent']))
            glow.setWidthF(0.5)
            p.strokePath(path, glow)
        else:
            pen = QPen(color, 1.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.strokePath(path, pen)
