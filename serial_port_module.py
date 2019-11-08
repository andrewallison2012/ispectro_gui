import serial
import pyudev
import sys
import copy
import struct
import collections

class connect_to_arduino:
    def __init__(self):
        self.baud = 38400
        self.operating_system = self.get_platform()
        self.timeout = 3

        self.datum_per_serial_line = 6
        self.bytes_per_datum = 4

        self.data = []
        for i in range(self.datum_per_serial_line):   # give an array for each type of data and store them in a list
            self.data.append(collections.deque([0]))

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
        return self.port

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

        self.raw_data = bytearray(self.datum_per_serial_line * self.bytes_per_datum)
        self.connection.readinto(self.raw_data)
        self.data_copy = copy.deepcopy(self.raw_data[:])
        for i in range(self.datum_per_serial_line):
            data = self.data_copy[(i*self.bytes_per_datum):(self.bytes_per_datum + (i * self.bytes_per_datum))]
            value, = struct.unpack('f', data)
            self.data[i].append(value)


    def write_data(self, data_string):
        data = data_string.encode('utf-8')
        self.connection.write(data)

    def close(self):
        self.connection.close()


s = connect_to_arduino()