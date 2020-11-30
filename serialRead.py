import serial                                                              #Serial imported for Serial communication
import time                                                                #Required to use delay functions
# ArduinoSerial = serial.Serial('com15',9600)
ArduinoSerial = serial.Serial('COM3',9600)

for i in range(100):
    # channelSwitches = [1,0,1,0,1,0]
    # print(''.join(map(str, channelSwitches)).encode())

    ArduinoSerial.write(b'1')
    # print('write\n')
    # time.sleep(1)
    print(ArduinoSerial.readline().decode().split("\t"))

    time.sleep(1)
