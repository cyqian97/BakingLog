from PyQt5 import QtCore, QtWidgets, QtSerialPort

class SerialManager(QtCore.QObject):
    valueChanged = QtCore.pyqtSignal(list)
    update = QtCore.pyqtSignal()

    def __init__(self, check_fn, parent=None):
        super().__init__(parent)
        self.serial_port = QtSerialPort.QSerialPort("COM15")
        self.serial_port.setBaudRate(QtSerialPort.QSerialPort.Baud9600)
        self.serial_port.errorOccurred.connect(self.handle_error)
        self.serial_port.readyRead.connect(self.handle_ready_read)
        self.serial_port.open(QtCore.QIODevice.ReadWrite)
        self.check = check_fn

    def handle_ready_read(self):
        while self.serial_port.canReadLine():
            self.serial_port.write(b'1')
            codec = QtCore.QTextCodec.codecForName("UTF-8")
            line = codec.toUnicode(self.serial_port.readLine()).strip().strip("\x00")
            line = line.split("\t")
            try:
                value = [float(t) for t in line]
            except ValueError as e:
                print("error", e)
            else:
                if self.check():
                    self.valueChanged.emit(value)
                    self.update.emit()

    def handle_error(self, error):
        if error == QtSerialPort.QSerialPort.NoError:
            return
        print(error, self.serial_port.errorString())