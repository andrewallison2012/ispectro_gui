
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
data1 = np.random.normal(size=100)
ptr1 = 0

win = pg.GraphicsWindow()
p2 = win.addPlot()
curve2 = p2.plot(data1)


def update1():
    global data1, ptr1
    data1[:-1] = data1[1:]
    data1[-1] = np.random.normal()
    ptr1 += 100
    curve2.setData(data1)
    curve2.setPos(ptr1, 0)

win.nextRow()

timer = pg.QtCore.QTimer()
timer.timeout.connect(update1)
timer.start(100)


if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
