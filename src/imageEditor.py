from model import GUIEditorModel
from gui import Window
from controller import Controller
from PyQt5.QtWidgets import QApplication
import os
import sys
import qdarkstyle
from PIL import Image

if __name__ == '__main__':
    # set up the QApplication
    os.environ['QT_API'] = 'pyqt5'
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    im = Image.open('amongus.png')
    blank = Image.new(mode="RGBA", size=(512, 512), color=(255, 255, 255, 0))

    # initiate MCV and connect features
    window = Window()
    model = GUIEditorModel(im)
    controller = Controller(window, model)

    # run GUI
    window.show()
    sys.exit(app.exec_())