import pyqtgraph as pg
import numpy as np
import gui_main
from pyqtgraph.Qt import QtGui, QtCore
import sys
import serial_port_module

class Spectrum(pg.GraphicsView):
    def __init__(self):
        pg.GraphicsView.__init__(self)


    def plot_data(self):
        self.datapoints = []
        for i in range(np.alen(serial_port_module.s.np_data[1:,0])):
            for j in range(np.alen(serial_port_module.s.np_data[1:,7])):
                self.datapoints.append({'pos': (serial_port_module.s.np_data[-1:,0], serial_port_module.s.np_data[-1,7]),
                               'brush': pg.intColor(i, 100)})
        self.plot1_graphicsView.addItem(pg.ScatterPlotItem().addPoints(self.datapoints))
        view = self.plot1_graphicsView
        scatterplot = pg.ScatterPlotItem()
        scatterplot.addPoints(self.datapoints)
        view.addItem(scatterplot)

    @QtCore.pyqtSlot(str, tuple)
    def update_data(self):
        self.plot_data()