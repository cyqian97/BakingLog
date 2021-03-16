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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import datetime


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, y_scale="linear"):
        with plt.style.context("dark_background"):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111, yscale=y_scale)
        super(MplCanvas, self).__init__(fig)

# Mouse scrolling for axes
# def zoom_zoom(axes, base_scale=1.2):
#     def on_scroll(event):
#         if event.inaxes != axes:
#             return
#         if event.button == 'up':
#             scale = 1/base_scale
#         else:
#             scale = base_scale
#
#         mouse_y = event.ydata
#         initial_ylim = axes.get_ylim()
#
#         new_height = (initial_ylim[1] - initial_ylim[0]) * scale
#
#         rely = (initial_ylim[1] - mouse_y) / (initial_ylim[1] - initial_ylim[0])
#
#         axes.set_ylim(mouse_y - new_height * (1 - rely), mouse_y + new_height * rely)
#
#         # print()
#         # print(axes.get_ylim())
#         # print()
#
#         # axes.get_figure().draw(axes.get_figure().canvas.renderer)
#         # plt.show()
#
#     fig = axes.get_figure()
#     fig.canvas.mpl_connect('scroll_event', on_scroll)
#     return on_scroll


class BakingLogGui(Ui_MainWindow):
    def __init__(self, mainwindow):
        # Initialize the qt designer gui
        self.mainwindow = mainwindow
        self.setupUi(mainwindow)

        # Parameters
        self.channelNum = 6  # Maximum available channels in this app
        self.maxVoltage = 3.3  # (V) arduino due analog reading maximum
        self.bitdepth = 12  # arduino due analog read bit depth
        self.t0 = 0  # To store the start time
        self.isLogging = False
        self.dataFileName = "data.txt"
        # curr_time = str(datetime.datetime.now())
        # curr_time = curr_time.replace(":", ".")
        # curr_time = curr_time.replace(".", "-")
        # self.dataFileName = "data_" + curr_time + "_.txt"

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
        self.canvasT = MplCanvas(self, width=5, height=4, dpi=100, y_scale="linear")
        self.canvasT.axes.set_xlabel("time (s)")
        self.canvasT.axes.set_ylabel("Temperature ($^\circ$C)")
        # self.canvasT.axes.autoscale(False, 'y')
        toolbarT = NavigationToolbar(self.canvasT, mainwindow)
        layoutT = QtWidgets.QVBoxLayout()
        layoutT.addWidget(toolbarT)
        layoutT.addWidget(self.canvasT)

        self.canvasP = MplCanvas(self, width=5, height=4, dpi=100, y_scale="log")
        self.canvasP.axes.set_xlabel("time (s)")
        self.canvasP.axes.set_ylabel("Pressure (Torr)")
        toolbarP = NavigationToolbar(self.canvasP, mainwindow)
        layoutP = QtWidgets.QVBoxLayout()
        layoutP.addWidget(toolbarP)
        layoutP.addWidget(self.canvasP)

        # self.horizontalLayoutPlot.addWidget(layoutT)
        # self.horizontalLayoutPlot.addWidget(layoutP)

        self.horizontalLayoutPlot.addLayout(layoutT)
        self.horizontalLayoutPlot.addLayout(layoutP)

        # self.horizontalLayoutPlot.addWidget(self.canvasT)
        # self.horizontalLayoutPlot.addWidget(toolbarT)
        # self.horizontalLayoutPlot.addWidget(self.canvasP)
        # self.horizontalLayoutPlot.addWidget(toolbarP)

        # Implement a graph zooming function
        # zoom_T = zoom_zoom(self.canvasT.axes)
        # zoom_P = zoom_zoom(self.canvasP.axes)

        # self.first_update = True

        # print(isinstance(self.canvasP.axes.set_ylim(), tuple))


        self.actionStart.triggered.connect(self.start_logging)
        self.actionRefresh.triggered.connect(self.refresh)

        # Create an empty file
        with open(self.dataFileName, "w") as f:
            f.write('time\tT1\tT2\tT3\tT4\tT5\tT6\tP\n')

        self.actionSave_data.triggered.connect(self.save_file)

        # Thermocouple
        self.f = k_type_fit()
        self.gain = [6.46159613e+01, 64.85970839, 64.33, 64.33, 64.33, 64.33]
        self.offset = [-6.32907620e-02, -0.0699907, -0.076, -0.076, -0.076, -0.076]

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
        self.first_update = True

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

    def refresh(self):
        # self.first_update = True

        self.channelData = [[[], []] for _ in range(self.channelNum)]
        self.pressureData = [[], []]
        if self.check_logging_status():
            self.t0 = time.time()
        else:
            self.t0 = 0
        # print("Eels are nature's noodles")
        self.update_plot()
        with open(self.dataFileName, "w") as f:
            f.write('time\tT1\tT2\tT3\tT4\tT5\tT6\tP\n')

    def get_arduino(self, v):
        v = [vv / 2 ** self.bitdepth * self.maxVoltage for vv in v[:-1]] + [
            v[-1]]  # convert from arduino result to real voltage (V)
        # print((v[1] - self.offset[1]) / self.gain[1])
        # T = self.f(v)
        t = time.time() - self.t0
        s = str(t) + '\t'
        for i in range(self.channelNum):
            if self.channelSwitches[i] > 0:
                self.channelData[i][0] += [t]
                T = self.f((v[i] - self.offset[i]) / self.gain[i])  # convert to the voltage before the amplifier
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
            # Clear axes and save the y axis limits
            # init_ylim_T = self.canvasT.axes.get_ylim()
            self.canvasT.axes.cla()

            # This stuff deals with setting the right zoom
            # if not self.first_update:
            #     self.canvasT.axes.set_ylim(init_ylim_T[0], init_ylim_T[1])
            # self.first_update = False

            for i in range(self.channelNum):
                if self.channelSwitches[i] > 0 and len(self.channelData[i][1]) > 0:
                    self.canvasT.axes.plot(self.channelData[i][0], self.channelData[i][1],
                                           label="ch" + str(i + 1) + ": " + "%.1f" % (self.channelData[i][1][-1]) + "C")
            # Trigger the canvas to update and redraw.
            self.canvasT.axes.legend()
            self.canvasT.axes.set_xlabel("time (s)")
            self.canvasT.axes.set_ylabel("Temperature ($^\circ$C)")
            self.canvasT.draw()

            self.canvasP.axes.cla()

            if len(self.pressureData[1]) > 0:
                self.canvasP.axes.plot(self.pressureData[0], self.pressureData[1],
                                   label="P:" + "%.3e Torr" % self.pressureData[1][-1])
            # self.canvasP.axes.legend()
            self.canvasP.axes.set_xlabel("time (s)")
            self.canvasP.axes.set_ylabel("Pressure (Torr)")
            self.canvasP.axes.set_yscale("log")
            self.canvasP.draw()

            # print()
            # print(self.canvasT.axes.get_ylim())
            # print()

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
