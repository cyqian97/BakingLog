import os
import sys
import time
import shutil
import qdarkstyle
from qtGUI import Ui_MainWindow
import matplotlib.pyplot as plt
from ThermocoupleFit import k_type_fit
from matplotlib.figure import Figure
from SerialManager import SerialManagerArduino, SerialManagerCombine
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        with plt.style.context("dark_background"):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class BakingLogGui(Ui_MainWindow):
    def __init__(self, mainwindow):
        # Initialize the qt designer gui
        self.mainwindow = mainwindow
        self.setupUi(mainwindow)

        # Parameters
        self.channelNum = 6  # Maximum available channels in this app
        self.maxVoltage = 3.3 # (V) arduino due analog reading maximum
        self.bitdepth = 12 # arduino due analog read bit depth
        self.t0 = 0  # To store the start time
        self.isLogging = False
        self.dataFileName = "data.txt"

        # Initialize data array
        self.channelData = [[[], []] for _ in range(self.channelNum)]
        self.pressureData = [[], []]

        # Read channel switches from file
        self.channelSwitches = self.read_channel_switches()

        # Initialize states of the checkboxes
        self.channelCheckboxes = (self.actionChannel_1, self.actionChannel_2, self.actionChannel_3,
                                  self.actionChannel_4, self.actionChannel_5, self.actionChannel_6)
        for i in range(self.channelNum):
            if self.channelSwitches[i] > 0:
                self.channelCheckboxes[i].setChecked(True)
            else:
                self.channelCheckboxes[i].setChecked(False)

        # Connect toggled signals to checkboxes
        self.actionChannel_1.toggled.connect(self.toggled_signal_generator(0))
        self.actionChannel_2.toggled.connect(self.toggled_signal_generator(1))
        self.actionChannel_3.toggled.connect(self.toggled_signal_generator(2))
        self.actionChannel_4.toggled.connect(self.toggled_signal_generator(3))
        self.actionChannel_5.toggled.connect(self.toggled_signal_generator(4))
        self.actionChannel_6.toggled.connect(self.toggled_signal_generator(5))

        # Add matplotlib widget
        self.canvasT = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvasT.axes.set_xlabel("time (s)")
        self.canvasT.axes.set_ylabel("Temperature ($^\circ$C)")
        self.canvasP = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvasP.axes.set_xlabel("time (s)")
        self.canvasP.axes.set_ylabel("Pressure (Torr)")
        self.horizontalLayoutPlot.addWidget(self.canvasT)
        self.horizontalLayoutPlot.addWidget(self.canvasP)

        self.actionStart.triggered.connect(self.start_logging)

        # Create an empty file
        with open(self.dataFileName, "w") as f:
            f.write('time\tT1\tT2\tT3\tT4\tT5\tT6\tP\n')

        self.actionSave_data.triggered.connect(self.save_file)

        # Thermocouple
        self.f = k_type_fit()
        self.gain = [64.38, 64.28, 64.33, 64.33, 64.33, 64.33]
        self.offest = [-69.42, -82.99, -76, -76, -76, -76]

    # Read channel switches from file
    def read_channel_switches(self):
        with open("channelSwitches", "rb") as f:
            return [int(f.read(1)) for _ in range(self.channelNum)]

    # Write channel switches to file
    def write_channel_switches(self, channel_switches):
        with open("channelSwitches", "wb") as f:
            for i in range(self.channelNum):
                f.write(str(channel_switches[i]).encode())

    def toggled_signal_generator(self, i):
        def toggled_signal(ischeck):
            if ischeck:
                self.channelSwitches[i] = 1
            else:
                self.channelSwitches[i] = 0
            self.write_channel_switches(self.channelSwitches)

        return toggled_signal

    def start_logging(self):
        self.isLogging = True
        if self.t0 == 0:
            self.t0 = time.time()
        self.actionStart.setText("Stop")
        self.actionStart.triggered.connect(self.stop_logging)

    def check_logging_status(self):
        return self.isLogging

    def stop_logging(self):
        self.isLogging = False
        self.actionStart.setText("Start")
        self.actionStart.triggered.connect(self.start_logging)

    # Todo: communicate with arduino, also save data in default name
    def get_arduino(self, v):
        v = v / self.maxVoltage * 2 ** self.bitdepth # convert from arduino result to real voltage (V)
        # T = self.f(v)
        t = time.time() - self.t0
        s = str(t) + '\t'
        for i in range(self.channelNum):
            if self.channelSwitches[i] > 0:
                self.channelData[i][0] += [t]
                T = self.f((v[i]-self.offest[i])/self.gain[i]) # convert to the voltage before the amplifier
                self.channelData[i][1] += [T]
                s += str(T)
            else:
                s += "-1"
            s += '\t'
        if v[-1]:
            self.pressureData[0] += [t]
            self.pressureData[1] += [v[-1]]
            s += str(v[-1])
        else:
            s += "-1"
        s += '\n'
        with open(self.dataFileName, "a") as f:
            f.write(s)

    # Todo: radio buttons and spin boxes
    def update_plot(self):
        # Clear the canvas.
        with plt.style.context("dark_background"):
            self.canvasT.axes.cla()
            for i in range(self.channelNum):
                if self.channelSwitches[i] > 0:
                    self.canvasT.axes.plot(self.channelData[i][0], self.channelData[i][1],
                                           label="channel " + str(i + 1))
            # Trigger the canvas to update and redraw.
            self.canvasT.axes.legend()
            self.canvasT.axes.set_xlabel("time (s)")
            self.canvasT.axes.set_ylabel("Temperature ($^\circ$C)")
            self.canvasT.draw()
            self.canvasP.axes.cla()
            self.canvasP.axes.plot(self.pressureData[0], self.pressureData[1])
            self.canvasP.axes.set_xlabel("time (s)")
            self.canvasP.axes.set_ylabel("Pressure (Torr)")
            self.canvasP.draw()

    def save_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self.mainwindow, "Save data", "", "Text Files (*.txt)",
                                                        options=options)
        if name[-4:].lower() != '.txt':
            name += ".txt"
        shutil.copyfile(os.path.join(os.getcwd(), self.dataFileName), name)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = QtWidgets.QMainWindow()
    ui = BakingLogGui(MainWindow)
    MainWindow.show()
    manager = SerialManagerArduino(ui.check_logging_status)
    manager.valueChanged.connect(ui.get_arduino)
    manager.update.connect(ui.update_plot)
    app.exec_()
    sys.exit()
