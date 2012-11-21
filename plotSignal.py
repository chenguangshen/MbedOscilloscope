import serial
import matplotlib.pyplot as plt
import numpy as np
from random import *
from threading import *
from datetime import datetime
import signal
import sys
import os

serdev = '/dev/tty.usbmodemfa132'
mbed = serial.Serial(port=serdev, baudrate=115200)

def signal_handler(signal, frame):
    print 'Exiting...'
    mbed.close()
    plt.clf()
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)

class DataGen(object):
    def __init__(self, init=0):
        self.data = self.init = init
    def next(self):
        return mbed.readline()

def plot_update(axes,curdata):
    global data
    data = np.append(data, curdata)
    #print(curdata)
    #print(data)
    xmax = len(data) if len(data) > 1000 else 1000
    xmin = xmax - 1000
    ymin = -3
    ymax = 3
    axes.set_xbound(lower=xmin, upper=xmax)
    axes.set_ybound(lower=ymin, upper=ymax)
    plot_data.set_xdata(np.arange(len(data)))
    plot_data.set_ydata(np.array(data))
    axes.figure.canvas.draw()

def update_data(axes):
    #print('update called')
    global count
    global tempdata
    count = count + 1
    if count <= 200:
        #print(count)
        tempdata[count] = int(datagen.next()) / 10000.0 * 3.3
    else:
        #print(tempdata)
        plot_update(axes,tempdata)
        tempdata = [None] * 201
        count = 0
    
def userInput():
    freq = 10
    while (1):
        usercmd = raw_input("mbed>")
        if usercmd == 'exit':
            mbed.close()
            os._exit(0)
        elif usercmd.startswith('freq'):
            str = usercmd[5:]
            if (str.isdigit()):
                freq = int(str)
                if freq >= 1 and freq <= 1000:
                    mbed.write(chr(freq))
                    mbed.flush()
                else:
                    print('Sampling frequency must be in [1..1000]!')
            else:
                    print('Invalid frequency input!')
        elif usercmd == 'stop':
            #timer.interval = 1
#            plt.ion()
            timer.remove_callback(update_data, ax)
            timer.stop()
            print('stop!!!')            
        elif usercmd == 'start':
#            plt.ioff()
            print(freq)
#            timer.add_callback(update_data, ax)
#            timer.start()
        elif usercmd != '':
            print(usercmd + ': invalid command.')

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
datagen = DataGen()
data = [int(datagen.next()) / 10000.0 * 3.3]
ax.set_title('Sampling LPC11u24')
ax.set_xlim([0, 50])
tempdata = [None] * 201
count = 0
plot_data = ax.plot(data, linewidth=2, color=(0, 0, 1),)[0]
ax.figure.canvas.draw()

timer = fig.canvas.new_timer(interval=1)
timer.add_callback(update_data, ax)
timer.start()

t = Thread(target=userInput, args=())
t.start()

plt.show()