from time import sleep, time
import serial
ser = serial.Serial('com15', 9600) # Establish the connection on a specific port
counter = 0 # Below 32 everything in ASCII is gibberish
while True:
    counter +=1
    t0 = time()
    ser.write(str.encode(str(counter))) # Convert the decimal number to ASCII then send it to the Arduino
    t1 = time()
    print(t1-t0)
    print(ser.readline())  # Read the newest output from the Arduino
    print(time()-t1)
    # sleep(.1) # Delay for one tenth of a second
    if counter == 255:
        counter = 32
    # print('counter=',counter)