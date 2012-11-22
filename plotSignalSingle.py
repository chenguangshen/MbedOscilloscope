import serial
import matplotlib.pyplot as plt
import numpy as np
from threading import *
import signal
import sys
import os
from Tkinter import *

freq = 1000
buffersize = 200
pinflag = [0] * 6
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
    global freq
    data = np.append(data, tempdata)
    xmax = len(data) if len(data) > freq else freq
    xmin = xmax - freq
    ymin = -3
    ymax = 3
    ax.set_xbound(lower=xmin, upper=xmax)
    ax.set_ybound(lower=ymin, upper=ymax)
    plot_data.set_xdata(np.arange(len(data)))
    plot_data.set_ydata(np.array(data))
    ax.figure.canvas.draw()

def update_data():
    #print('update called')
    global tempdata
    global count
    if count < buffersize:
        #print(count)
        tempdata[count] = int(datagen.next()) / 1023.0 * 3.3
        count = count + 1
    else:
        #print(tempdata)
        plot_update()
        tempdata = [None] * buffersize
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
        answer = answer + '     pin20: off;\n'
    else:
        answer = answer + '     pin20: on;\n'
    print(answer)

def userInput():
    global freq
    global tempdata
    global data
    global buffersize
    global pinflag
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
            else:
                print('Please specify correct pin to sample: p15-p20, or all')
            if numpin == 7:
                pinflag = [1] * 6
            else:
                pinflag[numpin - 1] = 1
            printAnswer()
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
                    plot_update()
                    count = 0;
                    buffersize = freq / 5;
                    tempdata = [None] * buffersize                   
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
                #print(numpin)
                mbed.write('p')
                mbed.flush()
                mbed.write(chr(numpin))
                mbed.flush()
                if numpin == 7:
                    pinflag = [0] * 6
                else:
                    pinflag[numpin - 1] = 0
                printAnswer()
            else:
                print('Please specify correct pin to stop: p15-p20, or all')
        elif usercmd.startswith('plot'):
            newpin = usercmd[5:]
            numpin = getPinNum(newpin)
            ax.set_title('Sampling LPC11u24 at ' + newpin)
            if numpin != None and numpin >= 1 and numpin <= 6:
                print('Start plotting the sample of ' + newpin + ' with freq='  + str(freq) + 'Hz')
                #print(numpin)
                count = 0
                tempdata = [None] * buffersize 
                data = [None]
                plot_data.set_xdata([])
                plot_data.set_ydata([])
                mbed.write('x');
                mbed.flush()
                mbed.write(chr(numpin));
                mbed.flush()
            else:
                print('Please specify correct pin to plot: p15-p20')
        elif usercmd != '':
            print(usercmd + ': invalid command.')
            
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.grid(True)
datagen = DataGen()
data = [None]
ax.set_title('Sampling LPC11u24')
ax.set_ylabel('Voltage')
ax.set_xlabel('Time')
ax.set_xlim([0, 50])
ax.set_ylim([0, 3.3])
tempdata = [None] * buffersize
count = 0
plot_data = ax.plot(data, linewidth=2, color=(0, 0, 1),)[0]
ax.figure.canvas.draw()

timer = fig.canvas.new_timer(interval=1)
timer.add_callback(update_data)
timer.start()

t = Thread(target=userInput, args=())
t.start()

plt.show()