import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
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

        # sets data for plot
        self.plot1_graphicsView.setDownsampling(mode='peak')
        self.plot1_graphicsView.setClipToView(True)

        plot = self.plot1_graphicsView.plot()
        # empty data array setup
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
        self.connect()

    def connect(self):
        self.arduino_connection = spm.connect_to_arduino()
        text = self.arduino_connection.port
        self.update_status('connected to:  '+ text)

    def start_sweep(self):
        self.arduino_connection.write_data('59330')
        self.update_status("Sweep Started")
        self.timer.timeout.connect(self.update_data)

    def start_stop(self):
        self.arduino_connection.write_data('59333')
        self.update_status("Sweep Aborted")

    def update_status(self, text):
        self.bottom_textBrowser.append(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S -- ') +text)

    def update_data(self):
        self.arduino_connection.read_data()
        i =+ 1
        spots3 = []
        # self.plot1_graphicsView.plot().setData(x=self.arduino_connection.np_data[1:,0],y=self.arduino_connection.np_data[1:,7], pen=None, symbol='x')
        for i in range(np.alen(self.arduino_connection.np_data[1:,0])):
            for j in range(np.alen(self.arduino_connection.np_data[1:,7])):
                spots3.append({'pos': (self.arduino_connection.np_data[-1:,0], self.arduino_connection.np_data[-1,7]),
                               'brush': pg.intColor(i, 100)})

        view = self.plot1_graphicsView
        s3 = pg.ScatterPlotItem()  ## Set pxMode=False to allow spots to transform with the view
        s3.addPoints(spots3)
        view.addItem(s3)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())