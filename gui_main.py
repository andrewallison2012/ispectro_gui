import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
import pyqtgraph as pg
import datetime as dt
import queue as Queue
import serial
from PyQt5.QtCore import QThread, QTimer, QEventLoop, pyqtSignal
import pandas as pd

port_name ="/dev/ttyACM0"
baud_rate = 38400

qtcreator_file  = "ispectro_xml.ui" # Enter file here, this is generated with qt creator or desinger
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)
pg.setConfigOptions(antialias=True)


class SerialThread(QtCore.QThread):
    my_signal = pyqtSignal()

    def __init__(self, port_name, buad_rate):
        QtCore.QThread.__init__(self)
        np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
        self.port_name = port_name
        self.buad_rate = buad_rate
        self.transmit = Queue.Queue()
        self.serial_running = True
        self.np_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.data_set = np.array([0, 1])
        self.temp_data = np.array([0, 1])

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
            gain_factor = (1 / 1000) / magnitude_cal
        else:
            gain_factor = (1 / 1000) / 1

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
        QtWidgets.QApplication.processEvents()

    def temp_processing(self, freq, temp):
        self.temp_data = np.vstack((self.temp_data, np.array([freq, temp])))
        return self.temp_data
        QtWidgets.QApplication.processEvents()

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
            if (np.array_equal(last_line, line) == False)  and (line[8] == 1.0):
                self.np_data = np.vstack((self.np_data, line))
                print(line)
                self.data_processing(line[1], line[2], line[3], line[4])
                self.temp_processing(line[0], line[7])
                self.my_signal.emit()

        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.update_status("iSpectro Loaded -- Welcome Please Press 'Connect'")

        self.plot1_graphicsView.setDownsampling(mode='peak')
        self.plot1_graphicsView.setClipToView(True)

        self.temp_graphicsView.setDownsampling(mode='peak')
        self.temp_graphicsView.setClipToView(True)

        self.plot1_graphicsView.showGrid(x=True, y=True)

        self.plot1_graphicsView.setTitle(title="Impedance Z")
        self.plot1_graphicsView.setLabel('left',text= 'Ohms (imaginary)')
        self.plot1_graphicsView.setLabel('bottom',text='Ohms (real)')

        self.temp_graphicsView.showGrid(x=True, y=True)
        self.temp_graphicsView.hideAxis('bottom')
        self.plot2_graphicsView.setTitle(title="Raw Data")
        self.plot2_graphicsView.showGrid(x=True, y=True)
        self.plot2_graphicsView.setLabel('left',text= 'Value')
        self.plot2_graphicsView.setLabel('bottom',text='Frequency (Hz)')

        # self.temp_graphicsView.setTitle(title="Internal Device Temperature")
        # self.temp_graphicsView.setLabel('bottom',text= 'Time (s.)')
        self.temp_graphicsView.setLabel('left',text='Temp (C)')

        self.start_QPushButton.clicked.connect(self.start_sweep)
        self.stop_QPushButton.clicked.connect(self.stop_sweep)
        self.connect_pushButton.clicked.connect(self.connect)

        self.apply_settings_QPushButton.clicked.connect(self.apply_settings)

        self.input_plot.setTitle(title='Input Signal')
        self.output_plot.setTitle(title='Output Signal')



    def apply_settings(self):
        self.serial_thread.write_data(f"<ADG1608_RC,{str(self.flyby_resistor_comboBox.currentIndex())}> ")
        self.update_status(f"<ADG1608_RC,{str(self.flyby_resistor_comboBox.currentIndex())}> ")

        self.serial_thread.write_data(f"<ADG1608_GAIN,{str(self.gain_resistor_comboBox.currentIndex())}> ")
        self.update_status(f"<ADG1608_GAIN,{str(self.gain_resistor_comboBox.currentIndex())}> ")

        self.serial_thread.write_data(f"<ADG1608_RFB,{str(self.fbr_comboBox.currentIndex())}> ")
        self.update_status(f"<ADG1608_RFB,{str(self.fbr_comboBox.currentIndex())}> ")

        self.serial_thread.write_data(f"<NUMBER_OF_INCREMENTS,{str(self.number_of_steps_spinBox_4.value())}> ")
        self.update_status(f"<NUMBER_OF_INCREMENTS,{str(self.number_of_steps_spinBox_4.value())}> ")

        self.serial_thread.write_data(f"<INCREMENT_FREQUENCY,0 , {str(self.step_size_spinBox.value() * 1000.0)}> ")
        self.update_status(f"<INCREMENT_FREQUENCY,0 , {str(self.step_size_spinBox.value()  * 1000.0)}> ")

        self.serial_thread.write_data(f"<SWEEP_DELAY,{str(self.settling_time_spinBox.value())}> ")
        self.update_status(f"<SWEEP_DELAY,{str(self.settling_time_spinBox.value())}> ")

        self.serial_thread.write_data(f"<PGA,{str(self.pga_comboBox.currentIndex())}> ")
        self.update_status(f"<PGA,{str(self.pga_comboBox.currentIndex())}> ")

        # self.serial_thread.write_data(f"<START_FREQUENCY,0,{str(self.start_freq_spinBox.value() * 1000.0)}> ")
        # self.update_status(f"<START_FREQUENCY,0,{str(self.start_freq_spinBox.value()  * 1000.0)}> ")

        # self.serial_thread.write_data(f"<ADG774,{str(self.flyby_calibration_comboBox.currentIndex())}> ")
        # self.update_status(f"<ADG774,{str(self.flyby_calibration_comboBox.currentIndex())}> ")


    def write(self, text):  # Handle sys.stdout.write: update display
        self.text_update.emit(text)  # Send signal to synchronise call with main thread

    def start_sweep(self):
        self.serial_thread.write_data('<RUN>')
        self.update_status("Sweep Started")

    def stop_sweep(self):
        self.serial_thread.write_data('<STOP>')
        self.update_status("Sweep Aborted")
        dataframe = pd.DataFrame(self.serial_thread.np_data)
        pd.DataFrame.to_csv(dataframe, 'tmpData.csv')

    def connect(self):
        self.serial_thread = SerialThread(port_name, baud_rate)
        self.update_status("Connected")
        self.serial_thread.start()
        self.serial_thread.serial_running = True
        self.serial_thread.my_signal.connect(self.update)

    def closeEvent(self, event):
        self.serial_thread.write_data('<ADG774,0>')
        self.serial_thread.serial_running = False

    def update_status(self, text):
        self.bottom_textBrowser.append(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S -- ') +text)

    def update_data(self):
        pass

    def update(self):
        global ptr1, spots3

        self.input_plot.clear()

        i =+ 1
        spots3 = []
        spots2 = []

        for i in range(np.alen(self.serial_thread.data_set[1:, ])):
            spots3.append({'pos': (self.serial_thread.data_set[-1:, 0], self.serial_thread.data_set[-1, 1]),
                           'brush': pg.intColor(self.serial_thread.np_data[-1:, 0]/1000, 120), 'pen': pg.mkPen(None), 'size': 3})
            spots2.append({'pos': (self.serial_thread.temp_data[-1:, 0], self.serial_thread.temp_data[-1, 1]),
                           'brush': pg.intColor(self.serial_thread.np_data[-1:, 0]/1000, 120), 'pen': pg.mkPen(None), 'size': 3})

        view = self.plot1_graphicsView
        s3 = pg.ScatterPlotItem()  ## Set pxMode=False to allow spots to transform with the view
        s3.addPoints(spots3)
        view.addItem(s3)

        view2 = self.temp_graphicsView
        s2 = pg.ScatterPlotItem()
        s2.addPoints(spots2)
        view2.addItem(s2)

        view3 = self.plot2_graphicsView
        s3 = pg.ScatterPlotItem()
        s3.addPoints(x=self.serial_thread.np_data[-1:, 0], y=self.serial_thread.np_data[-1:, 1], brush=(255, 0, 0), size=5, symbol='o')
        s3.addPoints(x=self.serial_thread.np_data[-1:, 0], y=self.serial_thread.np_data[-1:, 2], brush=(0, 0, 255), size=5, symbol='o')
        s3.addPoints(x=self.serial_thread.np_data[-1:, 0], y=self.serial_thread.np_data[-1:, 3], brush=(255, 0, 0), size=5, symbol='+')
        s3.addPoints(x=self.serial_thread.np_data[-1:, 0], y=self.serial_thread.np_data[-1:, 4], brush=(0, 0, 255), size=5, symbol='+')
        view3.addItem(s3)


        cycles_per_nano_second = ((self.serial_thread.np_data[-1:, 0])/1000)
        cycles_per_nano_second_radians = cycles_per_nano_second * np.pi * 2
        linspace_data = np.linspace(0, cycles_per_nano_second_radians, 1000)
        sin_data = np.sin(linspace_data)
        self.input_plot.plot(sin_data.flatten())



        QtWidgets.QApplication.processEvents()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

