import serial
import time

ser = serial.Serial('COM4',9600)
ser.write('#0002UHFIG1\r'.encode())
# time.sleep(0.02)
l = ser.read_until(b'\r')
l=l.decode()
print(float(l[1:]))