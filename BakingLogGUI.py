import sys
import qdarkstyle
from qtGUI import Ui_MainWindow
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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

        # Add matplotlib widget

        self.canvasT = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvasP = MplCanvas(self, width=5, height=4, dpi=100)
        self.horizontalLayoutPlot.addWidget(self.canvasT)
        self.horizontalLayoutPlot.addWidget(self.canvasP)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = QtWidgets.QMainWindow()
    ui = BakingLogGui(MainWindow)
    MainWindow.show()
    app.exec_()
    sys.exit()
