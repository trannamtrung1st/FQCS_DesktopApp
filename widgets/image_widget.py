from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from views.image_widget import Ui_ImageWidget


class ImageWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_ImageWidget()
        self.ui.setupUi(self)

    def imshow(self, image):
        image = QImage(image.data, image.shape[1], image.shape[0],
                             QImage.Format_RGB888).rgbSwapped()
        self.ui.lblImage.setPixmap(QPixmap.fromImage(image))