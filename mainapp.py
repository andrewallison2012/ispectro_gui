import sys

from pyqtgraph.Qt import QtCore, QtGui
import threading
import numpy as np
import time

from plot import Plot2D

class Helper(QtCore.QObject):
    changedSignal = QtCore.pyqtSignal(str, tuple)

def create_data1(helper, name):
    t = np.arange(-3.0, 2.0, 0.01)
    i = 0.0
    while True:
        s = np.sin(2 * 2 * 3.1416 * t) / (2 * 3.1416 * t + i)
        time.sleep(.1)

        i = i + 0.1

def create_data2(helper, name):
    t = np.arange(-3.0, 2.0, 0.01)
    i = 0.0
    while True:
        s = np.cos(2 * 2 * 3.1416 * t) / (2 * 3.1416 * t - i)
        time.sleep(.1)
        helper.changedSignal.emit(name, (t, s))
        i = i + 0.1

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    helper = Helper()
    plot = Plot2D()
    helper.changedSignal.connect(plot.updateData, QtCore.Qt.QueuedConnection)
    threading.Thread(target=create_data1, args=(helper, "910D"), daemon=True).start()
    threading.Thread(target=create_data2, args=(helper, "MPU"), daemon=True).start()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()