from PyQt5.QtCore import QObject, pyqtSignal, QBuffer
from PyQt5.QtGui import QImage, QPixmap
from seamCarver import carveSeam
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