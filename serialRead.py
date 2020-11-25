import serial                                                              #Serial imported for Serial communication
import time                                                                #Required to use delay functions
ArduinoSerial = serial.Serial('com15',9600)

for i in range(100):
    print(ArduinoSerial.readline())
    time.sleep(1)