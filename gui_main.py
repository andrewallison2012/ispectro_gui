from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pyqtgraph as pg
import datetime as dt
import serial_port_module
import sys
from pyqtgraph.Qt import QtCore, QtGui
import threading
import numpy as np
import plot_module
import time

qtcreator_file  = "ispectro_xml.ui" # Enter file here, this is generated with qt creator or desinger
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

class Helper(QtCore.QObject):
    signal_changed = QtCore.pyqtSignal(str,tuple)

def get_data(helper, name):
    while True:
        t = 1
        s = 2
        time.sleep(.1)
        serial_port_module.s.read_data()
        helper.signal_changed.emit(name, (t, s))


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.arduino_connection = serial_port_module.connect_to_arduino()

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
        text = self.arduino_connection.port
        self.update_status('connected to:  '+ text)

    def start_sweep(self):
        self.arduino_connection.write_data('59330')
        self.update_status("Sweep Started")


    def start_stop(self):
        self.opened_port.write_data('59333')
        self.update_status("Sweep Aborted")

    def update_status(self, text):
        self.bottom_textBrowser.append(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S -- ') +text)

    def graph(self):
        self.arduino_connection.read_data()
        self.datapoints = []
        for i in self.arduino_connection.np_data[1:,0]:
                self.datapoints.append({'pos': (self.arduino_connection.np_data[-1:,0], self.arduino_connection.np_data[-1,7]),
                               'brush': pg.intColor(i, 100)})
        view = self.plot1_graphicsView
        scatterplot = pg.ScatterPlotItem()
        scatterplot.addPoints(self.datapoints)
        view.addItem(scatterplot)

    @QtCore.pyqtSlot(str, tuple)
    def update_data(self):
        self.graph()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    helper = Helper()
    window = MyWindow()

    helper.signal_changed.connect(window.graph, QtCore.Qt.QueuedConnection)
    threading.Thread(target=get_data, args=(helper, "910D"), daemon=True).start()
    window.show()
    sys.exit(app.exec_())
