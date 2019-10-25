#!/usr/bin/env python
import math
from functools import partial
import platform
from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import copy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as Tk
import tkinter.messagebox
from tkinter.ttk import Frame
import pandas as pd
import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons
import time
import os
import os.path
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import matplotlib
import warnings
import serial.tools.list_ports
import warnings
import datetime as dt
from matplotlib.offsetbox import AnchoredText
from multiprocessing import Process
import threading
from queue import Queue
import time
from multiprocessing import Pool, TimeoutError
import time
import os
import os
import glob
import tkinter
from tkinter import ttk


plt.style.use('seaborn-whitegrid')

home_folder = os.path.expanduser('~')

warnings.filterwarnings("ignore")


def info():
    print('module name:'), __name__
    if hasattr(os, 'getppid'):  # only available on Unix
        print('parent process:'), os.getppid()
    print('process id:'), os.getpid()


def f(t):
    return np.exp(-t) * np.cos(2*np.pi*t)


class StdRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.config(state=tkinter.NORMAL)
        self.text_space.insert("end", string)
        self.text_space.see("end")
        self.text_space.config(state=tkinter.DISABLED)


class serialPlot:
    def __init__(self, serialPort='/dev/ttyUSB0', serialBaud=38400, plotLength=100, dataNumBytes=2, numPlots=1):
        self.runAni = True
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        self.rawData = bytearray(numPlots * dataNumBytes)
        self.dataType = None
        if dataNumBytes == 2:
            self.dataType = 'h'     # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = 'f'     # 4 byte float
        self.data = []
        for i in range(numPlots):   # give an array for each type of data and store them in a list
            self.data.append(collections.deque([0] * plotLength, maxlen=plotLength))
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        self.csvData = []
        self.connected = False
        self.arduino_ports = []
        self.connectfunction()

    def stopAni(self):

        self.close()


    def connectfunction(self):
        if self.connected is False:
            try:
                print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud) + ' BAUD.')
                self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                print('Connected to ' + str(self.port) + ' at ' + str(
                    self.baud) + ' BAUD.' + ' this is the impedance device')
                self.connected = True
            except:
                try:
                    self.port = '/dev/ttyACM0'
                    print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud) + ' BAUD.')
                    self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                    print('Connected to ' + str(self.port) + ' at ' + str(
                        self.baud) + ' BAUD.' + ' this is the impedance device')
                    self.connected = True

                except:
                    try:
                        self.port = '/dev/ttyUSB1'
                        print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud) + ' BAUD.')
                        self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                        print('Connected to ' + str(self.port) + ' at ' + str(
                            self.baud) + ' BAUD.' + ' this is the impedance device')
                        self.connected = True

                    except:
                        try:
                            self.port = '/dev/ttyUSB0'
                            print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud) + ' BAUD.')
                            self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                            print('Connected to ' + str(self.port) + ' at ' + str(
                                self.baud) + ' BAUD.' + ' this is the impedance device')
                            self.connected = True

                        except:
                            try:
                                self.port = '/dev/ttyACM1'
                                print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud) + ' BAUD.')
                                self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                                print('Connected to ' + str(self.port) + ' at ' + str(
                                    self.baud) + ' BAUD.' + ' this is the impedance device')
                                self.connected = True

                            except:
                                try:
                                    self.port = '/dev/ttyUSB2'
                                    print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud) + ' BAUD.')
                                    self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                                    print('Connected to ' + str(self.port) + ' at ' + str(
                                        self.baud) + ' BAUD.' + ' this is the impedance device')
                                    self.connected = True
                                except:
                                    try:
                                        self.arduino_ports = [
                                            p.device
                                            for p in serial.tools.list_ports.comports()
                                            if 'Arduino' in p.description  # may need tweaking to match new arduinos
                                        ]
                                        self.port = serial.Serial(self.arduino_ports[0])
                                        print('Trying to connect to: ' + str(self.port) + ' at ' + str(
                                            self.baud) + ' BAUD.')
                                        print('Connected to ' + str(self.port) + ' at ' + str(
                                            self.baud) + ' BAUD.' + ' found using Arduino search method.')
                                        self.connected = True
                                    except:
                                        try:
                                            self.port = 'COM5'
                                            print('Trying to connect to: ' + str(self.port) + ' at ' + str(
                                                self.baud) + ' BAUD.')
                                            self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                                            print('Connected to ' + str(self.port) + ' at ' + str(
                                                self.baud) + ' BAUD.' + ' this is the impedance device')
                                            self.connected = True
                                        except:
                                            try:
                                                self.port = 'COM4'
                                                print('Trying to connect to: ' + str(self.port) + ' at ' + str(
                                                    self.baud) + ' BAUD.')
                                                self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
                                                print('Connected to ' + str(self.port) + ' at ' + str(
                                                    self.baud) + ' BAUD.' + ' this is the impedance device')
                                                self.connected = True
                                            except:
                                                try:
                                                    self.port = 'COM3'
                                                    print('Trying to connect to: ' + str(self.port) + ' at ' + str(
                                                        self.baud) + ' BAUD.')
                                                    self.serialConnection = serial.Serial(self.port, self.baud,
                                                                                          timeout=4)
                                                    print('Connected to ' + str(self.port) + ' at ' + str(
                                                        self.baud) + ' BAUD.' + ' this is the impedance device')
                                                    self.connected = True
                                                except:
                                                    try:
                                                        self.port = 'COM2'
                                                        print('Trying to connect to: ' + str(self.port) + ' at ' + str(
                                                            self.baud) + ' BAUD.')
                                                        self.serialConnection = serial.Serial(self.port, self.baud,
                                                                                              timeout=4)
                                                        print('Connected to ' + str(self.port) + ' at ' + str(
                                                            self.baud) + ' BAUD.' + ' this is the impedance device')
                                                        self.connected = True
                                                    except:
                                                        try:
                                                            self.port = 'COM1'
                                                            print('Trying to connect to: ' + str(
                                                                self.port) + ' at ' + str(
                                                                self.baud) + ' BAUD.')
                                                            self.serialConnection = serial.Serial(self.port, self.baud,
                                                                                                  timeout=4)
                                                            print('Connected to ' + str(self.port) + ' at ' + str(
                                                                self.baud) + ' BAUD.' + ' this is the impedance device')
                                                            self.connected = True
                                                        except:
                                                            try:
                                                                self.port = 'COM6'
                                                                print('Trying to connect to: ' + str(
                                                                    self.port) + ' at ' + str(
                                                                    self.baud) + ' BAUD.')
                                                                self.serialConnection = serial.Serial(self.port,
                                                                                                      self.baud,
                                                                                                      timeout=4)
                                                                print('Connected to ' + str(self.port) + ' at ' + str(
                                                                    self.baud) + ' BAUD.' + ' this is the impedance device')
                                                                self.connected = True
                                                            except:
                                                                self.connected = False
                                                                print("Failed to connect with any arduino")
                                                                self.serialConnection = serial.Serial()

    def reconnect(self):
        self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
        print('Connected to ' + str(self.port) + ' at ' + str(
            self.baud) + ' BAUD.' + ' this is the impedance device')

    def getConnection(self):
        return self.serialConnection.port

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)


    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText):
        currentTimer = time.clock()
        newarray = []

        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)     # the first reading will be erroneous
        self.previousTimer = currentTimer
        # timeText.set_text(str(self.plotTimer) + 'ms')
        privateData = copy.deepcopy(self.rawData[:])    # so that the 3 values in our plots will be synchronized to the same sample time
        for i in range(self.numPlots):
            data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
            value,  = struct.unpack(self.dataType, data)
            self.data[i].append(value)    # we get the latest data point and append it to our array
            lines[i].set_data(range(self.plotMaxLength), self.data[i])
            lineValueText[i].set_text('[' + lineLabel[i] + '] = ' + str(value))

        oldarray = np.array([self.data[0][-2], self.data[1][-2], self.data[2][-2], self.data[3][-2], self.data[4][-2], self.data[5][-2]])
        newarray = np.array([self.data[0][-1], self.data[1][-1], self.data[2][-1], self.data[3][-1], self.data[4][-1], self.data[5][-1]])

        if np.array_equal(oldarray, newarray) != True:
            # print([self.data[0][-1], self.data[1][-1], self.data[2][-1], self.data[3][-1], self.data[4][-1], self.data[5][-1]]) # print to see current csv file
            self.csvData.append(self.append_calculations(serialDataArray=[self.data[0][-1], self.data[1][-1], self.data[2][-1], self.data[3][-1], self.data[4][-1], self.data[5][-1]]))
            df = pd.DataFrame(self.csvData)
            df.to_csv('tmpData.csv')

    def append_calculations(self, serialDataArray):
        pi = 3.14

        data = [round(data_point, 2) for data_point in serialDataArray]

        frequency = data[0]
        real = data[1]
        imaginary = data[2]
        temperature = data[3]
        real_calibration = data[4]
        imaginary_calibration = data[5]


        calibration_magnitude = round(math.sqrt((float(real_calibration) ** 2) + (float(imaginary_calibration) ** 2)), 3)

        if calibration_magnitude != 0:
            gain_factor = (1 / 1) / (calibration_magnitude)
        else:
            gain_factor = (1 / 1) / (1)

        if real != 0:
            magnitude = round(math.sqrt((float(real) ** 2) + (float(imaginary) ** 2)), 3)
            impedance = round(1 / (gain_factor * magnitude), 3)
        else:
            magnitude = 1
            impedance = 1

        phase = 1
        phase2 = 1

        if real > 0 and imaginary > 0:  # positive positive
            phase = round(np.arctan(real / imaginary) * (180 / pi),2)

        if real < 0 and imaginary > 0:  # negative positive
            phase = round(180 + (np.arctan(real / imaginary) * (180 / pi)),2)

        if real < 0 and imaginary < 0:  # negative negative
            phase = round(180 + (np.arctan(real / imaginary) * (180 / pi)),2)

        if real > 0 and imaginary < 0:  # positive negative
            phase = round(180 + (np.arctan(real / imaginary) * (180 / pi)),2)


        if real > 0 and imaginary > 0:  # positive positive
            phase2 = round(np.arctan(real / imaginary) * (180 / pi),2)

        if real < 0 and imaginary > 0:  # negative positive
            phase2 = round(np.arctan(real / imaginary) * (180 / pi),2)

        if real < 0 and imaginary < 0:  # negative negative
            phase2 = round(np.arctan(real / imaginary) * (180 / pi),2)

        if real > 0 and imaginary < 0:  # positive negative
            phase2 = round(np.arctan(real / imaginary) * (180 / pi),2)

        resistance = round(impedance * np.cos(phase2), 2)
        reactance = round(impedance * np.sin(phase2), 2)


        appended_data = [frequency,real,imaginary,temperature,real_calibration, imaginary_calibration, calibration_magnitude, gain_factor, magnitude, impedance, phase, resistance, reactance]

        return appended_data

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True
            #print(self.rawData)

    def sendSerialData(self, data):
        self.serialConnection.write(data.encode('utf-8'))

    def close(self):
        timeStrFolderAuto = time.strftime("%Y_%m_%d")
        path = home_folder + '/impedance-auto-log/' + timeStrFolderAuto

        if not os.path.exists(path):
            print('true')
            try:
                os.makedirs(path)
            except OSError:
                print("Creation of the directory %s failed" % path)
            else:
                print("Successfully created the directory %s" % path)

        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        df = pd.DataFrame(self.csvData)
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
        df.to_csv(path + '/auto-impedance-data-' + timestr + '.csv')
        plt.savefig(path + '/auto-impedance-data-' + timestr + '.pdf')
        print('old data automatically saved to: ' + path + '/auto-impedance-data-' + timestr + '.csv')
        print('old data automatically saved to: ' + path + '/auto-impedance-data-' + timestr + '.pdf')

    def saveDataSerial(self):
        timeStrFolderSerial = time.strftime("%Y_%m_%d")
        path = home_folder + '/impedance-data/' + timeStrFolderSerial

        if not os.path.exists(path):
            print('true')
            try:
                os.makedirs(path)
            except OSError:
                print("Creation of the directory %s failed" % path)
            else:
                print("Successfully created the directory %s" % path)

        df = pd.DataFrame(self.csvData)
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
        print('data saved to: ' + path + '/impedance-data-' + timestr + '.csv')
        print('data saved to: ' + path + '/impedance-data-' + timestr + '.pdf')
        df.to_csv(path + '/impedance-data-' + timestr + '.csv')
        plt.savefig(path + '/impedance-data-' + timestr + '.pdf')

    def tmpData(self):
        df = pd.DataFrame(self.csvData)
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
        print('data tmp file has been created')
        df.to_csv('tmpData.csv')

    def removeTmpData(self):
        timeStrFolderAuto = time.strftime("%Y_%m_%d")
        path = home_folder + '/impedance-auto-log/' + timeStrFolderAuto

        if not os.path.exists(path):
            print('true')
            try:
                os.makedirs(path)
            except OSError:
                print("Creation of the directory %s failed" % path)
            else:
                print("Successfully created the directory %s" % path)

        df = pd.DataFrame(self.csvData)
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
        df.to_csv(path + '/auto-impedance-data-' + timestr + '.csv')
        plt.savefig(path + '/auto-impedance-data-' + timestr + '.pdf')
        print('old data automatically saved to: ' + path + '/auto-impedance-data-' + timestr + '.csv')
        print('old data automatically saved to: ' + path + '/auto-impedance-data-' + timestr + '.pdf')
        self.csvData = []
        self.csvData = []

    def saveAsDataSerial(self):
        timeStrFolder = time.strftime("%Y_%m_%d")
        path = home_folder + '/impedance-data/' + timeStrFolder

        if not os.path.exists(path):
            print('true')
            try:
                os.makedirs(path)
            except OSError:
                print("Creation of the directory %s failed" % path)
            else:
                print("Successfully created the directory %s" % path)

        df = pd.DataFrame(self.csvData)
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
        print('data saved to: ' + path + '/impedance-data-' + timestr + '.csv')
        print('data saved to: ' + path + '/impedance-data-' + timestr + '.pdf')
        df.to_csv(path + '/impedance-data-' + timestr + '.csv')
        plt.savefig(path + '/impedance-data-' + timestr + '.pdf')



class Window(Frame):
    def __init__(self, figure, master, SerialReference):
        Frame.__init__(self, master)
        self.onClick
        self.word = "Press any key to pause/un-pause"
        self.pause = False
        self.entry = None
        self.setPoint = None
        self.master = master        # a reference to the master window
        self.serialReference = SerialReference      # keep a reference to our serial connection so that we can use it for bi-directional communicate from this class
        self.initWindow(figure)     # initialize the window with our settings
        self.master.protocol('WM_DELETE_WINDOW', self.master.quit)

        ## Status Bar

        #self.status = Tk.Label(self.master, text='null', bd=1, relief=Tk.SUNKEN, anchor=Tk.W)
        #self.status.pack(side=Tk.BOTTOM, fill=Tk.X)
        back = Tk.Frame(self.master, bg='black')
        back.pack(side=Tk.BOTTOM, fill=Tk.X)

        text_box = tkinter.Text(back, width=40, height=5)
        text_box.pack(fill=Tk.X)
        sys.stdout = StdRedirector(text_box)
        sys.stderr = StdRedirector(text_box)

    def main(self):
        print("Std Output")
        raise ValueError("Std Error")

    def initWindow(self, figure):
        self.master.title("ISpectro")

        ## file menu at the ver top

        menu0 = Tk.Menu(self.master, relief=Tk.FLAT)
        self.master.config(menu=menu0)

        submenuFile = Tk.Menu(menu0)
        menu0.add_cascade(label='File',menu=submenuFile)

        submenuFile.add_command(label='Save',command=self.saveData)
        submenuFile.add_command(label='Save as...',command=self.saveAsData)

        submenuFile.add_separator()
        submenuFile.add_command(label='Exit',command=self.master.quit)

        submenuEdit = Tk.Menu(menu0)
        menu0.add_cascade(label='Edit', menu=submenuEdit)

        submenuView = Tk.Menu(menu0)
        menu0.add_cascade(label='View', menu=submenuView)

        submenuHelp = Tk.Menu(menu0)
        menu0.add_cascade(label='Help', menu=submenuHelp)

        submenuHelp.add_command(label='Instructions...', command=self.instructions)
        submenuHelp.add_separator()
        submenuHelp.add_command(label='About ISpectro', command=self.about)

        ## start stop menu

        menu1 = Frame(self.master)
        menu2 = Frame(self.master)
        tree = ttk.Treeview(self.master)




        menu1.pack(side=Tk.TOP,fill=Tk.X)
        menu2.pack(side=Tk.LEFT, fill=Tk.X)

        tree["columns"] = ("one")
        tree.column("#0", width=80, minwidth=80, stretch=Tk.NO)
        tree.heading("#0", text="Data", anchor=Tk.W)
        tree.pack(side=Tk.RIGHT, fill=Tk.X)


        # create out widgets in the master frame
        # self.startIcon = Tk.PhotoImage(file='startIcon.png', master=self.master)

        SendButton2 = Tk.Button(menu1, text='Start Sweep', fg='green', command=self.sendStartToMCU)
        SendButton2.pack(side=Tk.LEFT)

        SendButton31 = Tk.Button(menu1, text='Cal1', fg='blue', command=self.autoCalibrate1)
        SendButton31.pack(side=Tk.LEFT)
        SendButton32 = Tk.Button(menu1, text='Cal2', fg='blue', command=self.autoCalibrate2)
        SendButton32.pack(side=Tk.LEFT)
        SendButton33 = Tk.Button(menu1, text='Cal3', fg='blue', command=self.autoCalibrate3)
        SendButton33.pack(side=Tk.LEFT)
        SendButton34 = Tk.Button(menu1, text='Cal4', fg='blue', command=self.autoCalibrate4)
        SendButton34.pack(side=Tk.LEFT)
        SendButton35 = Tk.Button(menu1, text='Cal5', fg='blue', command=self.autoCalibrate5)
        SendButton35.pack(side=Tk.LEFT)
        SendButton36 = Tk.Button(menu1, text='Cal6', fg='blue', command=self.autoCalibrate6)
        SendButton36.pack(side=Tk.LEFT)
        SendButton37 = Tk.Button(menu1, text='Cal7', fg='blue', command=self.autoCalibrate7)
        SendButton37.pack(side=Tk.LEFT)
        SendButton38 = Tk.Button(menu1, text='Cal8', fg='blue', command=self.autoCalibrate8)
        SendButton38.pack(side=Tk.LEFT)

        SendButton4 = Tk.Button(menu1, text='LED ON', command=self.ledON) #, image=self.startIcon)
        SendButton4.pack(side=Tk.LEFT)

        SendButton5 = Tk.Button(menu1, text='Save Data', command=self.saveData)
        SendButton5.pack(side=Tk.LEFT)

        SendButton6 = Tk.Button(menu1, text='Reconnect', command=self.reconnect)
        SendButton6.pack(side=Tk.LEFT)

        SendButton7 = Tk.Button(menu1, text='Clear Data', command=self.serialReference.removeTmpData)
        SendButton7.pack(side=Tk.LEFT)

        SendButton8 = Tk.Button(menu1, text='Disconnect', command=self.serialReference.stopAni)
        SendButton8.pack(side=Tk.LEFT)

        SendButton9 = Tk.Button(menu1, text='LEADS ON', command=self.on774) #, image=self.startIcon)
        SendButton9.pack(side=Tk.LEFT)
        SendButton10 = Tk.Button(menu1, text='LEADS OFF', command=self.off774) #, image=self.startIcon)
        SendButton10.pack(side=Tk.LEFT)

        system_controls = Tk.Label(menu2, text="System Controls")
        system_controls.pack(side=Tk.TOP)



        system_controls_fields = ('Start frequency (kHz)', 'Step Size (kHz)', 'Points in sweep (ct)', 'Setting Time (ms)', 'IN-AMP Gain (1-8)' , 'RFB Setting (1-8)', 'PGA Gain (1 or 5)', 'Fly-by Setting (1-8)')
        fields = ('ID', 'dist. btw leads (cm)', 'weight (kg)', 'age (years)', 'gender (m/f)', 'species (rat/mouse)')

        def monthly_payment(entries):
            # period rate:
            r = (float(entries['dist. btw leads (cm)'].get()) / 100) / 12
            print("r", r)
            # principal loan:
            loan = float(entries['weight (kg)'].get())
            n = float(entries['age (years)'].get())
            remaining_loan = float(entries['gender (m/f)'].get())
            q = (1 + r) ** n
            monthly = r * ((q * loan - remaining_loan) / (q - 1))
            monthly = ("%8.2f" % monthly).strip()
            entries['species (rat/mouse)'].delete(0, Tk.END)
            entries['species (rat/mouse)'].insert(0, monthly)
            print("TWB: %f" % float(monthly))

        def final_balance(entries):
            # period rate:
            r = (float(entries['dist. btw leads (cm)'].get()) / 100) / 12
            print("r", r)
            # principal loan:
            loan = float(entries['dist. btw leads (cm)'].get())
            n = float(entries['dist. btw leads (cm)'].get())
            monthly = float(entries['dist. btw leads (cm)'].get())
            q = (1 + r) ** n
            remaining = q * loan - ((q - 1) / r) * monthly
            remaining = ("%8.2f" % remaining).strip()
            entries['dist. btw leads (cm)'].delete(0, Tk.END)
            entries['dist. btw leads (cm)'].insert(0, remaining)
            print("TWB: %f" % float(remaining))
            twb_label.config(text="TWB: %d" % float(remaining))
            print("ECF: %f" % float(remaining))
            ecf_label.config(text="ECF: %d" % float(remaining))
            print("ICF: %f" % float(remaining))
            icf_label.config(text="ICF: %d" % float(remaining))
            print("FFM: %f" % float(remaining))
            ffm_label.config(text="FFM: %d" % float(remaining))
            print("FM: %f" % float(remaining))
            fm_label.config(text="FM: %d" % float(remaining))

        def makeform_system_controls(menu2, system_controls_fields):
            entries = {}
            for field in system_controls_fields:
                print(field)
                row = Tk.Frame(menu2)
                lab = Tk.Label(row, width=22, text=field + ": ", anchor='w')
                ent = Tk.Entry(row)
                ent.insert(0, "0")
                row.pack(side=Tk.TOP,
                         fill=Tk.X,
                         padx=5,
                         pady=5)
                lab.pack(side=Tk.LEFT)
                ent.pack(side=Tk.RIGHT,
                         expand=Tk.YES,
                         fill=Tk.X)
                entries[field] = ent
            return entries

        ents2 = makeform_system_controls(menu2, system_controls_fields)
        b1 = Tk.Button(menu2, text='Send', command=(lambda e=ents2: final_balance(e)))
        b1.pack(side=Tk.TOP, padx=5, pady=5)


        body_comp_details = Tk.Label(menu2, text="Animal Data")
        body_comp_details.pack(side=Tk.TOP)


        def makeform(menu2, fields):
            entries = {}
            for field in fields:
                print(field)
                row = Tk.Frame(menu2)
                lab = Tk.Label(row, width=22, text=field + ": ", anchor='w')
                ent = Tk.Entry(row)
                ent.insert(0, "0")
                row.pack(side=Tk.TOP,
                         fill=Tk.X,
                         padx=5,
                         pady=5)
                lab.pack(side=Tk.LEFT)
                ent.pack(side=Tk.RIGHT,
                         expand=Tk.YES,
                         fill=Tk.X)
                entries[field] = ent
            return entries

        ents = makeform(menu2, fields)
        b2 = Tk.Button(menu2, text='Calculate Body Composition', command=(lambda e=ents: final_balance(e)))
        b2.pack(side=Tk.LEFT, padx=5, pady=5)




        # b2 = Tk.Button(menu2, text='Monthly Payment', command=(lambda e=ents: monthly_payment(e)))
        # b2.pack(side=Tk.LEFT, padx=5, pady=5)
        # b3 = Tk.Button(menu2, text='Quit', command=menu2.quit)
        # b3.pack(side=Tk.LEFT, padx=5, pady=5)

        twb_label = Tk.Label(menu2, text="TWB:")
        twb_label.pack(side=Tk.BOTTOM)

        ecf_label = Tk.Label(menu2, text="ECF:")
        ecf_label.pack(side=Tk.BOTTOM)

        icf_label = Tk.Label(menu2, text="ICF:")
        icf_label.pack(side=Tk.BOTTOM)

        ffm_label = Tk.Label(menu2, text="FFM:")
        ffm_label.pack(side=Tk.BOTTOM)

        fm_label = Tk.Label(menu2, text="FM:")
        fm_label.pack(side=Tk.BOTTOM)

        canvas = FigureCanvasTkAgg(figure, master=self.master)
        toolbar = NavigationToolbar2Tk(canvas, self.master)
        canvas.get_tk_widget().pack(fill=Tk.BOTH, expand=1)
        figure.canvas.mpl_connect('key_press_event', self.onClick)

        bottom = Frame(self.master)
        bottom.pack()

        dftarea = Tk.Label(bottom, text=self.word)
        dftarea.pack()

    def onClick(self, event):

        self.pause ^= True
        if self.pause == True:
            self.word = "Paused"
            return self.word
        else:
            self.word = "Press any key to Pause"
            return

    def reconnect(self):
        question = Tk.messagebox.askquestion('Warning','Do you really want to try to reconnect - if already connected this could cause errors. Please read status box to confirm a serial read failed error before proceeding.')
        if question == 'yes':
            print('Trying to reconnect')
            self.serialReference.reconnect()
        else:
            print('not reconnecting')

    def saveData(self):
        self.serialReference.saveDataSerial()
        # print('Save Data function complete')

    def saveAsData(self):
        self.serialReference.saveAsDataSerial()
        # print('Save Data function complete')

    def instructions(self):
        Tk.messagebox.showinfo('Instructions','1) Connect Test Subject with 4 leads 2) Click Start Sweep 3) Press File > Save')
        print('Instructions function complete')

    def about(self):
        print('function not complete')

    def sendFactorToMCU(self):
        self.serialReference.sendSerialData(self.entry.get() + '%')     # '%' is our ending marker

    def sendStartToMCU(self):
        question = Tk.messagebox.askquestion('Warning','Starting a sweep before the previous sweep is complete will create a sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting frequency sweep...')
            self.serialReference.sendSerialData('C')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting frequency sweep...')

    def autoCalibrate1(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal1 with R73 (1kohm resistor)...')
            self.serialReference.sendSerialData('D')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')
    def autoCalibrate2(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal2 with R71 (10kohm resistor)...')
            self.serialReference.sendSerialData('E')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')
    def autoCalibrate3(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal3 with R69 (100ohm resistor)...')
            self.serialReference.sendSerialData('F')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')
    def autoCalibrate4(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal4 with R67 (75ohm resistor)...')
            self.serialReference.sendSerialData('G')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')
    def autoCalibrate5(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal5 with R65 (10nF capacitor)...')
            self.serialReference.sendSerialData('H')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')
    def autoCalibrate6(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal6 RCR thorax circuit...')
            self.serialReference.sendSerialData('I')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')
    def autoCalibrate7(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal7 RCR thorax circuit...')
            self.serialReference.sendSerialData('J')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')
    def autoCalibrate8(self):
        question = Tk.messagebox.askquestion('Warning','Starting a auto-calibration sweep before the previous sweep is complete will create a auto-calibration sweep after the currently running sweep. Proceed?')
        if question == 'yes':
            self.serialReference.removeTmpData()
            print('Starting Cal8 RCR thorax circuit...')
            self.serialReference.sendSerialData('K')  # 'C' is our intiaties the beginning of the sweep marker
        else:
            print('Aborting auto-calibration frequency sweep...')

    def ledON(self):
        self.serialReference.sendSerialData('L')  # 'C' is our intiaties the beginning of the sweep marker

    def on774(self):
        self.serialReference.sendSerialData('M')  # 'C' is our intiaties the beginning of the sweep marker

    def off774(self):
        self.serialReference.sendSerialData('N')  # 'C' is our intiaties the beginning of the sweep marker


def main():

    root = Tk.Tk()
    portName = '/dev/ttyUSB0'
    baudRate = 38400
    maxPlotLength = 2000     # number of points in x-axis of real time plot
    dataNumBytes = 4        # number of bytes of 1 data point
    numPlots = 6            # number of plots in 1 graph

    s = serialPlot(portName, baudRate, maxPlotLength, dataNumBytes, numPlots)   # initializes all required variables

    if s.connected is True:
        s.readSerialStart() # starts background thread

    # plotting starts below
    pltInterval = 50    # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = maxPlotLength
    ymin = 25
    ymax = 40

    plt.ion()

    t1 = np.arange(0.0, 3.0, 0.01)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(321, xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    # ax = fig.add_subplot(321, xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title('Device Data', loc='left')
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (C)")

    ax2 = fig.add_subplot(324)
    ax2.set_title('Nyquist', loc='left')
    ax2.set_xlabel("Resistance (kOhms)")
    ax2.set_ylabel("Reactance (kOhms)")
    ax2.set_xlim(-4, 4)
    ax2.set_ylim(-1.5, 1.5)
    ax2.axis('equal')


    ax3 = fig.add_subplot(323)
    ax3.set_title('DFT', loc='left')
    ax3.set_xlabel("R")
    ax3.set_ylabel("I")
    ax3.set_xlim(-58000, 54000)
    ax3.set_ylim(-28200, 13500)
    ax3.axis('equal')


    ax4 = fig.add_subplot(326)
    ax4.set_title('Impedance', loc='left')
    ax4.set_xlabel("f (kHz)")
    ax4.set_ylabel("Z (kOhms)")
    ax4.set_xlim(0, 100)
    ax4.set_ylim(0, 2)

    ax5 = fig.add_subplot(325)
    ax5.set_title('Magnitude', loc='left')
    ax5.set_xlabel("f (kHz)")
    ax5.set_ylabel("Magnitude (raw)")
    ax5.set_xlim(0, 100)
    ax5.set_ylim(0, 30000)

    ax6 = fig.add_subplot(322)
    ax6.set_title('System Phase', loc='left')
    ax6.set_xlabel("f (kHz)")
    ax6.set_ylabel("Phase (Degrees)")
    ax6.set_xlim(0, 100)
    ax6.set_ylim(0, 360)

    ln2, = ax2.plot([], [], 'rs')
    ln3, = ax3.plot([], [], 'C1', linewidth=1.3)
    ln4, = ax4.plot([], [], 'C2', linewidth=1.3)
    ln5, = ax5.plot([], [], 'C4', linewidth=1.3)
    ln6, = ax6.plot([], [], 'C5', linewidth=1.3)

    ulim = 250  # upper limit
    llim = 0.1  # lower limit

    app = Window(fig, root, s)


    def animate(i):

        if not app.pause:
            graph_data = open('tmpData.csv', 'r').read()
            lines = graph_data.split('\n')
            frequencies = []
            reals = []
            imaginaries = []
            temperatures = []
            magnitudes = []
            impedances = []
            phases = []
            resistances = []
            reactances = []

            for line in lines:
                if len(line) > 35:
                    split_line = line.split(',')
                    #print(split_line)

                    frequency = split_line[1]
                    real = split_line[2]
                    imaginary = split_line[3]
                    temperature = split_line[4]
                    magnitude = split_line[9]
                    impedance = split_line[10]
                    phase = split_line[11]
                    resistance = split_line[12]
                    reactance = split_line[13]

                    frequencies.append(float(frequency))
                    reals.append(float(real))
                    imaginaries.append(float(imaginary))
                    temperatures.append(float(temperature))
                    magnitudes.append(float(magnitude))
                    impedances.append(float(impedance))
                    phases.append(float(phase))
                    resistances.append(float(resistance))
                    reactances.append(float(reactance))

            anchored_text = AnchoredText(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), loc=1)
            ax6.add_artist(anchored_text)
            ln2.set_data(resistances, reactances)
            # ax2.clear()
            # anchored_text = AnchoredText(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), loc=1)
            # ax2.add_artist(anchored_text)
            # ax2.axis('equal')
            # ax2.scatter(resistances, reactances, s=10, c='C3')
            # ax2.set_title('Nyquist', loc='left')
            # ax2.set_xlabel("Resistance (kOhms)")
            # ax2.set_ylabel("Reactance (kOhms)")


            ln3.set_data(reals, imaginaries)
            # ln3.set_data(reals, imaginaries)
            # ax3.clear()
            # ax3.axis('equal')
            # ax3.set_title('DFT', loc='left')
            # ax3.set_xlabel("R")
            # ax3.set_ylabel("I")
            # ax3.plot(reals, imaginaries, color='C1',linewidth=1.3)

            ln4.set_data(frequencies, impedances)
            # ax4.clear()
            # ax4.set_title('Impedance', loc='left')
            # ax4.set_xlabel("f (kHz)")
            # ax4.set_ylabel("Z (kOhms)")
            # ax4.plot(frequencies, impedances, color='C2', linewidth=1.3)


            ln5.set_data(frequencies, magnitudes)
            # ax5.clear()
            # ax5.set_title('Magnitude', loc='left')
            # ax5.set_xlabel("f (kHz)")
            # ax5.set_ylabel("Magnitude (raw)")
            # ax5.plot(frequencies, magnitudes, color='C4', linewidth=1.3)


            ln6.set_data(frequencies, phases)
            # ax6.clear()
            # ax6.set_title('System Phase', loc='left')
            # ax6.set_xlabel("f (kHz)")
            # ax6.set_ylabel("Phase (Degrees)")
            # ax6.plot(frequencies, phases, color='C6', linewidth=1.3)

    # ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))


    plt.tight_layout()

    # put our plot onto Tkinter's GUI
    lineLabel = ['Freq', 'R', 'I', 'Temp', 'Rcal', 'Ical']
    style = ['#FFFFFF', '#FFFFFF', '#FFFFFF', 'k-', '#FFFFFF', '#FFFFFF']  # linestyles for the different plots
    linewidth = [0.0, 0.0, 0.0, 1.3, 0.0, 0.0]
    timeText = ax.text(0.70, 0.95, '', transform=ax.transAxes)
    lines = []
    lineValueText = []

    for i in range(numPlots):
        lines.append(ax.plot([], [], style[i], label=lineLabel[i], linewidth=linewidth[i])[0])
        lineValueText.append(ax.text(0.1, 0.1+i*0.1, '', transform=ax.transAxes))


    ani = animation.FuncAnimation(fig, animate, interval=1000)
    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(lines, lineValueText, lineLabel, timeText), interval=pltInterval)    # fargs has to be a tuple

    plt.legend(loc="upper left")
    print('Welcome to ISpectro (ALA 2019) - this section will display current program status')
    print('--')
    print('You are connected to the impedance device at ' + s.getConnection())
    root.mainloop()   # use this instead of plt.show() since we are encapsulating everything in Tkinter
    s.close()

if __name__ == '__main__':
    # p = Pool(5)
    # p.map(main())
    info()
    main()

