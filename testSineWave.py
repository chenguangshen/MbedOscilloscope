#number = 300
#a = range(4)
#a[0] = (number>>24) & 0xff
#a[1] = (number>>16) & 0xff
#a[2] = (number>>8) & 0xff
#a[3] = number & 0xff
#print(a)
import serial
from matplotlib import *    
import matplotlib.pyplot as plt
from threading import Thread, Timer
import time

count = 0
serdev = '/dev/tty.usbmodemfa132'
mbed = serial.Serial(port=serdev, baudrate=115200)

def myfunc():
    global count
    while (1):
        v = mbed.readline()
        count = count + 1
        print(v)
        
myfunc()
mbed.close()

#print time.time()
#Timer(1, myfunc, ()).start()
#time.sleep(2)
#print time.time()
#print(count)
#mbed.close()
#t = Thread(target=myfunc, args=(mbed,))
#t.start()

#while (1):
#    usercmd = raw_input("mbed>")
#    if usercmd != '':
#        print(usercmd)
#    if usercmd == 'exit()':
#        sys.exit(0)

#    mbed.write(chr(10))
#    mbed.flush()
#mbed.close()