import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
import pyqtgraph as pg
import datetime as dt

from PyQt5.QtWidgets import QTextEdit

import serial_port_module as spm
import queue as Queue
import serial
import time

port_name ="/dev/ttyACM0"
baud_rate = 38400




qtcreator_file  = "ispectro_xml.ui" # Enter file here, this is generated with qt creator or desinger
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

# Custom text box, catching keystrokes
class MyTextBox(QTextEdit):
    def __init__(self, *args):
        QTextEdit.__init__(self, *args)

class SerialThread(QtCore.QThread):
    def __init__(self, port_name, buad_rate):
        QtCore.QThread.__init__(self)
        self.port_name = port_name
        self.buad_rate = buad_rate
        self.transmit = Queue.Queue()
        self.serial_running = True



    def serial_out(self, data_to_send):
        self.transmit.put(data_to_send)

    def serial_in(self, data_to_read):
        display(data_to_read)

    def run(self):
        self.np_data = np.array([1, 2, 3, 4, 5, 6, 7])
        try:
            self.serial_connection = serial.Serial(self.port_name, self.buad_rate, timeout=3)
            # time.sleep(3 *1.2)
            # self.serial_connection.flushInput()
        except:
            self.serial_connection = None
        if not self.serial_connection:
            print('could not open port')
            self.serial_running = False

        while self.serial_running:

            self.raw_data = bytearray(7*4)
            self.serial_connection.readinto(self.raw_data)
            line = np.frombuffer(bytes(self.raw_data), dtype='<f4')

            last_line = self.np_data[-1]
            if np.array_equal(last_line, line) == False:
                self.np_data = np.vstack((self.np_data, line))
                print(line)
                print(self.raw_data)

        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)



        self.setupUi(self)
        self.serial_thread = SerialThread(port_name, baud_rate)
        self.serial_thread.start()
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

    def write(self, text):  # Handle sys.stdout.write: update display
        self.text_update.emit(text)  # Send signal to synchronise call with main thread

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

        i =+ 1
        spots3 = []
        # self.plot1_graphicsView.plot().setData(x=self.arduino_connection.np_data[1:,0],y=self.arduino_connection.np_data[1:,7], pen=None, symbol='x')
        for i in range(np.alen(self.serial_thread.np_data[1:,0])):
            for j in range(np.alen(self.serial_thread.np_data[1:,6])):
                spots3.append({'pos': (self.serial_thread.np_data[-1:,1], self.serial_thread.np_data[-1,2]),
                               'brush': pg.intColor(i, 120)})

        view = self.plot1_graphicsView
        s3 = pg.ScatterPlotItem()  ## Set pxMode=False to allow spots to transform with the view
        s3.addPoints(spots3)
        view.addItem(s3)



if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())