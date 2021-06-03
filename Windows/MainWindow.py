import cv2
import numpy as np

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QAction, QActionGroup

def create_question(title, question, textBtn1, textBtn2):
    messageBox = QMessageBox()
    messageBox.setIcon(QMessageBox.Question)
    messageBox.setWindowTitle(title)
    messageBox.setText(question)
    messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    messageBox.setDefaultButton(QMessageBox.Yes)

    buttonYes = messageBox.button(QMessageBox.Yes)
    buttonYes.setText(textBtn1)

    buttonNo = messageBox.button(QMessageBox.No)
    buttonNo.setText(textBtn2)
    messageBox.exec_()
    return messageBox, buttonYes, buttonNo


def range_color_to_range_height(oldArray, newRange):
    heights = [int(round(newRange[0] + x * (newRange[1] - newRange[0]) / 255)) for x in range(256)]
    return [[heights[oldArray[i][j]] for j in range(len(oldArray[0]))] for i in range(len(oldArray))]


class ImageProcessing(QMainWindow):
    conn = sqlite3.connect("history.db")
    user_parametersFromJSON = None
    user_rangeHeight = None
    user_stepXY = None
    user_maxDiscrepancy = None
    map_imageColor = None
    map_imageHeight = None
    map_takenPoints = None
    map_triangulation = None

    def __init__(self):
        super(ImageProcessing, self).__init__()
        uic.loadUi('res/MainWindow.ui', self)
        self.show()
        self.setFixedSize(self.width(), self.height())
        self.chooseFileButton.clicked.connect(self.choose_map_file)
        self.ExitAction.triggered.connect(lambda: exit(0))
        self.RunAction.triggered.connect(self.start_triangulation)

    def choose_map_file(self):
        fileName = QFileDialog.getOpenFileName(parent=self,
                                               caption='Open File',
                                               filter="Image (*.png *.jpg *.jpeg)")[0]
        self.pathFileLabel.setText(fileName)
        if len(fileName) > 0 and QMessageBox.question(self, "Подтверждение", f"Загрузить файл\n{fileName}?",
                                                      QMessageBox.Yes | QMessageBox.No,
                                                      QMessageBox.Yes) == QMessageBox.Yes:
            self.statusTextEdit.appendPlainText("Загрузка карты высот...")
            self.load_map_file()
            self.statusTextEdit.appendPlainText("Загрузка карты высот завершена")

    def load_map_file(self):
        map_imageOriginal = cv2.imdecode(np.fromfile(self.pathFileLabel.text(), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        self.map_imageColor = np.array(cv2.cvtColor(src=map_imageOriginal,
                                                    code=cv2.COLOR_BGR2GRAY))
        self.map_imageColor = cv2.GaussianBlur(self.map_imageColor, (5, 5), 5)

    def start_triangulation(self):
        if len(self.pathFileLabel.text()) == 0:
            QMessageBox.critical(self, "Ошибка", "Сначала загрузите файл")
        elif self.minHeightSpin.value() >= self.maxHeightSpin.value():
            QMessageBox.critical(self, "Ошибка", "Минимальная высота должна быть больше меньше максимальной высоты")
        else:
            self.user_rangeHeight = (self.minHeightSpin.value(), self.maxHeightSpin.value())
            self.user_stepXY = (self.stepXSpin.value(), self.stepYSpin.value())
            self.user_maxDiscrepancy = self.maxDiscrepancySpin.value()
            self.statusTextEdit.appendPlainText("Преобразование диапазонов...")
            QMessageBox.about(self, "Сообщение", "Нажмите ОК, чтобы начать преобразование диапазонов")
            self.map_imageHeight = np.array(range_color_to_range_height(oldArray=self.map_imageColor,
                                                                        newRange=self.user_rangeHeight))
            self.statusTextEdit.appendPlainText("Преобразование диапазонов завершено")
            self.open_window_show_result()

    def open_window_show_result(self):
        self.close()
