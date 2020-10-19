from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from views.color_param_calibration_screen import Ui_ColorParamCalibScreen

class ColorParamCalibrationScreen(QWidget):
    def __init__(self, backscreen: (), nextscreen: ()):
        QWidget.__init__(self)
        self.ui = Ui_ColorParamCalibScreen()
        self.ui.setupUi(self)

        self.bind_backscreen(backscreen=backscreen)
        self.bind_nextscreen(nextscreen=nextscreen)

    #data binding
    def bind_backscreen(self, backscreen: ()):
        self.ui.btnBack.clicked.connect(backscreen)

    def bind_nextscreen(self, nextscreen: ()):
        self.ui.btnNext.clicked.connect(nextscreen)

