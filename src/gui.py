import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PyEditor")
        self.setGeometry(100, 100, 500, 300)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setColumnStretch(0, 1)

        self.createMenuBar()
        self.createImagePanel()
        self.createDrawPanel()
        self.createLayerPanel()

    def createMenuBar(self):
        """Creates the top menu bar with the File, Image, Draw and Help Menus"""
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction("&New")
        fileMenu.addAction("&Open")
        fileMenu.addAction("&Save")
        fileMenu.addAction("&Save As")
        fileMenu.addAction("&Save Project")
        fileMenu.addAction("&Quit")

        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)
        editMenu.addAction("&Resize")

        imageMenu = QMenu("&Image", self)
        menuBar.addMenu(imageMenu)
        imageMenu.addAction("&Filter")
        imageMenu.addAction("&Copy Layer")
        imageMenu.addAction("&Remove")
        imageMenu.addAction("&Remove All")

        drawMenu = QMenu("Draw", self)
        menuBar.addMenu(drawMenu)
        drawMenu.addAction("&For Future Use")

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

        scroll = QScrollArea(filterTab)
        scroll.setWidgetResizable(True)
        scrollContent = QWidget(scroll)
        scrollLayout = QVBoxLayout(scrollContent)

        filters = ['Blur', 'Sharpen', 'Sepia', 'Grayscale', 'Mosaic', ]

        filterLayout.addWidget(scroll)

        apply = QPushButton("Apply", filterTab)
        apply.setFixedSize(75, 25)
        filterLayout.addWidget(apply)

        drawTab = QWidget()

        tabs.addTab(filterTab, "Filter")
        tabs.addTab(drawTab, "Draw")
        drawLayout.addWidget(tabs)

        self.gridLayout.addWidget(drawPanel, 0, 1)

    def createLayerPanel(self):
        layerPanel = QWidget(self)
        layerLayout = QVBoxLayout(layerPanel)

        tab = QTabWidget()

        layerTab = QWidget(tab)
        layerTabLayout = QVBoxLayout(layerTab)

        layerList = QListWidget(layerTab)
        layerList.move(10, 20)
        layerTabLayout.addWidget(layerList)

        tab.addTab(layerTab, "Layers")
        layerLayout.addWidget(tab)

        self.gridLayout.addWidget(layerPanel, 1, 1)

    def createLayerWidget(self, index):
        layer = QWidget()
        layout = QHBoxLayout(layer)
        layer.setLayout(layout)

        eye = QPushButton()
        eye.setIcon(QIcon('eye.png'))
        layout.addWidget(eye)

        layerLabel = QLabel(f'Layer {index}')
        layout.addWidget(layerLabel)

        delete = QPushButton()
        delete.setIcon(QIcon('delete.png'))
        layout.addWidget(delete)
        return layer


def test():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())


test()
