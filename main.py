from Windows.MainWindow import ImageProcessing
from PyQt5 import QtWidgets
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ImageProcessing()
    app.exec_()
