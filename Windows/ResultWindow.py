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

        self.actionSaveAs.triggered.connect(self.save_triangulation)

        self.ShowMapOfHeightButton.clicked.connect(lambda: self.show_map_image(originalImage))
        self.infoTextEdit.setPlainText(
            f"|_1_| Абсолютный путь к файлу: {self.user_parameters['path']}\n"
            f"|_2_| Диапазон высот (в метрах): {self.user_parameters['range of height'][0]} (м) - {self.user_parameters['range of height'][1]} (м)\n"
            f"|_3_| Шаг по оси OX: {self.user_parameters['step on the OX and OY axes'][0]} пикселей\n"
            f"|_4_| Шаг по оси OY: {self.user_parameters['step on the OX and OY axes'][1]} пикселей\n"
            f"|_5_| Максимальная невязка: {self.user_parameters['maximum residual value']} пикселей")

    def show_triangulation(self):
        if self.ParametersShowToolBox.currentIndex() == 0:
            self.map_takenPoints.show_taken_points(color='#%02x%02x%02x' % (
                self.ColorPointsButton.palette().button().color().red(),
                self.ColorPointsButton.palette().button().color().green(),
                self.ColorPointsButton.palette().button().color().blue(),
            ))
        elif self.ParametersShowToolBox.currentIndex() == 1:
            self.map_triangulation.show_2d_triangulation(color='#%02x%02x%02x' % (
                self.ColorLinesButton.palette().button().color().red(),
                self.ColorLinesButton.palette().button().color().green(),
                self.ColorLinesButton.palette().button().color().blue(),
            ))
        else:
            self.show_3d_triangulation()

    def show_3d_triangulation(self):
        colorTrianglesOnTop = self.ColorTrianglesButton.palette().button().color()
        colorSkeleton = self.ColorSkeletonButton.palette().button().color()

        triangles = self.map_triangulation.triangles
        colorsAllTriangles = np.empty(np.array(triangles).shape, dtype='U50')
        for i in range(len(triangles)):
            averageZ = 150 * max(abs(triangles[i].nodes[0].z), abs(triangles[i].nodes[1].z),
                                 abs(triangles[i].nodes[2].z)) / (
                               self.user_parameters['range of height'][1] - self.user_parameters['range of height'][0])
            colorsAllTriangles[i] = '#%02x%02x%02x' % (
                min(int(averageZ), colorTrianglesOnTop.red()),
                min(int(averageZ), colorTrianglesOnTop.green()),
                min(int(averageZ), colorTrianglesOnTop.blue()))
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        triangles = []
        for triangle in self.map_triangulation.triangles:
            triangles.append(
                ((triangle.nodes[0].x, triangle.nodes[0].y, triangle.nodes[0].z),
                 (triangle.nodes[1].x, triangle.nodes[1].y, triangle.nodes[1].z),
                 (triangle.nodes[2].x, triangle.nodes[2].y, triangle.nodes[2].z))
            )
        ax.add_collection3d(Poly3DCollection(verts=triangles,
                                             alpha=0.0 if self.ShowSkeletonRadio.isChecked() else 1.0,
                                             edgecolors='#%02x%02x%02x' % (
                                                 colorSkeleton.red(),
                                                 colorSkeleton.green(),
                                                 colorSkeleton.blue()) if not self.ShowTrianglesRadio.isChecked() else None,
                                             facecolors=colorsAllTriangles if not self.ShowSkeletonRadio.isChecked() else None))
        plt.show()

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

    def save_triangulation(self):
        try:
            triangles = {"parameters": {
                "path to map of height": self.user_parameters['path'],
                "range of height":
                    f"{self.user_parameters['range of height'][0]} {self.user_parameters['range of height'][1]}",
                "step on the OX axis": f"{self.user_parameters['step on the OX and OY axes'][0]}",
                "step on the OY axis": f"{self.user_parameters['step on the OX and OY axes'][1]}",
                "maximum residual value": f"{self.user_parameters['maximum residual value']}",
            }}
            triangles.update({"Triangle {0}".format(i): self.map_triangulation.triangles[i].ToDict()
                              for i in range(len(self.map_triangulation.triangles))})
            jsonFileName = QFileDialog.getSaveFileName(parent=self,
                                                       caption="Сохранить",
                                                       filter="JSON Files (*.json)")[0]
            if jsonFileName is not None:
                with open(jsonFileName, "w") as file:
                    json.dump(obj=triangles,
                              fp=file,
                              indent=4)
                QMessageBox.about(self, "Сообщение", f"Триангуляция сохранена успешно в {jsonFileName}")
        except:
            QMessageBox.critical(self, "Ошибка", "Ошибка при сохранениии триангуляции!")

