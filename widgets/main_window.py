from PySide2.QtWidgets import QMainWindow
from PySide2.QtCore import Signal, QTimer
from views.main_window import Ui_MainWindow
from FQCS import detector
from FQCS.manager import FQCSManager
from app_models.detector_config import DetectorConfig
from app import helpers
import cv2
from widgets.measurement_screen import MeasurementScreen
from widgets.home_screen import HomeScreen
from widgets.test_detect_pair_screen import TestDetectPairScreen
from widgets.color_preprocess_config_screen import ColorPreprocessConfigScreen
from widgets.detection_config_screen import DetectionConfigScreen
from widgets.color_param_calibration_screen import ColorParamCalibrationScreen
from widgets.error_detect_screen import ErrorDetectScreen
from widgets.progress_screen import ProgressScreen
from widgets.asym_config_screen import AsymConfigScreen
from services.login_service import LoginService
from qasync import asyncSlot


class MainWindow(QMainWindow):
    logged_out = Signal(bool)
    loaded_config = Signal()

    def __init__(self, login_service: LoginService):
        QMainWindow.__init__(self)
        self.__login_service = login_service
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showFullScreen()
        self.detector_cfg = DetectorConfig.instance()
        self.video_camera = cv2.VideoCapture()
        self.timer = QTimer()
        self.process_cam = None

        # screen 0
        self.home_screen = HomeScreen(login_service, self)
        # screen 1
        self.detection_screen = DetectionConfigScreen(self)
        # screen 2
        self.measurement_screen = MeasurementScreen(self)
        # screen 3
        self.test_detect_pair_screen = TestDetectPairScreen(self)
        # screen 4
        self.color_preprocess_config_screen = ColorPreprocessConfigScreen(self)
        # screen 5
        self.color_param_calib_screen = ColorParamCalibrationScreen(self)
        # screen 6
        self.error_detect_screen = ErrorDetectScreen(self)
        # screen 7
        self.progress_screen = ProgressScreen(self)
        # screen 8
        self.asym_config_screen = AsymConfigScreen(self)

        self.binding()

        # add to Stacked Widget
        self.ui.centralStackWidget.addWidget(self.home_screen)
        self.ui.centralStackWidget.addWidget(self.detection_screen)
        self.ui.centralStackWidget.addWidget(self.measurement_screen)
        self.ui.centralStackWidget.addWidget(self.test_detect_pair_screen)
        self.ui.centralStackWidget.addWidget(
            self.color_preprocess_config_screen)
        self.ui.centralStackWidget.addWidget(self.color_param_calib_screen)
        self.ui.centralStackWidget.addWidget(self.error_detect_screen)
        self.ui.centralStackWidget.addWidget(self.progress_screen)
        self.ui.centralStackWidget.addWidget(self.asym_config_screen)

    # binding
    def binding(self):
        self.ui.actionExit.triggered.connect(self.exit_program)
        self.ui.actionLoadCfg.triggered.connect(self.on_load_config)
        self.ui.actionSaveCfg.triggered.connect(self.on_save_config)
        self.timer.timeout.connect(self.show_cam)
        self.ui.centralStackWidget.currentChanged.connect(self.widget_change)

        self.home_screen.action_logout.connect(self.on_logged_out)
        self.home_screen.action_edit.connect(self.change_detection_screen)
        self.home_screen.action_start.connect(self.change_progress_screen)
        self.home_screen.action_exit.connect(self.exit_program)

        self.detection_screen.backscreen.connect(self.change_home_screen)
        self.detection_screen.nextscreen.connect(
            self.change_measurement_screen)
        self.detection_screen.captured.connect(self.capture)
        self.detection_screen.camera_choosen.connect(
            lambda index: self.video_camera.open(index))

        self.measurement_screen.backscreen.connect(
            self.change_detection_screen)
        self.measurement_screen.nextscreen.connect(
            self.change_detect_pair_screen)

        self.test_detect_pair_screen.backscreen.connect(
            self.change_measurement_screen)
        self.test_detect_pair_screen.nextscreen.connect(
            self.change_color_preprocess_config_screen)

        self.color_preprocess_config_screen.backscreen.connect(
            self.change_detect_pair_screen)
        self.color_preprocess_config_screen.nextscreen.connect(
            self.change_asym_config_screen)

        self.asym_config_screen.backscreen.connect(
            self.change_color_preprocess_config_screen)
        self.asym_config_screen.nextscreen.connect(
            self.change_color_param_calib_screen)

        self.color_param_calib_screen.backscreen.connect(
            self.change_asym_config_screen)
        self.color_param_calib_screen.nextscreen.connect(
            self.change_error_detect_screen)

        self.error_detect_screen.backscreen.connect(
            self.change_color_param_calib_screen)
        self.error_detect_screen.nextscreen.connect(
            self.change_progress_screen)

        self.progress_screen.finished.connect(self.change_home_screen)
        self.progress_screen.captured.connect(self.capture)
        self.progress_screen.stopped.connect(self.stop)

        self.loaded_config.connect(self.detection_screen.load_cfg)
        self.loaded_config.connect(self.measurement_screen.load_cfg)
        # TODO: fix detector_cfg bugs in following screens before
        self.loaded_config.connect(
            self.color_preprocess_config_screen.load_cfg)
        self.loaded_config.connect(
            self.color_param_calib_screen.load_cfg)
        self.loaded_config.connect(self.error_detect_screen.load_cfg)

        return

    def on_logged_out(self, event: bool):
        # logic
        self.logged_out.emit(event)

    def show_cam(self):
        if (self.video_camera.isOpened() and self.process_cam is not None):
            _, image = self.video_camera.read()
            self.process_cam(image)

    # start/stop timer
    def control_timer(self, active):
        # if timer is stopped
        if active:
            if (not self.timer.isActive()):
                # start timer
                self.timer.start(20)
        # if timer is started
        else:
            self.timer.stop()

    # event handler
    def exit_program(self):
        self.close()

    def change_home_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(self.home_screen)

    def change_detection_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(self.detection_screen)

    def change_measurement_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(self.measurement_screen)

    def change_detect_pair_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(
            self.test_detect_pair_screen)

    def change_color_preprocess_config_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(
            self.color_preprocess_config_screen)

    def change_color_param_calib_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(
            self.color_param_calib_screen)

    def change_error_detect_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(self.error_detect_screen)

    def change_progress_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(self.progress_screen)

    def change_asym_config_screen(self):
        self.ui.centralStackWidget.setCurrentWidget(self.asym_config_screen)

    def widget_change(self):
        currentWidget = self.ui.centralStackWidget.currentWidget()
        if (currentWidget == self.detection_screen):
            self.process_cam = self.detection_screen.view_cam
            self.control_timer(True)
        elif (currentWidget == self.measurement_screen):
            self.process_cam = self.measurement_screen.view_cam
            self.control_timer(True)
        elif (currentWidget == self.color_preprocess_config_screen):
            self.color_preprocess_config_screen.view_image()
        elif (currentWidget == self.color_param_calib_screen):
            self.process_cam = self.color_param_calib_screen.view_cam
            self.control_timer(True)
        elif (currentWidget == self.test_detect_pair_screen):
            self.process_cam = self.test_detect_pair_screen.view_cam
            self.control_timer(True)
        elif (currentWidget == self.error_detect_screen):
            self.process_cam = self.error_detect_screen.view_cam
            self.control_timer(True)
        elif (currentWidget == self.progress_screen):
            self.process_cam = self.progress_screen.view_cam
            self.control_timer(True)
        elif (currentWidget == self.asym_config_screen):
            self.process_cam = self.asym_config_screen.view_cam
            self.control_timer(True)
        else:
            self.control_timer(False)

    def stop(self):
        self.control_timer(False)

    def capture(self):
        self.control_timer(True)

    @asyncSlot
    async def on_load_config(self):
        file_path = helpers.file_chooser_open_directory(self)
        if file_path is not None:
            manager = FQCSManager(config_folder=file_path)
            manager.load_sample_images()
            configs = manager.get_configs()
            for cfg in configs:
                if cfg["is_main"] == True:
                    await manager.load_model(cfg)
                    break
            self.detector_cfg.manager = manager
            self.detector_cfg.current_path = file_path
            self.loaded_config.emit()
        else:
            print("Error loading config")

    def on_save_config(self):
        configs = self.detector_cfg.manager.get_configs()
        if configs is not None:
            file_path = helpers.file_chooser_open_directory(self)
            if (file_path):
                self.detector_cfg.manager.save_config(file_path)
                self.detector_cfg.current_path = file_path
        else:
            print("No config provided")
