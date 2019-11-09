import serial
import pyudev
import sys
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class connect_to_arduino:
    def __init__(self):
        self.datum_per_serial_line = 7
        self.bytes_per_datum = 4
        self.baud = 38400
        self.operating_system = self.get_platform()
        self.timeout = 3
        self.data = []
        self.np_data = np.array([1,2,3,4,5,6,7,8])
        if self.operating_system == 'linux':
            self.open_serial_linux()
        elif self.operating_system == 'Windows':
            self.open_serial_windows(self)

    def open_serial_linux(self):
        self.context = pyudev.Context()
        self.my_device_list = []
        for device in self.context.list_devices(subsystem='tty', ID_BUS='usb'):
            self.my_device_list.append(device.device_node)
        self.port = self.my_device_list[0]
        self.connection = serial.Serial(self.port, self.baud, timeout=self.timeout)

    def open_serial_windows(self):
        self.my_device_list = [
            serial.tools.list_ports.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description  # may need tweaking to match new arduinos
        ]
        self.port = self.my_device_list[0]
        self.connection = serial.Serial(self.port, self.baud, timeout=self.timeout)
        return self.port

    def get_platform(self):
        self.platforms = {
            'linux1': 'Linux',
            'linux2': 'Linux',
            'darwin': 'OS X',
            'win32': 'Windows'
        }
        if sys.platform not in self.platforms:
            return sys.platform

        return self.platforms[sys.platform]

    def read_data(self):
        self.raw_data = bytearray(self.datum_per_serial_line * self.bytes_per_datum) # constructs a byte array object
        self.connection.readinto(self.raw_data) # reads serial data into byte array object
        line = np.frombuffer(bytes(self.raw_data), dtype='<f4')
        admittance = 0.0
        last_line = self.np_data[-1]
        if np.array_equal(last_line,line) == False:
            calibration_magnitude = np.round(np.sqrt((line[3] ** 2) + (line[4] ** 2)), 3)
            print(calibration_magnitude)
            if calibration_magnitude != 0.0:
                gain_factor = (1 / 1) / (calibration_magnitude)
                print(gain_factor)
                magnitude = np.round(np.sqrt((line[1] ** 2) + (line[2] ** 2)), 3)
                print(magnitude)
                admittance = np.round((gain_factor * magnitude), 3)
                print(admittance)
                admittance_array = np.array([admittance])
            line = np.hstack((line, admittance))
            self.np_data = np.vstack((self.np_data, line))

    def write_data(self, data_string):
        data = data_string.encode('utf-8')
        self.connection.write(data)

    def close(self):
        self.connection.close()

s = connect_to_arduino()