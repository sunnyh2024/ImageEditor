from model import GUIEditorModel
from gui import Window
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image
import utils
import io


class Controller():
    """
    Connect self to the given model
    The controller will pass information from the view to the model and back to update the GUI
    """
    def __init__(self, view: Window, model: GUIEditorModel):
        self.layerCount = 0
        self.view = view
        self.model = model
        self.w, self.h = self.model.getSize()
        bkgrnd = self.model.getDisplayImage()
        self.view.createImagePanel(self.w, self.h, bkgrnd)
        for _ in model.getAllImages():
            self.view.addLayer(0, self.layerCount)
            self.layerCount += 1
        self.updateImage()
        self.view.connect_features(self)

        # create settings to store data between sessions (optional add)
        self.settings = QSettings('session_data.ini', QSettings.IniFormat)

    def blur(self):
        """
        Blurs the selected layer in the GUI
        """
        self.selectLayer()
        self.model.blur()
        self.updateImage()

    def sharpen(self):
        """
        Sharpens the selected layer in the GUI
        """
        self.selectLayer()
        self.model.sharpen()
        self.updateImage()

    def sepia(self):
        """
        Applies sepia filter to the selected layer in the GUI
        """
        self.selectLayer()
        self.model.sepia()
        self.updateImage()

    def grayscale(self):
        """
        Grayscales the selected layer in the GUI
        """
        self.selectLayer()
        self.model.grayscale()
        self.updateImage()

    # put this on a separate thread/multithread it... currently takes a long time
    def mosaic(self):
        """
        Applies the mosaic filter to the selected layer in the GUI
        """
        self.selectLayer()
        numseeds = QInputDialog.getInt(
            self.view, 'Seed Input', 'Enter seed count for mosaic', min=0, max=10000)
        if not numseeds[1]:
            return
        numseeds = numseeds[0]
        # Setting up thread (mosaic takes too long and freezes GUI)
        if self.view.t:
            return 
        self.view.t = QThread()
        self.view.worker = utils.MosaicWorker(self.model, numseeds)
        # create worker and move to thread
        self.view.worker.moveToThread(self.view.t)
        self.view.t.started.connect(self.view.worker.run)
        self.view.worker.finished.connect(self.view.t.quit)
        self.view.worker.finished.connect(self.view.worker.deleteLater)
        self.view.t.finished.connect(self.view.t.deleteLater)
        self.view.t.finished.connect(self.updateImage)
        self.view.t.finished.connect(self.view.removeLoadScreen)
        self.view.loadScreen() # let user know that process is running
        self.view.t.start()

    def carveSeam(self):
        """
        Prompts user input for the target width and height, then carves seams down to the input dimensions
        """
        maxWH = self.model.getSize()
        width = QInputDialog.getInt(self.view, 'Width Input', 'Enter taget image width (Pixels)\nEnter 0 to keep original image width', 
                                    min=0, max=maxWH[0])
        if not width[1]:
            return
        height = QInputDialog.getInt(self.view, 'Width Input', 'Enter taget image width (Pixels)\nEnter 0 to keep original image height', 
                                     min=0, max=maxWH[1])
        if not height[1]:
            return
        w = width[0] if width[0] else maxWH[0]
        h = height[0] if height[0] else maxWH[1]
        # Setting up thread (mosaic takes too long and freezes GUI)
        if self.view.t:
            return 
        self.view.t = QThread()
        self.view.worker = utils.SeamCarveWorker(self.model, w, h)
        # create worker and move to thread
        self.view.worker.moveToThread(self.view.t)
        self.view.t.started.connect(self.view.worker.run)
        self.view.worker.progress.connect(lambda i: print(f'carving for layer {i} completed'))
        self.view.worker.finished.connect(self.view.t.quit)
        self.view.worker.finished.connect(self.view.worker.deleteLater)
        self.view.t.finished.connect(self.view.t.deleteLater)
        self.view.t.finished.connect(self.updateImage)
        self.view.t.finished.connect(self.view.removeLoadScreen)
        self.view.loadScreen() # let user know that process is running
        self.view.t.start()

    def rotateImages(self):
        """
        Rotates all the images in the GUI 90 degrees counterclockwise
        """
        self.model.rotateAll90()
        self.updateImage()

    def horizontalFlip(self):
        """
        Flips the selected layer in the GUI horizontally
        """
        self.selectLayer()
        self.model.horizontalFlip()
        self.updateImage()

    def verticalFlip(self):
        """
        Flips the selected layer in the GUI vertically
        """
        self.selectLayer()
        self.model.verticalFlip()
        self.updateImage()

    def copyLayer(self):
        """
        Adds a copy of the GUI's selected layer above the selected layer
        """
        selected = self.selectLayer()
        self.model.addImage(self.model.getImageAt(selected))
        self.view.addLayer(selected, self.layerCount)
        self.updateImage()
        self.layerCount += 1

    def selectLayer(self):
        """
        Returns
        ============ 
        updates the model's selected layer to match the view's and returns the selected layer index.
        """
        current = self.view.layerList.currentRow()
        if current < 0:
            return 0
        self.model.selectLayer(current)
        self.updateImage()
        return current

    def addLayer(self):
        """
        Adds a blank white layer above the current selected layer.
        """
        selected = self.selectLayer()
        w, h = self.model.getSize()
        im = Image.new(mode="RGBA", size=(w, h), color=(255, 255, 255, 0))
        self.model.addImage(im)
        self.view.addLayer(selected, self.layerCount)
        self.updateImage()
        self.layerCount += 1

    def deleteLayer(self):
        """
        Deletes the GUI's selected layer
        """
        index = self.selectLayer()
        self.model.removeImage()
        self.view.removeLayer(index)
        self.updateImage()

    def deleteAllLayers(self):
        """
        Deletes all layers in the open project
        """
        self.model.removeAllImages()
        self.view.removeAllLayers()
        self.updateImage()
        self.layerCount = 0

    def updateImage(self):
        """
        Updates the GUI's displayed image according to the topmost visible image in the model
        """
        #img = self.model.getTopMost()
        img = self.model.getDisplayImage()
        self.view.updateImage(img)

    def rearrangeLayers(self, i, j):
        """
        Parameters
        ============ 
        i:
            integer representing the starting index of the layer that was moved
        j:
            integer representing the index that the moving layer was dropped at
        """
        self.model.moveLayer(i, j)
        self.updateImage()

    def changeVisibility(self):
        """
        Changes the visibility of the GUI's selected layer
        """
        self.selectLayer()
        self.model.changeVisibility()
        self.updateImage()

    def newProject(self):
        """
        Creates new empty project *FORMAT TBD*
        """
        return

    def openProject(self):
        """
        Opens a project in the editor's specific format
        """
        return

    # SAVE FUNCTIONS HERE

    def updateBrush(self):
        """
        Updates the hue and opacity of the brush and changes the preview square to match the new color
        """
        color = self.view.colorCircle.getColor()
        brightness = self.view.brightnessSlider.value()/255
        r = int(color.red()*brightness)
        g = int(color.green()*brightness)
        b = int(color.blue()*brightness)
        a = self.view.opacitySlider.value()
        newColor = QColor(r, g, b, a)
        self.view.scene.set_pen_color(newColor)
        self.view.changeSelectedColor(newColor)

    def updateBrushSize(self):
        """
        Changes the size of the drawing brush
        """
        size = self.view.widthSlider.value()
        self.view.scene.set_pen_size(size)

    def updateBrushStroke(self, stroke: QGraphicsPathItem):
        """
        Parameters
        ============ 
        stroke:
            QGraphicsPathItem that contains the stroke path as well as information about the pen

        connected to canvas edited. Takes the given brush stroke and adds it to the topmost model layer, then updates GUI
        """
        im, i = self.model.getTopMost()
        pix = utils.toPixmap(im)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(stroke.pen())
        painter.drawPath(stroke.path())
        painter.end()
        pil_im = utils.toPIL(pix)
        self.model.layers[i] = pil_im
        self.updateImage()



