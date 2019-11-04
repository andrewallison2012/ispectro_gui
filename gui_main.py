import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg


qtcreator_file  = "ispectro_xml.ui" # Enter file here, this is generated with qt creator or desinger
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # sets the plots y max
        # self.plot1_graphicsView.setYRange(min=0, max=100)

        # sets data for plot
        self.plot1_graphicsView.plot()
        self.data = np.empty(100)
        self.ptr  = 0

        # print start after clicking start
        self.start_QPushButton.clicked.connect(self.update_status)

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(50)

    # testing
    # print start after clicking start function
    def update_status(self):
        start_text = 'Sweep Started'
        self.bottom_textBrowser.setText(start_text)

    def update_data(self):
        self.data[self.ptr] = np.random.normal()
        self.ptr += 1
        if self.ptr >= self.data.shape[0]:
            tmp = self.data
            self.data = np.empty(self.data.shape[0] * 2)
            self.data[:tmp.shape[0]] = tmp
        self.plot1_graphicsView.plot().setData(self.data[:self.ptr])

        text = self.sweep_count_spinBox.text()
        self.bottom_textBrowser.setText(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())