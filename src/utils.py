from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import itertools
import sys
import time
import threading


def getDistance(posn1, posn2):
    """Helper for getSeeds that calculates the cartesian distance between two tuple points."""
    distX = (posn1[0] - posn2[0]) ** 2
    distY = (posn1[1] - posn2[1]) ** 2
    return (distX + distY) ** 0.5

def toPixmap(image):
    if image:
        im = image.convert("RGBA")
        data = im.tobytes("raw","RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGBA8888)
        pix = QPixmap(qim)
        return pix

class MosaicWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, model, numseeds, parent=None):
        super().__init__(parent)
        self.model = model
        self.numseeds = numseeds

    def run(self):
       self.model.mosaic(self.numseeds)
       self.finished.emit()

class SeamCarveWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.placeholder = 'test'

# done = False
# #here is the animation
# def animate():
#     for c in itertools.cycle(['|', '/', '-', '\\']):
#         if done:
#             break
#         sys.stdout.write('\rloading ' + c)
#         sys.stdout.flush()
#         time.sleep(0.1)
#     sys.stdout.write('\rDone!     ')

# t = threading.Thread(target=animate)
# t.start()

# #long process here
# time.sleep(10)
# done = True