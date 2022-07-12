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

    def __init__(self, w, h):
        super().__init__()
        self.setFixedSize(w, h)
        self.setAttribute(Qt.WA_TranslucentBackground)

        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)
        self.setPixmap(pixmap)

        self.lastPos = None
        self.brushColor = QColor('#FFFFFF')
        self.brushSize = 5

    def setBrushColor(self, c: QColor):
        self.brushColor = QColor(c)

    def setBrushSize(self, s: int):
        self.brushSize = s

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.lastPos = e.pos()
            

    def mouseMoveEvent(self, e):
        """
        Override parent mouse event function to update x and y
        """
        print('here')
        if self.lastX is None:
            print(e.x(), e.y())
            self.lastX = e.x()
            self.lastY = e.y()
            return # Ignore first event
        print('after')
        painter = QPainter(self.pixmap())
        print('making painter')
        p = painter.pen()
        p.setWidth(self.brushSize)
        p.setColor(self.brushColor)
        painter.setPen(p)
        painter.drawLine(self.lastX, self.lastY, e.x(), e.y())
        painter.end()
        self.update()

        #update lastx and lasty
        print('not first', e.x(), e.y())
        self.lastX = e.x()
        self.lastY = e.y()

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.lastX = None
        self.lastY = None
        self.canvasEdited.emit()

