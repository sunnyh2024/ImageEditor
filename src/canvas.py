from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image

class Canvas(QLabel):
    """
    Extension of QLabel that contains tools to edit a QPixmap
    Canvas will always be set with a transparent pixmap
    taken from: https://www.pythonguis.com/tutorials/bitmap-graphics/ 
    """
    canvasEdited = pyqtSignal()

    def __init__(self, w, h, pixmap=None):
        super().__init__()
        self.setFixedSize(w, h)
        if pixmap is None:
            pixmap = QPixmap(w, h)
            #pixmap.fill(Qt.transparent)
            pixmap.fill()
        self.setPixmap(pixmap)

        self.lastX, self.lastY = None, None
        self.brushColor = QColor('#000000')
        self.brushSize = 5

    def setBrushColor(self, c: QColor):
        self.brushColor = QColor(c)

    def setBrushSize(self, s: int):
        self.brushSize = s

    def mouseMoveEvent(self, e):
        """
        Override parent mouse event function to update x and y
        """
        if self.lastX is None:
            self.lastX = e.x()
            self.lastY = e.y()
            return # Ignore first event

        painter = QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(self.brushSize)
        p.setColor(self.brushColor)
        painter.setPen(p)
        painter.drawLine(self.lastX, self.lastY, e.x(), e.y())
        painter.end()
        self.update()

        #update lastx and lasty
        self.lastX = e.x()
        self.lastY = e.y()

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.lastX = None
        self.lastY = None
        self.canvasEdited.emit()