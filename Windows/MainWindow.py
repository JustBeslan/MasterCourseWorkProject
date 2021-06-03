import cv2
import numpy as np
import sqlite3
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QAction, QActionGroup

from Windows.ResultWindow import ResultWindow
from Models.GeometricFigures import *
from Triangulation.CloudOfPoints import CloudOfPoints
from Triangulation.CreaterTriangulation import CreaterTriangulation

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
        self.db_work()

        def db_work(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS file_info
                            (id INTEGER PRIMARY KEY,
                            path TEXT,
                            date_of_use TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS triangle_parameters
                            (file_id INTEGER NOT NULL REFERENCES file_info(id), 
                            min_height INTEGER, max_height INTEGER,
                            step_x INTEGER, step_y INTEGER,
                            max_discrepancy INTEGER)""")
        self.conn.commit()
        cursor.execute("SELECT * FROM file_info")
        file_info_all = cursor.fetchall()
        actionGroup = QActionGroup(self)
        if len(file_info_all) > 0:
            for file_info in file_info_all:
                action = QAction(f"|_№{file_info[0]}_|_{file_info[2]}_| {file_info[1]}", self)
                actionGroup.addAction(action)
                self.TriangulationMenu.addAction(action)
            actionGroup.triggered.connect(self.load_parameters)

    def update_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM file_info")
        row_count = cursor.fetchone()[0]
        cursor.execute(f"""INSERT INTO file_info VALUES (?,?,?);""",
                       (row_count + 1,
                        self.pathFileLabel.text() if len(self.pathFileLabel.text()) > 0 is not None
                        else self.user_parametersFromJSON['path to map of height'],
                        datetime.today().strftime('%d.%m.%Y %H:%M')))
        cursor.execute(f"""INSERT INTO triangle_parameters VALUES (?,?,?,?,?,?);""",
                       (row_count + 1,
                        self.user_rangeHeight[0],
                        self.user_rangeHeight[1],
                        self.user_stepXY[0],
                        self.user_stepXY[1],
                        self.user_maxDiscrepancy))
        self.conn.commit()
        if row_count == 5:
            cursor.execute(f"""DELETE FROM triangle_parameters WHERE file_id = ?""", (1,))
            cursor.execute(f"""DELETE FROM file_info WHERE id = ?""", (1,))
            cursor.execute(f"""UPDATE triangle_parameters SET file_id = file_id-1""")
            cursor.execute(f"""UPDATE file_info SET id = id-1""")
            self.conn.commit()

    def load_parameters(self, action):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM file_info WHERE id=?", (int(action.text()[3]),))
        info = cursor.fetchone()
        loadParametersQuestion, buttonYes, _ = create_question(
            title="Подтверждение",
            question=f"Вы желаете загрузить триангуляцию от {info[2]}\nдля файла {info[1]}?",
            textBtn1="Да",
            textBtn2="Нет")
        if loadParametersQuestion.clickedButton() == buttonYes:
            cursor.execute("SELECT * FROM triangle_parameters WHERE file_id=?", (info[0],))
            parameters = cursor.fetchone()
            self.minHeightSpin.setValue(parameters[1])
            self.maxHeightSpin.setValue(parameters[2])
            self.stepXSpin.setValue(parameters[3])
            self.stepYSpin.setValue(parameters[4])
            self.maxDiscrepancySpin.setValue(parameters[5])
            try:
                self.pathFileLabel.setText(info[1])
                self.load_map_file()
                QMessageBox.about(self, "Сообщение", "Параметры и изображение загружены")
            except:
                self.pathFileLabel.setText("")
                QMessageBox.critical(self, "Ошибка", f"Файла\n\n{info[1]}\n\nне существует!")
                QMessageBox.about(self, "Сообщение", "Остальные параметры загружены")

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
            self.statusTextEdit.appendPlainText("Извлечение точек для триангуляции...")
            QMessageBox.about(self, "Сообщение", "Нажмите ОК для запуска процесса извлечения точек триангуляции")
            self.map_takenPoints = CloudOfPoints(map_imageHeight=self.map_imageHeight,
                                                 stepXY=self.user_stepXY,
                                                 minDist=self.user_maxDiscrepancy)
            self.statusTextEdit.appendPlainText("Извлечение точек для триангуляции завершено")
            self.statusTextEdit.appendPlainText("Триангуляция на плоскости...")
            QMessageBox.about(self, "Сообщение", "Нажмите ОК для запуска процесса триангуляции на плоскости")
            self.map_triangulation = CreaterTriangulation(nodes=self.map_takenPoints.takenPoints)
            self.statusTextEdit.appendPlainText("Триангуляция на плоскости завершена")
            self.statusTextEdit.appendPlainText("Триангуляция в пространстве...")
            QMessageBox.about(self, "Сообщение", "Нажмите ОК для запуска процесса триангуляции в пространстве")
            self.statusTextEdit.appendPlainText("Триангуляция в пространстве завершена")
            self.update_history()
            self.open_window_show_result()

    def open_window_show_result(self):
        self.close()
        ResultWindow(user_parameters={
            "path": self.user_parametersFromJSON['path to map of height']
            if self.map_imageColor is None else self.pathFileLabel.text(),
            "range of height": self.user_rangeHeight,
            "step on the OX and OY axes": self.user_stepXY,
            "maximum residual value": self.user_maxDiscrepancy},
            originalImage=self.map_imageColor,
            map_takenPoints=self.map_takenPoints,
            triangulation=self.map_triangulation)
