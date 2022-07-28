from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from seamCarver import carveSeam
from colorcircle import ColorCircle
from PIL import Image
import io


def getDistance(posn1, posn2):
    """Helper for getSeeds that calculates the cartesian distance between two tuple points."""
    distX = (posn1[0] - posn2[0]) ** 2
    distY = (posn1[1] - posn2[1]) ** 2
    return (distX + distY) ** 0.5

def toPixmap(image):
    if not image:
        return
    im = image.convert("RGBA")
    data = im.tobytes("raw","RGBA")
    qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGBA8888)
    pix = QPixmap(qim)
    return pix

def toPIL(pixmap: QPixmap):
    if not pixmap:
        return
    qim = pixmap.toImage()
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    qim.save(buffer, 'PNG')
    return Image.open(io.BytesIO(buffer.data()))

class MosaicWorker(QObject):
    """
    worker that runs the mosaic filter. Used with the QThread to prevent GUI freezing
    """
    finished = pyqtSignal()

    def __init__(self, model, numseeds, parent=None):
        super().__init__(parent)
        self.model = model
        self.numseeds = numseeds

    def run(self):
       self.model.mosaic(self.numseeds)
       self.finished.emit()

class SeamCarveWorker(QObject):
    """
    worker that carves seams. Used with the QThread to prevent GUI freezing
    """
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, model, width, height, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.model = model

    def run(self):
        for count, image in enumerate(self.model.getAllImages()):
            newImage = Image.fromarray(carveSeam(image, self.width, self.height))
            self.model.layers[count] = newImage
            self.progress.emit(count)
        self.finished.emit()

class BlankProjectDialog(QDialog):
    """
    Dialog that allows user to configure a new blank file
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configure New Project')
        self.color = QColor(255, 255, 255, 255)
        self.width = 0
        self.height = 0

        self.layout = QGridLayout(self)
        self.layout.setRowMinimumHeight(3, 250)
        for i in range(3):
            self.layout.setColumnMinimumWidth(i, 125)

        validator = QIntValidator()
        self.widthInput = QLineEdit()
        self.widthInput.setValidator(validator)
        self.layout.addWidget(QLabel('Project Width (Pixels):'), 0, 0)
        self.layout.addWidget(self.widthInput, 0, 1, 1, 2)
        self.heightInput = QLineEdit()
        self.heightInput.setValidator(validator)
        self.layout.addWidget(QLabel('Project Height (Pixels):'), 1, 0)
        self.layout.addWidget(self.heightInput, 1, 1, 1, 2)
        self.layout.addWidget(QLabel('Background Color:'), 2, 0)
        self.colorCircle = ColorCircle()
        self.colorCircle.currentColorChanged.connect(self.setColor)
        self.layout.addWidget(self.colorCircle, 3, 0, 1, 2)

        pix = QPixmap(30, 30)
        pix.fill()
        self.selectedColorLabel = QLabel(alignment=Qt.AlignCenter | Qt.AlignBottom)
        self.selectedColorLabel.setStyleSheet('background-color: rgba(0, 0, 0, 0)')
        self.selectedColorLabel.setPixmap(pix)
        self.layout.addWidget(self.selectedColorLabel, 3, 2)

        self.createBtn = QPushButton('Create')
        self.createBtn.clicked.connect(self.create)
        self.layout.addWidget(self.createBtn, 4, 1)
        self.cancelBtn = QPushButton('Cancel')
        self.cancelBtn.clicked.connect(self.cancel)
        self.layout.addWidget(self.cancelBtn, 4, 2)

        self.errorLabel = QLabel('', alignment=Qt.AlignCenter)
        self.errorLabel.setStyleSheet('color: rgba(255, 0, 0, 255)')
        self.layout.addWidget(self.errorLabel, 5, 0, 1, 3)

        self.exec()

    def setColor(self, color):
        """
        Setter for background color
        """
        self.color = color
        pix = QPixmap(30, 30)
        pix.fill(color)
        self.selectedColorLabel.setPixmap(pix)

    def cancel(self):
        """
        Resets 
        """
        self.width = 0
        self.height = 0
        self.close()

    def create(self):
        self.errorLabel.clear()

        if (not self.widthInput.text()):
            self.errorLabel.setText('Please provide a width')
            return
        if (not self.heightInput.text()):
            self.errorLabel.setText('Please provide a height')
            return
        try:
            self.width = int(self.widthInput.text())
            self.height = int(self.heightInput.text())
            if (self.width < 1) or (self.height < 1):
                self.errorLabel.setText('Dimensions must be greater than 0')
                return
        except:
            self.errorLabel.setText('Given Dimensions are not valid')
            return
        self.close()
        