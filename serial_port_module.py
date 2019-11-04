import os
import serial

def get_serial_port():
    return "/dev/"+os.popen("dmesg | egrep ttyACM | cut -f3 -d: | tail -n1").read().strip()

device = serial.Serial(get_serial_port(), baudrate=38400, timeout=3)

print(device)
print(device.isOpen())