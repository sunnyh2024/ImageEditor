from model import GUIEditorModel
from gui import Window
from controller import Controller
from PyQt5.QtWidgets import QApplication
import os
import sys
import qdarkstyle
from PIL import Image

"""
Main script to run for image editor
"""
if __name__ == '__main__':
    # set up the QApplication
    os.environ['QT_API'] = 'pyqt5'
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    amongus = Image.open('test/amongus.png')
    tower = Image.open('test/tower.png')
    blank = Image.new(mode="RGBA", size=(512, 512), color=(255, 255, 255, 0))

    screen_res = app.desktop().screenGeometry()
    w, h = screen_res.width(), screen_res.height()

    # initiate MCV and connect features
    window = Window(int(w*0.6), int(h*0.6))
    model = GUIEditorModel(tower)
    controller = Controller(window, model)

    # run GUI
    window.show()
    sys.exit(app.exec_())