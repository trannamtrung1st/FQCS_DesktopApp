from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Signal

from views.home_screen import Ui_HomeScreen
from services.identity_service import IdentityService


class HomeScreen(QWidget):
    action_edit: Signal
    action_start: Signal
    action_exit: Signal
    action_logout = Signal(bool)

    def __init__(self, identity_service: IdentityService, parent=None):
        QWidget.__init__(self, parent)
        self.__identity_service = identity_service
        self.ui = Ui_HomeScreen()
        self.ui.setupUi(self)
        self.action_edit = self.ui.btnEditConfig.clicked
        self.action_start = self.ui.btnStart.clicked
        self.action_exit = self.ui.btnExit.clicked
        self.binding()

    # data binding
    def binding(self):
        self.ui.btnLogout.clicked.connect(self.log_out)
        return

    def log_out(self, event: bool):
        self.action_logout.emit(event)
        self.__identity_service.log_out()
