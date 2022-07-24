from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class PaintScene(QGraphicsScene):
    """
    This module deals with all stroke information for PyQtPaint.
    Creates and stores strokes, toggles visibility, communicates with PaintView
    and LayerPanel. Makes calls to QUndoFramework.
    based off: https://github.com/dpebly/pyqt-paint 

    Attributes:
        brushChanged (SIGNAL): emitted when brush settings change
        height (int): Height of scene
        next_stroke (int): Stores index of next stroke
        pen_blur (int): Controls brush hardness
        pen_color (QColor): Color of brush
        pen_size (int): Controls brush size
        strokeAdded (SIGNAL): emitted when new stroke added
        strokeRemoved (SIGNAL): emitted when stroked deleted
        undo_stack (QUndoStack): contains histroy of paint scene
        undo_view (QUndoView): history panel; currently hidden from users
        width (int): width of scene
    """

    strokeAdded = pyqtSignal(int, str)
    strokeRemoved = pyqtSignal(int)
    brushChanged = pyqtSignal()
    canvasEdited = pyqtSignal(QGraphicsPathItem)

    def __init__(self, background, *args, **kwargs):
        super(PaintScene, self).__init__(*args, **kwargs)

        # scene properties
        self.width = self.sceneRect().width()
        self.height = self.sceneRect().height()

        self.background = self.addPixmap(background)
        self.background.setZValue(0)

        # stroke info
        self.next_stroke = 0
        self._current_path = None
        self._path_preview = None
        self._paint_layer = None
        self._is_painting = False

        # brush properites
        self.pen_size = 30
        self.pen_color = QColor(255, 255, 255, 255)
        self.pen_blur = 25
        self.pen_opacity = 100

        # cursor preview
        pen = QPen(QColor(0, 0, 0, 255), .5,
                         Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin) 
        brush = QBrush(QColor(0, 0, 0, 0), Qt.SolidPattern)
        self._cursor_outline = self.addEllipse(-15, -15, 30, 30, pen, brush)

        pen = QPen(QColor(255, 255, 255, 0), 1,
                         Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin)
        brush = QBrush(QColor(255, 255, 255, 127),
                             Qt.SolidPattern)
        self._cursor_fill = self.addEllipse(-15, -15, 30, 30, pen, brush)
        self._cursor_fill.setOpacity(0)

        self._cursor_fill.setZValue(1000)
        self._cursor_outline.setZValue(1001)

    def clear(self):
        self.removeItem(self.background)

    def setPixmap(self, pixmap):
        self.background = self.addPixmap(pixmap)

    @property
    def is_painting(self):
        """
        Determines whether paint scene is currently creating new stroke

        Returns:
            bool: painting state
        """
        if self._current_path is None:
            return self._current_path

    def start_paintstroke(self, position, layer=None):
        """
        creates new QPath with appropriate brush settings

        Args:
            position (QPoint): start position of stroke
            layer (None, optional): index of target layer
        """
        if self.is_painting:
            if self.paintLayer == layer:
                self.update_paintstroke(position)
                return
            else:
                self.complete_paintstroke()

        self._current_path = QGraphicsPathItem(QPainterPath())
        pen = QPen(self.pen_color, self.pen_size, Qt.SolidLine,
                         Qt.RoundCap, Qt.RoundJoin)
        self._current_path.setPen(pen)
        path = QPainterPath(position)
        self._current_path.setPath(path)

        # draw preview
        # preview is temp version of stroke to display while drawing
        # preview is deleted when stroke is finalized
        pen = QPen(self.pen_color, self.pen_size,
                         Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin)
        self._path_preview = self.addPath(QPainterPath(), pen)
        self._path_preview.setPath(path)
        self._path_preview.setZValue(self.next_stroke + 1)

    def update_paintstroke(self, position):
        """
        Update stroke on mouse move

        Args:
            position (QPoint): new position of mouse, draw to this point
        """
        try:
            path = self._current_path.path()
            path.lineTo(position)
            self._current_path.setPath(path)
            self._path_preview.setPath(path)
        except AttributeError:
            pass

    def complete_paintstroke(self, position=None):
        """
        finish paint stroke, call push_stroke to add stroke to scene.
        Delete preview stroke used for stroke visualization while drawing.

        Args:
            position (None, optional): End position
        """
        if position:
            position.setX(position.x() + .0001)
            self.update_paintstroke(position)

        # add stroke
        stroke = self._current_path

        # delete preview stroke
        self._current_path = None
        self.removeItem(self._path_preview)
        self._path_preview = None

        self.canvasEdited.emit(stroke)

    def set_stroke_zindex(self, stroke_id, index):
        """
        sets stoke stacking order

        Args:
            stroke_id (int): stroke index
            index (int): stacking position
        """
        self.strokes[stroke_id]['stroke'].setZValue(index)

    def move_cursor_preview(self, position):
        """
        Updates position of preview cursor

        Args:
            position (QPoint): position of cursor
        """
        self._cursor_outline.setPos(position)
        self._cursor_fill.setPos(position)

    def set_pen_size(self, size):
        """
        sets size of pen

        Args:
            size (int): diameter of brush size
        """
        self.pen_size = size
        self._cursor_outline.setRect(-size/2, -size/2, size, size)
        self._cursor_fill.setRect(-size/2, -size/2, size, size)

    def set_pen_blur(self, blur):
        """
        sets softness of pen

        Args:
            blur (int): amount to blur pen by

        """
        self.pen_blur = blur
        self._cursor_fill.graphicsEffect().setBlurRadius(blur)

    def set_pen_color(self, color):
        """
        set pen color

        Args:
            color (QColor): new pen color

        """
        self.pen_color = color
        self._cursor_fill.setBrush(QBrush(color, Qt.SolidPattern))


class PaintView(QGraphicsView):
    """
    Display/input for Paint Scene
    """
    def __init__(self, *args, **kwargs):
        super(PaintView, self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setFrameStyle(QFrame.NoFrame)
        self.setBackgroundBrush(
            QBrush(QColor(128, 128, 128, 128),
                         Qt.SolidPattern))
        self._current_layer = None

    @property
    def current_layer(self):
        """
        current active layer/stroke

        Returns:
            int: layer index
        """
        return self._current_layer

    @current_layer.setter
    def current_layer(self, value):
        self._current_layer = value

    def mousePressEvent(self, event):
        """
        Starts paint stroke on user's initial click
        """
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            # self.scene().start_paintstroke(scene_pos)
            self.scene().start_paintstroke(scene_pos, layer=self.current_layer)
        super(PaintView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        updates cursor preview, updates stroke if drawing
        """
        # use event modifiers (?)
        scene_pos = self.mapToScene(event.pos())
        if event.buttons() & Qt.LeftButton:
            self.scene().update_paintstroke(scene_pos)
        self.scene().move_cursor_preview(scene_pos)

    def mouseReleaseEvent(self, event):
        """
        comeplete paint stroke on mouse release
        """
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.scene().complete_paintstroke(scene_pos)
            

    def resizeEvent(self, event):
        """
        scale paint viewer so canvas is in view, maintain aspect ratio
        """
        self.fitInView(0, 0, self.scene().width, self.scene().height,
                       Qt.KeepAspectRatio)

