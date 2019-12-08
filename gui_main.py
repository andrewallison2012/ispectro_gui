import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
import pyqtgraph as pg
import datetime as dt
import queue as Queue
import serial
from PyQt5.QtCore import QThread, QTimer, QEventLoop, pyqtSignal

port_name ="/dev/ttyACM0"
baud_rate = 38400



qtcreator_file  = "ispectro_xml.ui" # Enter file here, this is generated with qt creator or desinger
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

# class SerialGraphThread(QtCore.QThread):
#     signal = pyqtSignal(object)
#
#     def __init__(self, connection_object, plot1_graphicsView, *args, **kwargs):
#         QtCore.QThread.__init__(self, *args, **kwargs)
#         self.connection_object = connection_object
#         self.plot1_graphicsView = plot1_graphicsView
#         self.dataCollectionTimer = QTimer()
#         self.dataCollectionTimer.moveToThread(self)
#         self.dataCollectionTimer.timeout.connect(self.update_data)
#         self.running = True

    # def update_data(self):
    #     i =+ 1
    #     spots3 = []
    #     if self.connection_object == (2,7):
    #     # self.plot1_graphicsView.plot().setData(x=self.arduino_connection.np_data[1:,0],y=self.arduino_connection.np_data[1:,7], pen=None, symbol='x')
    #         for i in range(np.alen(self.connection_object[1:,0])):
    #             for j in range(np.alen(self.connection_object[1:,6])):
    #                 spots3.append({'pos': (self.connection_object[-1:,1], self.connection_object[-1,2]),
    #                                'brush': pg.intColor(i, 120)})
    #
    #     view = self.plot1_graphicsView.plot()
    #     s3 = pg.ScatterPlotItem()  ## Set pxMode=False to allow spots to transform with the view
    #     s3.addPoints(spots3)
    #     view.addItem(s3)
    #
    #     print('raan')
    #
    # def run(self):
    #     while self.running:
    #         self.dataCollectionTimer.start(1000)
    #         loop = QEventLoop()
    #         loop.exec_()

class SerialThread(QtCore.QThread):

    def __init__(self, port_name, buad_rate):
        QtCore.QThread.__init__(self)
        self.port_name = port_name
        self.buad_rate = buad_rate
        self.transmit = Queue.Queue()
        self.serial_running = True
        self.np_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.data_set = np.array([0, 1])

    def write_data(self, data_string):
        data = data_string.encode('utf-8')
        self.serial_connection.write(data)

    def data_processing(self, real_unknown, imaginary_unknown, real_cal, imaginary_cal):
        # function to find theta using x and y from device or calibration x and y from device
        # just pass in the real and imaginary component
        def find_angle(real, imaginary):
            pi = np.pi
            phase = 0
            theta = 0

            # phase calibration with arctangent function accounting for changes in quadrant
            if real != 0 and imaginary != 0:
                # positive and positive
                if real > 0 and imaginary > 0:  # 1st, per page 21 in AD5933 data sheet
                    theta = np.arctan(imaginary / real)
                    phase = (theta * 180) / pi
                # negative and positive
                if real < 0 and imaginary > 0:  # 2nd, per page 21 in AD5933 data sheet
                    theta = pi + np.arctan(imaginary / real)
                    phase = (theta * 180) / pi
                # negative and negative
                if real < 0 and imaginary < 0:  # 3rd, per page 21 in AD5933 data sheet
                    theta = pi + np.arctan(imaginary / real)
                    phase = (theta * 180) / pi
                # positive and negative
                if real > 0 and imaginary < 0:  # 4th, per page 21 in AD5933 data sheet
                    theta = 2 * (pi) + np.arctan(imaginary / real)
                    phase = (theta * 180) / pi

            # handle arctan function if 'real' aka 'x' component is zero
            if real == 0:
                if real == 0 and imaginary > 0:  # 1st, per page 21 in AD5933 data sheet
                    theta = pi / 2
                    phase = (theta * 180) / pi
                    print('1 and 2')
                if real == 0 and imaginary < 0:  # 4th, per page 21 in AD5933 data sheet
                    theta = (3 * pi) / 2
                    phase = (theta * 180) / pi
                    print('3 and 4')

            # handle arctan function if 'imaginary' aka 'y' component is zero
            if imaginary == 0:
                if real > 0 and imaginary == 0:  # 1st, per page 21 in AD5933 data sheet
                    theta = 0
                    phase = (theta * 180) / pi
                    print('1 and 4')
                if real < 0 and imaginary == 0:  # 4th, per page 21 in AD5933 data sheet
                    theta = pi
                    phase = (theta * 180) / pi
                    print('2 and 3')
            return theta

        # magnitude calculation with gain factor from calibration resistor
        magnitude_cal = np.sqrt((real_cal ** 2) + (imaginary_cal ** 2))

        if magnitude_cal != 0:
            gain_factor = (1 / 1) / magnitude_cal
        else:
            gain_factor = (1 / 1) / 1

        if real_unknown != 0:
            magnitude = np.sqrt((real_unknown ** 2) + (imaginary_unknown ** 2))
            impedance = 1 / (gain_factor * magnitude)
        else:
            magnitude = 1
            impedance = 1

        theta = find_angle(real_unknown, imaginary_unknown)

        # adjusting vector projection to adjust for phase angle and magnitude
        z_real = np.abs(impedance) * np.cos(theta)
        z_imaginary = np.abs(impedance) * np.sin(theta)

        string_to_print = f'calibrated impedace magnitude: {impedance}\ntheta: {theta}\nz_real: {z_real}\nz_imaginary: {z_imaginary}'
        self.data_set = np.vstack((self.data_set, np.array([z_real,z_imaginary])))
        return self.data_set
        print(string_to_print)

    def run(self):
        self.np_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        try:
            self.serial_connection = serial.Serial(self.port_name, self.buad_rate, timeout=3)
        except:
            # self.serial_running = True
            self.serial_connection = None
        if not self.serial_connection:
            print('could not open port')
            self.serial_running = False

        while self.serial_running:
            self.raw_data = bytearray(9*4)
            self.serial_connection.readinto(self.raw_data)
            line = np.frombuffer(bytes(self.raw_data), dtype='<f4')

            last_line = self.np_data[-1]
            if np.array_equal(last_line, line) == False:
                self.np_data = np.vstack((self.np_data, line))
                print(line)
                self.data_processing(line[1], line[2], line[3], line[4])

        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.update_status("iSpectro Loaded -- Welcome")
        self.plot1_graphicsView.setDownsampling(mode='peak')
        self.plot1_graphicsView.setClipToView(True)


        self.plot1_graphicsView.showGrid(x=True, y=True)
        self.plot1_graphicsView.setTitle(title="Impedance Z")
        self.plot1_graphicsView.setLabel('left',text= 'Ohms (imaginary)')
        self.plot1_graphicsView.setLabel('bottom',text='Ohms (real)')


        self.start_QPushButton.clicked.connect(self.start_sweep)
        self.stop_QPushButton.clicked.connect(self.stop_sweep)
        self.connect_pushButton.clicked.connect(self.connect)

        self.timer = pg.QtCore.QTimer()
        self.timer.start(250)
        self.timer.timeout.connect(self.update)



        # self.graph_thread = SerialGraphThread(connection_object=self.serial_thread.np_data, plot1_graphicsView=plot)
        # self.graph_thread.start()

    def write(self, text):  # Handle sys.stdout.write: update display
        self.text_update.emit(text)  # Send signal to synchronise call with main thread

    def start_sweep(self):
        self.serial_thread.write_data('<RUN>')
        self.update_status("Sweep Started")
        # self.graphthread.start()

    def stop_sweep(self):
        self.serial_thread.write_data('<STOP>')
        self.update_status("Sweep Aborted")
        self.serial_thread.serial_running = False

    def connect(self):
        self.serial_thread = SerialThread(port_name, baud_rate)
        self.serial_thread.start()

    def update_status(self, text):
        self.bottom_textBrowser.append(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S -- ') +text)

    def update_data(self):
        pass

    def update(self):
        # self.graphthread.start()


        i =+ 1
        spots3 = []
        # pi = 3.14

        # self.plot1_graphicsView.plot().setData(x=self.arduino_connection.np_data[1:,0],y=self.arduino_connection.np_data[1:,7], pen=None, symbol='x')
        for i in range(np.alen(self.serial_thread.data_set[1:,])):
            spots3.append({'pos': (self.serial_thread.data_set[-1:,0], self.serial_thread.data_set[-1,1]),
                           'brush': pg.intColor(i, 120, alpha = 20), 'pen': pg.mkPen(None)})


        view = self.plot1_graphicsView
        s3 = pg.ScatterPlotItem()  ## Set pxMode=False to allow spots to transform with the view
        s3.addPoints(spots3)
        view.addItem(s3)

        #
        # data = [round(data_point, 2) for data_point in spots3]
        #
        # frequency = data[0]
        # real = data[1]
        # imaginary = data[2]
        # real = data[3]
        # imaginary = data[4]
        # real = data[5]
        # imaginary = data[6]
        # temperature = data[7]
        # status = data[8]
        #
        # if real > 0 and imaginary > 0:  # positive positive
        #     phase = round(np.arctan(real / imaginary) * (180 / pi),2)
        #
        # if real < 0 and imaginary > 0:  # negative positive
        #     phase = round(180 + (np.arctan(real / imaginary) * (180 / pi)),2)
        #
        # if real < 0 and imaginary < 0:  # negative negative
        #     phase = round(180 + (np.arctan(real / imaginary) * (180 / pi)),2)
        #
        # if real > 0 and imaginary < 0:  # positive negative
        #     phase = round(180 + (np.arctan(real / imaginary) * (180 / pi)),2)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())