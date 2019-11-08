import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import datetime as dt
import serial_port_module as spm


qtcreator_file  = "ispectro_xml.ui" # Enter file here, this is generated with qt creator or desinger
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.update_status("iSpectro Loaded\nWelcome")

        # sets the plots y max
        # self.plot1_graphicsView.setYRange(min=0, max=100)

        # sets data for plot
        self.plot1_graphicsView.setDownsampling(mode='peak')
        self.plot1_graphicsView.setClipToView(True)

        # empty plot set up
        self.plot1_graphicsView.plot()

        # empty data array setup
        self.data = np.empty(100)
        self.ptr = 0

        # print start after clicking start
        self.start_QPushButton.clicked.connect(self.start_sweep)
        self.stop_QPushButton.clicked.connect(lambda: self.update_status("Sweep Stopped"))

        # refresh timer creation
        self.timer = pg.QtCore.QTimer()
        self.timer.start(50)

        self.connect_pushButton.clicked.connect(self.connect)

    # testing
    # print start after clicking start function

    def connect(self):
        self.arduino_connection = spm.connect_to_arduino()

        text = self.arduino_connection.port
        self.update_status('connected to:  '+ text)

    def start_sweep(self):
        self.arduino_connection.write_data('59330')
        self.update_status("Sweep Started")
        self.timer.timeout.connect(self.update_data)

    def update_status(self, text):
        self.bottom_textBrowser.append(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S -- ') +text)

    def update_data(self):
        self.arduino_connection.read_data()
        self.plot1_graphicsView.plot().setData(x=self.arduino_connection.np_data[1:,1],y=self.arduino_connection.np_data[1:,2])


        # # self.data[self.ptr] = np.random.normal()
        # self.data[self.ptr] = np.array([self.arduino_connection.data[0][self.ptr]])
        # self.ptr += 1
        # if self.ptr >= self.data.shape[0]:
        #      tmp = self.data
        #      self.data = np.empty(self.data.shape[0] * 2)
        #      self.data[:tmp.shape[0]] = tmp
        # self.plot1_graphicsView.plot().setData(self.data[:self.ptr])



        # dataX = np.array([self.arduino_connection.data[0][1]])
        # dataY = np.array([self.arduino_connection.data[1][1]])
        # print(dataX)
        # print(dataY)
        # self.plot1_graphicsView.plot().setData(x=dataX, y=dataY)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())