from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorcircle import ColorCircle
from canvas import Canvas
import utils
import itertools
import time
import threading

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PyEditor")
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(400, 200, 1600, 900)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setColumnMinimumWidth(1, 300)

        self.createMenuBar()
        self.createDrawPanel()
        #self.createImagePanel()
        self.createLayerPanel()
        self.createToolbar()

    def createMenuBar(self):
        """Creates the top menu bar with the File, Image, Draw and Help Menus"""
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        self.newAct = QAction('&New')
        fileMenu.addAction(self.newAct)
        self.openAct = QAction('&Open')
        fileMenu.addAction(self.openAct)
        self.saveAct = QAction('&Save')
        fileMenu.addAction(self.saveAct)
        self.saveAsAct = QAction('&Save As')
        fileMenu.addAction(self.saveAsAct)
        self.saveProjAct = QAction('&Save Project')
        fileMenu.addAction(self.saveProjAct)
        self.quitAct = QAction('&Quit')
        self.quitAct.triggered.connect(lambda: QApplication.quit())
        fileMenu.addAction(self.quitAct)

        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)
        self.zinAct = QAction('&Zoom In')
        editMenu.addAction(self.zinAct)
        self.zoutAct = QAction('&Zoom Out')
        editMenu.addAction(self.zoutAct)

        imageMenu = QMenu("&Image", self)
        menuBar.addMenu(imageMenu)
        # creates filter submenu
        filtermenu = imageMenu.addMenu('Filter')
        self.blurAct = QAction('Blur')
        filtermenu.addAction(self.blurAct)
        self.sharpenAct = QAction('Sharpen')
        filtermenu.addAction(self.sharpenAct)
        self.sepiaAct = QAction('Sepia')
        filtermenu.addAction(self.sepiaAct)
        self.grayscaleAct = QAction('Grayscale')
        filtermenu.addAction(self.grayscaleAct)
        self.mosaicAct = QAction('Mosaic')
        filtermenu.addAction(self.mosaicAct)

        self.cLayerAct = QAction('&Copy Layer')
        imageMenu.addAction(self.cLayerAct)
        self.removeAct = QAction('&Remove Layer')
        imageMenu.addAction(self.removeAct)
        self.remAllAct = QAction('&Remove All')
        imageMenu.addAction(self.remAllAct)

        rotateMenu = imageMenu.addMenu('&Image Rotation')
        self.rotateAct = QAction('&Rotate 90° Counterclockwise')
        rotateMenu.addAction(self.rotateAct)
        self.horizFlipAct = QAction('&Flip Horizontally')
        rotateMenu.addAction(self.horizFlipAct)
        self.vertFlipAct = QAction('&Flip Vertically')
        rotateMenu.addAction(self.vertFlipAct)

        drawMenu = QMenu("&Draw", self)
        menuBar.addMenu(drawMenu)
        drawMenu.addAction("&For Future Use")

        # viewMenu = QMenu("&View", self)
        # menuBar.addMenu(viewMenu)
        # modeMenu = viewMenu.addMenu('&Mode')
        # modeMenu.addAction('Light')
        # modeMenu.addAction('Dark')

        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)

        helpMenu.addAction("&Help")
        helpMenu.addAction("&How to Use")

    def createImagePanel(self, w, h, background):
        """creates main image panel"""
        leftSpacer = QLabel()
        leftSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout.addWidget(leftSpacer, 0, 0, 3, 1)
        # self.workspace = WorkSpace(w, h, background)
        # self.gridLayout.addWidget(self.workspace, 0, 1, 3, 1, alignment=Qt.AlignCenter)
        self.background = QLabel()
        self.background.setPixmap(utils.toPixmap(background))
        self.gridLayout.addWidget(self.background, 0, 1, 3, 1, alignment=Qt.AlignCenter)
        self.canvas = Canvas(w, h)
        self.gridLayout.addWidget(self.canvas, 0, 1, 3, 1, alignment=Qt.AlignCenter)
        rightSpacer = QLabel()
        rightSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout.addWidget(rightSpacer, 0, 2, 3, 1)
        self.loadingLabel = QLabel()
        self.loadingLabel.setAlignment(Qt.AlignCenter)
        self.loadingLabel.setStyleSheet("background-color: rgba(0, 0, 0, 150); font-size: 16pt;")
        self.gridLayout.addWidget(self.loadingLabel, 0, 0, 3, 3)
        self.loadingLabel.hide()
    
    def loadScreen(self):
        """starts the loading animation for certain processes that take a long time to run"""
        self.finishedLoading = False
        # use this when running long filters so user knows the image is being updated
        def animate():
            for c in itertools.cycle(['', '.', '..', '...']):
                if self.finishedLoading:
                    break
                self.loadingLabel.setText('Applying ' + c)
                time.sleep(0.3)
        self.loadingThread = threading.Thread(target=animate, daemon=True)
        self.loadingLabel.show()
        self.loadingThread.start()

    def removeLoadScreen(self):
        """removes the loading animation from the image panel"""
        self.finishedLoading = True
        self.loadingLabel.clear()
        self.loadingLabel.hide()

    def createDrawPanel(self):
        """creates the panel that contains the filter tab and draw tab"""
        drawPanel = QWidget(self)
        drawLayout = QVBoxLayout(drawPanel)
        drawPanel.setLayout(drawLayout)

        tabs = QTabWidget()

        filterTab = QWidget()
        filterLayout = QVBoxLayout(filterTab)

        scrollArea = QScrollArea(filterTab)
        scrollArea.setWidgetResizable(True)
        scrollContent = QWidget()
        scrollLayout = QVBoxLayout(scrollContent)
        scrollArea.setWidget(scrollContent)

        self.blurBtn = QPushButton('Blur')
        self.blurBtn.setFixedSize(QSize(75, 25))
        scrollLayout.addWidget(self.blurBtn)
        self.sharpenBtn = QPushButton('Sharpen')
        self.sharpenBtn.setFixedSize(QSize(75, 25))
        scrollLayout.addWidget(self.sharpenBtn)
        self.sepiaBtn = QPushButton('Sepia')
        self.sepiaBtn.setFixedSize(QSize(75, 25))
        scrollLayout.addWidget(self.sepiaBtn)
        self.grayBtn = QPushButton('Grayscale')
        self.grayBtn.setFixedSize(QSize(75, 25))
        scrollLayout.addWidget(self.grayBtn)
        self.mosaicBtn = QPushButton('Mosaic')
        self.mosaicBtn.setFixedSize(QSize(75, 25))
        scrollLayout.addWidget(self.mosaicBtn)
        self.carveBtn = QPushButton('Carve')
        self.carveBtn.setFixedSize(QSize(75, 25))
        scrollLayout.addWidget(self.carveBtn)

        filterLayout.addWidget(scrollArea)

        drawTab = QWidget()
        drawTabLayout = QGridLayout(drawTab)
        colorLabel = QLabel('Select Color or Enter RGB')
        colorLabel.setMaximumHeight(50)
        self.colorInput = QLineEdit()
        self.colorInput.setPlaceholderText('Enter RGB')
        self.enterColorBtn = QPushButton('Apply')
        self.colorCircle = ColorCircle(self)
        self.colorCircle.setMinimumSize(200, 200)
        selectedColor = QPixmap(30, 30)
        selectedColor.fill()
        self.selectedColorLabel = QLabel(alignment=Qt.AlignCenter)
        self.selectedColorLabel.setStyleSheet('background-color: rgba(0, 0, 0, 0)')
        self.selectedColorLabel.setPixmap(selectedColor)

        self.widthSlider = QSlider(Qt.Horizontal)
        self.widthSlider.setMinimum(1)
        self.widthSlider.setMaximum(20)
        self.widthSlider.setValue(5)
        self.widthSlider.setTickPosition(QSlider.NoTicks)

        self.brightnessSlider = QSlider(Qt.Horizontal)
        self.brightnessSlider.setMinimum(0)
        self.brightnessSlider.setMaximum(255)
        self.brightnessSlider.setValue(255)
        self.brightnessSlider.setTickPosition(QSlider.NoTicks)

        self.opacitySlider = QSlider(Qt.Horizontal)
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(255)
        self.opacitySlider.setValue(255)
        self.opacitySlider.setTickPosition(QSlider.NoTicks)

        self.hardnessSlider = QSlider(Qt.Horizontal)
        self.hardnessSlider.setMinimum(0)
        self.hardnessSlider.setMaximum(100)
        self.hardnessSlider.setValue(75)
        self.hardnessSlider.setTickPosition(QSlider.NoTicks)

        drawTabLayout.addWidget(colorLabel, 0, 0, 1, 2)
        drawTabLayout.addWidget(self.colorCircle, 1, 0, 2, 2)
        drawTabLayout.addWidget(self.selectedColorLabel, 2, 1)
        drawTabLayout.addWidget(self.colorInput, 3, 0)
        drawTabLayout.addWidget(self.enterColorBtn, 3, 1)
        drawTabLayout.addWidget(QLabel('Brush Size:'), 4, 0)
        drawTabLayout.addWidget(self.widthSlider, 5, 0, 1, 2)
        drawTabLayout.addWidget(QLabel('Color Brightness:'), 6, 0)
        drawTabLayout.addWidget(self.brightnessSlider, 7, 0, 1, 2)
        drawTabLayout.addWidget(QLabel('Opacity:'), 8, 0)
        drawTabLayout.addWidget(self.opacitySlider, 9, 0, 1, 2)
        drawTabLayout.addWidget(QLabel('Hardness:'),10, 0)
        drawTabLayout.addWidget(self.hardnessSlider, 11, 0, 1, 2)

        tabs.addTab(filterTab, "Filter")
        tabs.addTab(drawTab, "Draw")
        drawLayout.addWidget(tabs)

        self.gridLayout.addWidget(drawPanel, 0, 3)

    def changeSelectedColor(self, newColor):
        newLabel = QPixmap(30, 30)
        newLabel.fill(newColor)
        self.selectedColorLabel.setPixmap(newLabel)

    def createLayerPanel(self):
        """creates layer panel on the bottom right of the GUI"""
        layerPanel = QWidget(self)
        layerLayout = QVBoxLayout(layerPanel)

        tab = QTabWidget()
        layerTab = QWidget(tab)
        layerTabLayout = QGridLayout(layerTab)

        scrollArea = QScrollArea(layerTab)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)

        self.layerList = LayerList()
        scrollArea.setWidget(self.layerList)
        self.layerList.setMinimumWidth(255)
        scrollArea.setMinimumWidth(265)
        
        self.layerList.move(10, 20)
        layerTabLayout.addWidget(scrollArea, 0, 0, 1, 2)

        self.addLayerBtn = QPushButton('Add Layer')
        self.copyLayerBtn = QPushButton('Copy')
        self.delLayerBtn = QPushButton('Delete')
        self.visibilityBtn = QPushButton('Toggle Visibilibility')

        tab.addTab(layerTab, "Layers")
        layerTabLayout.addWidget(self.addLayerBtn, 1, 0)
        layerTabLayout.addWidget(self.copyLayerBtn, 1, 1)
        layerTabLayout.addWidget(self.delLayerBtn, 2, 0)
        layerTabLayout.addWidget(self.visibilityBtn, 2, 1)
        layerLayout.addWidget(tab)

        self.gridLayout.addWidget(layerPanel, 1, 3)

    def createToolbar(self):
        """creates the left-hand tool bar (similar to PS) which will include brush, hand, lasso, and other tools"""
        editTools = QToolBar('Tools')
        editTools.setMovable(False)
        # spacer widget for left
        top_spacer = QWidget()
        top_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # spacer widget for right
        bottom_spacer = QWidget()
        bottom_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        brushAct = QAction('B', self)
        brushAct.setShortcut('b')

        lassoAct = QAction('L', self)
        lassoAct.setShortcut('l')

        textAct = QAction('T', self)
        textAct.setShortcut('t')
        
        editTools.addWidget(top_spacer)
        editTools.addActions([brushAct, lassoAct, textAct])
        editTools.addWidget(bottom_spacer)
        self.addToolBar(Qt.LeftToolBarArea, editTools)

    # takes in a PIL image, transforms it into a QPixMap, and updates the image
    def updateImage(self, image):
        """
        Parameters
        ============ 
        image:
            PIL Image in any format

        Converts the given PIL image into a QPixmap, then displays is on the main image panel"""
        self.canvas.clear()
        if image is not None:
            image = utils.toPixmap(image)
        self.canvas.setPixmap(image)

    def addLayer(self, index, layer):
        """
        Parameters
        ============
        index:
            integer the index of the current selected layer
        layer:
            integer representing the number of layers created so far
        
        Adds a new layer to the project at the given index to the layer panel
        """
        widget = LayerWidget(f'Layer {layer}')
        item = QListWidgetItem()
        self.layerList.insertItem(index, item)
        self.layerList.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())
    
    def removeLayer(self, index):
        """
        removes the layer widget at the given index from the layer panel
        """
        self.layerList.takeItem(index)

    def removeAllLayers(self):
        """
        Removes all layers in the project
        """
        for _ in range(self.layerList.count()):
            self.layerList.takeItem(0)

    def connect_features(self, features):
        """
        Connects the buttons in this view to the given features (in this case will be the controller)
        """
        self.rotateAct.triggered.connect(features.rotateImages)
        self.horizFlipAct.triggered.connect(features.horizontalFlip)
        self.vertFlipAct.triggered.connect(features.verticalFlip)

        self.blurBtn.clicked.connect(features.blur)
        self.sharpenBtn.clicked.connect(features.sharpen)
        self.sepiaBtn.clicked.connect(features.sepia)
        self.grayBtn.clicked.connect(features.grayscale)
        self.mosaicBtn.clicked.connect(features.mosaic)
        self.carveBtn.clicked.connect(features.carveSeam)

        self.blurAct.triggered.connect(features.blur)
        self.sharpenAct.triggered.connect(features.sharpen)
        self.sepiaAct.triggered.connect(features.sepia)
        self.grayscaleAct.triggered.connect(features.grayscale)
        self.mosaicAct.triggered.connect(features.mosaic)

        self.addLayerBtn.clicked.connect(features.addLayer)
        self.copyLayerBtn.clicked.connect(features.copyLayer)
        self.delLayerBtn.clicked.connect(features.deleteLayer)
        self.visibilityBtn.clicked.connect(features.changeVisibility)
        self.layerList.currentRowChanged.connect(features.selectLayer)
        self.layerList.itemMoved.connect(features.rearrangeLayers)

        self.colorCircle.currentColorChanged.connect(features.updateBrush)
        self.canvas.canvasEdited.connect(features.updateBrushStroke)
        self.widthSlider.valueChanged.connect(features.updateBrushSize)
        self.brightnessSlider.valueChanged.connect(features.updateBrush)
        self.opacitySlider.valueChanged.connect(features.updateBrush)
        self.hardnessSlider.valueChanged.connect(features.updateBrush)

class LayerWidget(QWidget):
    """
    Helper class that creates a layer widget, which will be added to the LayerList widget
    Each Layer contains a name, as well as buttons for toggling its visibility and deleting the layer
    """
    def __init__(self, name, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)

        # self.visibility = QCheckBox()
        # self.visibility.setChecked(True)
        self.namelabel = QLineEdit(name)
        self.namelabel.setFrame(False)
        spacer = QSpacerItem(80, 25, QSizePolicy.Minimum, QSizePolicy.Expanding) 

        #layout.addWidget(self.visibility)
        layout.addWidget(self.namelabel)
        layout.addItem(spacer)

    def getName(self):
        return self.namelabel.text()

class LayerList(QListWidget):
    """
    Helper class that inheriting from QListWidget that reimplements some action event connections to 
    better handle layer movement and manipulation.
    taken from : https://www.riverbankcomputing.com/pipermail/pyqt/2011-June/030002.html 
    """
    itemMoved = pyqtSignal(int, int, QListWidgetItem) # Old index, new  index, item

    def __init__(self, parent=None, **args):
         super(LayerList, self).__init__(parent, **args)

         self.setAcceptDrops(True)
         self.setDragEnabled(True)
         self.setDragDropMode(QAbstractItemView.InternalMove)
         self.drag_item = None
         self.drag_row = None

    def dropEvent(self, event):
         super(LayerList, self).dropEvent(event)
         self.itemMoved.emit(self.drag_row, self.row(self.drag_item), self.drag_item)
         self.drag_item = None

    def startDrag(self, supportedActions):
         self.drag_item = self.currentItem()
         self.drag_row = self.row(self.drag_item)
         super(LayerList, self).startDrag(supportedActions)