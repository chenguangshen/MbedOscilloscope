import serial
import matplotlib.pyplot as plt
import numpy as np
from threading import *
import signal
import sys
import os
from Tkinter import *

freq = 200
xlength = 100
buffersize = 20
tempdata = [[None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize]
count = 0
data = [[0], [0], [0], [0], [0], [0]]
ax = [None] * 6
plot_data = [None] * 6

serdev = '/dev/tty.usbmodemfa132'
mbed = serial.Serial(port=serdev, baudrate=115200)

def signal_handler(signal, frame):
    print 'Exiting...'
    mbed.write('p');
    mbed.flush() 
    mbed.close()
    plt.clf()
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)

class DataGen(object):
    def __init__(self, init=0):
        self.data = self.init = init
    def next(self):
        return mbed.readline()

def plot_update():
    global data
    global tempdata
    for index in range(0, 6):
        if len(data[index]) <= xlength - count + 1:
            data[index] = np.append(data[index], tempdata[index])
        else:
            data[index] = np.append(data[index][49:], tempdata[index])
        xmax = xlength
        xmin = 0
        ymin = 0
        ymax = 3.5
        ax[index].set_xbound(lower=xmin, upper=xmax)
        ax[index].set_ybound(lower=ymin, upper=ymax)
        plot_data[index].set_xdata(np.arange(len(data[index])))
        plot_data[index].set_ydata(np.array(data[index]))
        ax[index].figure.canvas.draw()
            
def update_data():
    global tempdata
    global count
    v = datagen.next().split(' ')
    #print(v)
    if len(v) == 6:
        if count < buffersize:
            for index in range(0, 6):
                vcur = int(v[index]) / 65536.0 * 3.3
                tempdata[index][count] = vcur
            count = count + 1
        else:
            plot_update()
            tempdata = [[None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize]
            count = 0
            
def getPinNum(newpin):
    numpin = -1
    if (newpin == 'p15'):
        numpin = 1
    elif (newpin == 'p16'):
        numpin = 2
    elif (newpin == 'p17'):
        numpin = 3
    elif (newpin == 'p18'):
        numpin = 4
    elif (newpin == 'p19'):
        numpin = 5
    elif (newpin == 'p20'):
        numpin = 6
    elif (newpin == 'all'):
        numpin = 7
    return numpin

def printAnswer():
    answer = 'Sampling status:\n'
    if pinflag[0] == 0:
        answer = answer + '     pin15: off;\n'
    else:
        answer = answer + '     pin15: on;\n'
    if pinflag[1] == 0:
        answer = answer + '     pin16: off;\n'
    else:
        answer = answer + '     pin16: on;\n'
    if pinflag[2] == 0:
        answer = answer + '     pin17: off;\n'
    else:
        answer = answer + '     pin17: on;\n'
    if pinflag[3] == 0:
        answer = answer + '     pin18: off;\n'
    else:
        answer = answer + '     pin18: on;\n'
    if pinflag[4] == 0:
        answer = answer + '     pin19: off;\n'
    else:
        answer = answer + '     pin19: on;\n'
    if pinflag[5] == 0:
        answer = answer + '     pin20: off.'
    else:
        answer = answer + '     pin20: on.'
    print(answer)


def userInput():
    global freq
    global tempdata
    global data
    global buffersize
    global pinflag
    global xlength
    global mbed
    while (1):
        usercmd = raw_input("mbed>")
        if usercmd == 'exit':
            mbed.write('p');
            mbed.flush()       
            mbed.close()
            os._exit(0)
        elif usercmd.startswith('start'):
            newpin = usercmd[6:]
            #print(newpin)
            numpin = getPinNum(newpin)
            if numpin != None and numpin >= 1 and numpin <= 7:
                print('Sample at ' + newpin)
                #print(numpin)
                mbed.write('s')
                mbed.flush()
                mbed.write(chr(numpin))
                mbed.flush()
                if numpin == 7:
                    pinflag = [1] * 6
                else:
                    pinflag[numpin - 1] = 1
                printAnswer()
            else:
                print('Please specify correct pin to sample: p15-p20, or all')
        elif usercmd.startswith('freq'):
            newfreq = usercmd[5:]
            if (newfreq.isdigit()):
                nfreq = int(newfreq)
                if nfreq >= 1 and nfreq <= 1000:
                    freq = nfreq
                    mbed.write('c')
                    mbed.flush()
                    mbed.write(chr(freq / 1000))
                    mbed.flush()
                    mbed.write(chr(freq % 1000 / 100))
                    mbed.flush()
                    mbed.write(chr(freq % 100 / 10))
                    mbed.flush()
                    mbed.write(chr(freq % 10))
                    mbed.flush()
                    count = 0
                    xlength = freq / 2.0
                    tempdata = [[None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize]              
                    print('Change frequency to be ' + str(freq) + 'Hz')
                else:
                    print('Sampling frequency must be in [1..1000]!')
            else:
                    print('Invalid frequency input!')
        elif usercmd.startswith('stop'):
            newpin = usercmd[5:]
            numpin = getPinNum(newpin)
            if numpin != None and numpin >= 1 and numpin <= 7:
                print('Stop sampling at ' + newpin)
                mbed.write('p')
                mbed.flush()
                mbed.write(chr(numpin))
                mbed.flush()
                if numpin == 7:
                    pinflag = [0] * 6
                    tempdata = [[None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize, [None] * buffersize]
                else:
                    pinflag[numpin - 1] = 0
                    tempdata[numpin - 1] = [None] * buffersize
                printAnswer()
            else:
                print('Please specify correct pin to stop: p15-p20, or all')
        elif usercmd == ('status'):
            printAnswer()
        elif usercmd != '':
            print(usercmd + ': invalid command.')

fig = plt.figure(figsize=(20, 10))
ax[0] = fig.add_subplot(2, 3, 1)
ax[1] = fig.add_subplot(2, 3, 2)
ax[2] = fig.add_subplot(2, 3, 3)
ax[3] = fig.add_subplot(2, 3, 4)
ax[4] = fig.add_subplot(2, 3, 5)
ax[5] = fig.add_subplot(2, 3, 6)
for i in range(6):
    ax[i].grid(True)
    datagen = DataGen()
    ax[i].set_title('Sampling LPC11u24 AnalogIn ' + str(i + 1))
    ax[i].set_xlim([0, xlength])
    ax[i].set_ylim([0, 3.3])
    plot_data[i] = ax[i].plot(data, linewidth=2, color=(0, 0, 1),)[0]
    ax[i].figure.canvas.draw()

timer = fig.canvas.new_timer(interval=1)
timer.add_callback(update_data)
timer.start()

t = Thread(target=userInput, args=())
t.start()

plt.show()