from calendar import c
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from colorcircle import ColorCircle
import model as model
import seamCarver as sc
import qdarkstyle
import os

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PyEditor")
        self.setWindowIcon(QIcon('icons/pythonLogo.png'))
        self.setGeometry(100, 100, 1000, 700)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setColumnStretch(0, 1)

        self.createMenuBar()
        self.createImagePanel()
        self.createDrawPanel()
        self.createLayerPanel()
        self.createToolbar()

    def createMenuBar(self):
        """Creates the top menu bar with the File, Image, Draw and Help Menus"""
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        actions = ["New", "Open", "Save", "Save As", "Save Project", "Quit"]

        for action in actions:
            fileMenu.addAction(action)
        # fileMenu.addAction("&New")
        # fileMenu.addAction("&Open")
        # fileMenu.addAction("&Save")
        # fileMenu.addAction("&Save As")
        # fileMenu.addAction("&Save Project")
        # fileMenu.addAction("&Quit")

        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)
        editMenu.addAction("&Resize")

        imageMenu = QMenu("&Image", self)
        menuBar.addMenu(imageMenu)
        imageMenu.addAction("&Filter")
        imageMenu.addAction("&Copy Layer")
        imageMenu.addAction("&Remove")
        imageMenu.addAction("&Remove All")

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

    def createImagePanel(self):
        imageLabel = QLabel(self, alignment=Qt.AlignCenter)
        pixmap = QPixmap('amongus.png')
        imageLabel.setPixmap(pixmap)
        self.gridLayout.addWidget(imageLabel, 0, 0, 3, 1)

    def createDrawPanel(self):
        drawPanel = QWidget(self)
        drawLayout = QVBoxLayout(drawPanel)
        drawPanel.setLayout(drawLayout)

        tabs = QTabWidget()

        filterTab = QWidget()
        filterLayout = QVBoxLayout(filterTab)

        scrollArea = QScrollArea(filterTab)
        scrollArea.setWidgetResizable(True)
        scrollContent = QWidget(scrollArea)
        scrollLayout = QVBoxLayout(scrollContent)

        filters = ['Blur', 'Sharpen', 'Sepia', 'Grayscale', 'Mosaic']
        for filter in filters:
            scrollItem = QPushButton(filter)
            scrollLayout.addWidget(scrollItem)
        filterLayout.addWidget(scrollArea)

        apply = QPushButton("Apply", filterTab)
        apply.setFixedSize(75, 25)
        filterLayout.addWidget(apply)

        drawTab = QWidget()
        drawTabLayout = QVBoxLayout(drawTab)
        colorLabel = QLabel('Select Color or Enter RGB')
        colorLabel.setMaximumHeight(50)
        colorInput = QLineEdit()
        colorInput.setPlaceholderText('Enter RGB')
        colorCircle = ColorCircle(self)
        colorCircle.setMinimumSize(200, 200)

        drawTabLayout.addWidget(colorLabel)
        drawTabLayout.addWidget(colorCircle)
        drawTabLayout.addWidget(colorInput)

        tabs.addTab(filterTab, "Filter")
        tabs.addTab(drawTab, "Draw")
        drawLayout.addWidget(tabs)

        self.gridLayout.addWidget(drawPanel, 0, 1)

    def createLayerPanel(self):
        layerPanel = QWidget(self)
        layerLayout = QVBoxLayout(layerPanel)

        tab = QTabWidget()
        layerTab = QWidget(tab)
        layerTabLayout = QGridLayout(layerTab)

        layerList = QListWidget(layerTab)
        layerList.move(10, 20)
        layerTabLayout.addWidget(layerList, 0, 0, 1, 2)
        layerList.addItem('testLayer 1')

        addBtn = QPushButton('Add Layer')
        addBtn.setFixedSize(75, 25)
        deleteBtn = QPushButton('Delete')
        #deleteBtn.setIcon(QIcon('icons/delete.png'))
        deleteBtn.setFixedSize(75, 25)

        tab.addTab(layerTab, "Layers")
        layerTabLayout.addWidget(addBtn, 1, 0)
        layerTabLayout.addWidget(deleteBtn, 1, 1)
        layerLayout.addWidget(tab)

        self.gridLayout.addWidget(layerPanel, 1, 1)

    def createToolbar(self):
        """creates the left-hand tool bar (similar to PS) which will include brush, hand, lasso, and other tools"""
        editTools = QToolBar('Tools')
        # spacer widget for left
        top_spacer = QWidget()
        top_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # spacer widget for right
        # you can't add the same widget to both left and right. you need two different widgets.
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
        return

    def createLayerWidget(self, index):
        layer = QWidget()
        layout = QHBoxLayout(layer)
        layer.setLayout(layout)

        eye = QPushButton()
        eye.setIcon(QIcon('icons/eye.png'))
        layout.addWidget(eye)

        layerLabel = QLabel(f'Layer {index}')
        layout.addWidget(layerLabel)
        return layer

if __name__ == '__main__':
    os.environ['QT_API'] = 'pyqt5'
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = Window()
    window.show()
    sys.exit(app.exec_())
