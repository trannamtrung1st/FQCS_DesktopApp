from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Signal
from app_models.detector_config import DetectorConfig

import cv2
import os
import imutils
import numpy as np
from FQCS import detector, helper, manager
from widgets.image_widget import ImageWidget
from app import helpers
from views.test_detect_pair_screen import Ui_test_detect_pair_screen


class TestDetectPairScreen(QWidget):
    __detected_pair = None
    backscreen: Signal
    nextscreen: Signal

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_test_detect_pair_screen()
        self.__current_cfg = DetectorConfig.instance().get_current_cfg()
        self.ui.setupUi(self)
        self.build()
        self.binding()

    def build(self):
        self.backscreen = self.ui.btnBack.clicked
        self.nextscreen = self.ui.btnNext.clicked
        self.manager_changed()

    # binding
    def binding(self):
        DetectorConfig.instance().manager_changed.connect(self.manager_changed)
        self.ui.btnSaveSample.clicked.connect(self.btn_save_sample_clicked)
        self.ui.btnRetakeSample.clicked.connect(self.btn_retake_sample_clicked)

    def view_cam(self, image):
        # read image in BGR format
        self.image1 = ImageWidget()
        self.image2 = ImageWidget()
        self.image3 = ImageWidget()
        self.label_w = self.ui.screen1.width()
        self.label_h = self.ui.screen1.height()
        self.dim = (self.label_w, self.label_h)
        self.imageLayout = self.ui.screen1.parentWidget().layout()
        self.imageLayout.replaceWidget(self.ui.screen1, self.image1)
        self.imageLayout.replaceWidget(self.ui.screen2, self.image2)
        self.imageLayout.replaceWidget(self.ui.screen4, self.image3)
        self.img = image
        contour, detected, detected_pair = self.__process_pair(self.img.copy())
        img_resized = cv2.resize(self.img, self.dim)
        contour_resized = cv2.resize(contour, self.dim)
        self.image1.imshow(img_resized)
        self.image2.imshow(contour_resized)
        if detected is not None and self.__detected_pair is None:
            detected_resized = cv2.resize(detected, self.dim)
            self.image3.imshow(detected_resized)
            self.__detected_pair = detected_pair

    def manager_changed(self):
        self.__current_cfg = DetectorConfig.instance().get_current_cfg()
        if self.__current_cfg is None: return

    def __process_pair(self, image):
        manager = DetectorConfig.instance().manager
        boxes, proc = manager.extract_boxes(self.__current_cfg, image)
        final_grouped, sizes, check_group_idx, pair, split_left, split_right, image_detect = manager.detect_groups_and_checked_pair(
            self.__current_cfg, boxes, image)
        unit = self.__current_cfg["length_unit"]
        for idx, group in enumerate(final_grouped):
            for b_idx, b in enumerate(group):
                c, rect, dimA, dimB, box, tl, tr, br, bl, minx, maxx, cenx = b
                cur_size = sizes[idx][b_idx]
                lH, lW = cur_size
                helper.draw_boxes_and_sizes(image, idx, box, lH, lW, unit, tl,
                                            br)
        if (pair is not None):
            manager.check_group(check_group_idx, final_grouped)
            left, right = pair
            left, right = left[0], right[0]
            left = cv2.flip(left, 1)
            max_width = max((left.shape[0], right.shape[0]))
            temp_left = imutils.resize(left, height=max_width)
            temp_right = imutils.resize(right, height=max_width)
            detected = np.concatenate((temp_left, temp_right), axis=1)
            return image, detected, [left, right]
        return image, None, None

    def btn_save_sample_clicked(self):
        if self.__detected_pair is not None:
            left, right = self.__detected_pair
            folder_path = DetectorConfig.instance().get_current_path()
            if folder_path is None:
                folder_path = helpers.file_chooser_open_directory(self)
                DetectorConfig.instance().set_current_path(folder_path)
            left = cv2.flip(left, 1)
            cv2.imwrite(os.path.join(folder_path, detector.SAMPLE_LEFT_FILE),
                        left)
            cv2.imwrite(os.path.join(folder_path, detector.SAMPLE_RIGHT_FILE),
                        right)
            DetectorConfig.instance().get_manager().load_sample_images()
            print(f"save successful at {folder_path}")

    def btn_retake_sample_clicked(self):
        self.__detected_pair = None
        self.image3.imreset()
