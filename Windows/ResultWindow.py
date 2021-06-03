import cv2
import json
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QColorDialog, QMainWindow
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def choose_color(button):
    color = QColorDialog.getColor()
    if color.isValid():
        button.setStyleSheet('background: %s;' % (color.name()))


class ResultWindow(QMainWindow):

    def __init__(self,
                 user_parameters=None,
                 originalImage=None,
                 map_takenPoints=None,
                 triangulation=None):
        super(ResultWindow, self).__init__()
        self.user_parameters = user_parameters
        self.map_takenPoints = map_takenPoints
        self.map_triangulation = triangulation

        uic.loadUi('res/ResultWindow.ui', self)
        self.show()
        self.setFixedSize(self.width(), self.height())

        self.actionExit.triggered.connect(lambda: exit(0))

        self.actionShow.triggered.connect(self.show_triangulation)
        self.ColorPointsButton.clicked.connect(lambda: choose_color(self.ColorPointsButton))
        self.ColorLinesButton.clicked.connect(lambda: choose_color(self.ColorLinesButton))
        self.ColorTrianglesButton.clicked.connect(lambda: choose_color(self.ColorTrianglesButton))
        self.ColorSkeletonButton.clicked.connect(lambda: choose_color(self.ColorSkeletonButton))

        self.ShowMapOfHeightButton.clicked.connect(lambda: self.show_map_image(originalImage))
        self.infoTextEdit.setPlainText(
            f"|_1_| Абсолютный путь к файлу: {self.user_parameters['path']}\n"
            f"|_2_| Диапазон высот (в метрах): {self.user_parameters['range of height'][0]} (м) - {self.user_parameters['range of height'][1]} (м)\n"
            f"|_3_| Шаг по оси OX: {self.user_parameters['step on the OX and OY axes'][0]} пикселей\n"
            f"|_4_| Шаг по оси OY: {self.user_parameters['step on the OX and OY axes'][1]} пикселей\n"
            f"|_5_| Максимальная невязка: {self.user_parameters['maximum residual value']} пикселей")

    def show_triangulation(self):
        pass

    def show_map_image(self, map_image):
        if map_image is None:
            try:
                map_imageOriginal = cv2.imdecode(np.fromfile(self.user_parameters['path'], dtype=np.uint8),
                                                 cv2.IMREAD_UNCHANGED)
                map_image = np.array(cv2.cvtColor(src=map_imageOriginal, code=cv2.COLOR_BGR2GRAY))
            except:
                QMessageBox.critical(self, "Ошибка", f"Файла\n\n{self.user_parameters['path']}\n\nне существует!")
                return
        cv2.namedWindow("The map of height", cv2.WINDOW_NORMAL)
        cv2.imshow("The map of height", map_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
