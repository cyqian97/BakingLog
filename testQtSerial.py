import sys

from PyQt5 import QtCore, QtWidgets, QtSerialPort

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(325, 237)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(110, 20, 61, 16))
        self.label.setObjectName("label")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(90, 60, 104, 71))
        self.textEdit.setObjectName("textEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(100, 150, 75, 23))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 325, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "test window"))
        self.label.setText(_translate("MainWindow", "pyqt5 tests"))
        self.pushButton.setText(_translate("MainWindow", "test button"))


class MainWindowm(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindowm, self).__init__(*args, **kwargs)

        self.canvas = FigureCanvasQTAgg(Figure(figsize=(5, 4), dpi=100))
        self.setCentralWidget(self.canvas)

        self.axes = self.canvas.figure.subplots()

        n_data = 10
        self.xdata = list(range(n_data))
        self.ydata = [0 for i in range(n_data)]

    def update_plot(self, value):
        self.ydata = self.ydata[1:] + [value]
        self.axes.cla()
        self.axes.plot(self.xdata, self.ydata, "r")
        self.canvas.draw()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def update_text(self, value):
        self.label.setNum(value)
        self.label.adjustSize()


class SerialManager(QtCore.QObject):
    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial_port = QtSerialPort.QSerialPort("COM3")
        self.serial_port.setBaudRate(QtSerialPort.QSerialPort.Baud9600)
        self.serial_port.errorOccurred.connect(self.handle_error)
        self.serial_port.readyRead.connect(self.handle_ready_read)
        self.serial_port.open(QtCore.QIODevice.ReadWrite)

    def handle_ready_read(self):
        while self.serial_port.canReadLine():
            self.serial_port.write(b'1')
            codec = QtCore.QTextCodec.codecForName("UTF-8")
            line = codec.toUnicode(self.serial_port.readLine()).strip().strip("\x00")
            try:
                print(line)
                value = float(line)
            except ValueError as e:
                print("error", e)
            else:
                self.valueChanged.emit(value)

    def handle_error(self, error):
        if error == QtSerialPort.QSerialPort.NoError:
            return
        print(error, self.serial_port.errorString())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w1 = MainWindow()
    w1.show()

    w = MainWindowm()
    w.show()

    manager = SerialManager()
    manager.valueChanged.connect(w1.update_text)
    manager.valueChanged.connect(w.update_plot)

    sys.exit(app.exec_())