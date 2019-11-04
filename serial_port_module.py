import serial
import pyudev
import sys

class connect_to_arduino:
    def __init__(self):
        self.baud = 38400
        self.operating_system = self.get_platform()
        # self.datum_per_line
        # self.bytes_per_datum
        # self.device_info
        # if self.bytes_per_datum == 2:
        #     self.data_type = 'h'
        # elif self.bytes_per_datum == 4:
        #     self.data_type = 'f'
        self.data = []

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
        self.device_info = serial.Serial(self.port, self.baud, timeout=3)
        return self.port

    def open_serial_windows(self):
        self.my_device_list = [
            serial.tools.list_ports.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description  # may need tweaking to match new arduinos
        ]
        self.port = self.my_device_list[0]
        self.device_info = serial.Serial(self.port, self.baud, timeout=3)
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

s = connect_to_arduino()