import serial
import matplotlib.pyplot as plt
import numpy as np
from threading import *
import signal
import sys
import os
from Tkinter import *

freq = 1000
buffersize = 2000
tempdata = [[None] * buffersize, [None] * buffersize, [None] * buffersize]
count = [0] * 3
data = [None] * 3
ax = [None] * 3
plot_data = [None] * 3

serdev = '/dev/tty.usbmodemfa132'
mbed = serial.Serial(port=serdev, baudrate=230400)

def signal_handler(signal, frame):
    print 'Exiting...'
    mbed.write('p');
    mbed.flush() 
    mbed.close()
    plt.clf()
    os._exit(0)

class DataGen(object):
    def __init__(self, init=0):
        self.data = self.init = init
    def next(self):
        return [mbed.read(), mbed.readline()]

def plot_update(index):
    #print('update figure' + str(index + 1))
    data[index] = np.append(data[index], tempdata[index])
    xmax = len(data[index]) if len(data[index]) > freq else freq
    xmin = xmax - freq
    ymin = -3
    ymax = 3
    ax[index].set_xbound(lower=xmin, upper=xmax)
    ax[index].set_ybound(lower=ymin, upper=ymax)
    plot_data[index].set_xdata(np.arange(len(data[index])))
    plot_data[index].set_ydata(np.array(data[index]))
    ax[index].figure.canvas.draw()

def update_data():
    #print('update called')
    #global tempdata
    #global count
    [vt, va] = datagen.next()
    index = int(vt) - 1
    #print(index)
    if count[index] < buffersize:
        #print(count[index])
        tempdata[index][count[index]] = int(va) / 1023.0 * 3.3
        count[index] = count[index] + 1
    else:
        #print(tempdata)
        plot_update(index)
        tempdata[index] = [None] * buffersize
        count[index] = 0

#def userInput():
#    global freq
#    global tempdata
#    global data
#    global buffersize
#    while (1):
#        usercmd = raw_input("mbed>")
#        if usercmd == 'exit':
#            mbed.write('p');
#            mbed.flush()       
#            mbed.close()
#            os._exit(0)
#        elif usercmd.startswith('freq'):
#            newfreq = usercmd[5:]
#            if (newfreq.isdigit()):
#                nfreq = int(newfreq)
#                if nfreq >= 1 and nfreq <= 1000:
#                    freq = nfreq
#                    buffersize = freq / 5;
#                    tempdata = [None] * buffersize 
#                    print('Change frequency to be ' + str(freq) + 'Hz')
#                    mbed.write('c')
#                    mbed.flush()
#                    mbed.write(chr(freq))
#                    mbed.flush()
#                else:
#                    print('Sampling frequency must be in [1..1000]!')
#            else:
#                    print('Invalid frequency input!')
#        elif usercmd == 'stop':
#            mbed.write('p');
#            mbed.flush() 
#            print('Plot stopped')
#            #plot_update()
#            #data = np.append(data, tempdata)
#            count = 0
#            tempdata = [None] * buffersize         
#       
#        elif usercmd == 'start':
#            print('Start plotting with freq=' + str(freq) + 'Hz')
#            mbed.write('s');
#            mbed.flush()
#        elif usercmd != '':
#            print(usercmd + ': invalid command.')

signal.signal(signal.SIGINT, signal_handler)
fig = plt.figure(figsize=(20, 5))
ax[0] = fig.add_subplot(1, 3, 1)
ax[1] = fig.add_subplot(1, 3, 2)
ax[2] = fig.add_subplot(1, 3, 3)
for i in range(3):
    ax[i].grid(True)
    datagen = DataGen()
    ax[i].set_title('Sampling LPC11u24 AnalogIn ' + str(i + 1))
    ax[i].set_xlim([0, 50])
    ax[i].set_ylim([0, 3.3])
    plot_data[i] = ax[i].plot(data, linewidth=2, color=(0, 0, 1),)[0]
    ax[i].figure.canvas.draw()

timer = fig.canvas.new_timer(interval=1)
timer.add_callback(update_data)
timer.start()

#t = Thread(target=userInput, args=())
#t.start()

plt.show()