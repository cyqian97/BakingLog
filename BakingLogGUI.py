import sys
import time
import serial
import random
import qdarkstyle
from qtGUI import Ui_MainWindow
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from SerialManager import SerialManager
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        with plt.style.context("dark_background"):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class WorkerSignals(QtCore.QObject):
    update = QtCore.pyqtSignal()


class Worker(QtCore.QThread):
    def __init__(self, check_fn, body_fn, signal_fn, sleep=1):
        super(Worker, self).__init__()

        self.signals = WorkerSignals()
        self.signals.update.connect(signal_fn)
        self.check = check_fn
        self.body = body_fn
        self.sleep = sleep

    def run(self):
        print("0")
        self.arduinoSerial = serial.Serial('COM3', 9600)
        print(self.arduinoSerial.readline())  # skip the startup line
        while self.check():
            print("1")
            self.arduinoSerial.write(b'1')
            print("2")
            time.sleep(self.sleep)
            v = self.arduinoSerial.readline().decode().split("\t")
            self.body(v)
            print("3")
            self.signals.update.emit()
            time.sleep(self.sleep)


class BakingLogGui(Ui_MainWindow):
    def __init__(self, mainwindow):
        # Initialize the qt designer gui
        self.mainwindow = mainwindow
        self.setupUi(mainwindow)

        # Parameters
        self.channelNum = 6  # Maximum available channels in this app
        self.t0 = 0  # To store the start time
        self.isLogging = False

        # Connect to arduino
        # self.arduinoSerial = serial.Serial('COM3', 9600)
        # self.arduinoSerial.readline()  # skip the startup line

        self.channelSwitches = self.read_channel_switches()
        self.channelData = [[[], []] for _ in range(self.channelNum)]

        # Add matplotlib widget
        self.canvasT = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvasP = MplCanvas(self, width=5, height=4, dpi=100)
        self.horizontalLayoutPlot.addWidget(self.canvasT)
        self.horizontalLayoutPlot.addWidget(self.canvasP)

        # Todo: start and stop connect
        self.actionStart.triggered.connect(self.start_logging)

    # Read channel switches from file
    def read_channel_switches(self):
        with open("channelSwitches", "rb") as f:
            return [int(f.read(1)) for _ in range(self.channelNum)]

    # Write channel switches to file
    def write_channel_switches(self, channel_switches):
        with open("channelSwitches", "wb") as f:
            for i in range(self.channelNum):
                f.write(str(channel_switches[i]).encode())

    def start_logging(self):
        self.isLogging = True
        if self.t0 == 0:
            self.t0 = time.time()
        self.actionStart.setText("Stop")
        self.actionStart.triggered.connect(self.stop_logging)
        # Todo: move worker to init?
        # self.worker = Worker(self.check_logging_status, self.get_arduino, self.update_plot)
        # print('00')
        # self.worker.start()

    def check_logging_status(self):
        return self.isLogging

    def stop_logging(self):
        self.isLogging = False
        self.actionStart.setText("Start")
        self.actionStart.triggered.connect(self.start_logging)

    # Todo: update channels from menu, also change file

    # Todo: communicate with arduino, also save data in default name
    def get_arduino(self, v):
        t = time.time() - self.t0
        for i in range(self.channelNum):
            if self.channelSwitches[i] > 0:
                self.channelData[i][0] += [t]
                self.channelData[i][1] += [v[i]]

    # Todo: radio buttons and spin boxes
    def update_plot(self):
        # Clear the canvas.
        self.canvasT.axes.cla()
        for i in range(self.channelNum):
            if self.channelSwitches[i] > 0:
                self.canvasT.axes.plot(self.channelData[i][0], self.channelData[i][1])
        # Trigger the canvas to update and redraw.
        self.canvasT.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = QtWidgets.QMainWindow()
    ui = BakingLogGui(MainWindow)
    MainWindow.show()
    manager = SerialManager(ui.check_logging_status)
    manager.valueChanged.connect(ui.get_arduino)
    manager.update.connect(ui.update_plot)
    app.exec_()
    sys.exit()
