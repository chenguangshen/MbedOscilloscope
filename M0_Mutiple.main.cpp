#include "mbed.h"

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);

AnalogIn ain1(p15);
AnalogIn ain2(p16);
AnalogIn ain3(p17);
AnalogIn ain4(p18);
AnalogIn ain5(p19);
AnalogIn ain6(p20);

Serial pc(USBTX, USBRX);
Ticker tic;

bool started[] = {false, false, false, false, false, false};

unsigned short t1, t2, t3, t4, t5, t6;

void sample() {
    //double t = ain1;
    //unsigned int v = (unsigned int)(t * 1023);
    //putv(v);
    if (started[0])
        t1 = ain1.read_u16();
    else
        t1 = 0;
    if (started[1])
        t2 = ain2.read_u16();
    else
        t2 = 0;
    if (started[2])
        t3 = ain3.read_u16();
    else
        t3 = 0;
    if (started[3])
        t4 = ain4.read_u16();
    else
        t4 = 0;
    if (started[4])
        t5 = ain5.read_u16();
    else
        t5 = 0;
    if (started[5])
        t6 = ain6.read_u16();
    else
        t6 = 0;
    printf("%d %d %d %d %d %d\n", t1, t2, t3, t4, t5, t6);
}

void Rx_interrupt() {
    char c;
    int freq = 200;
    int numpin = 1;
    led1 = 1;
    if (pc.readable()) {
        c = pc.getc();
        if (c == 'p') {
            led4 = 1;
            numpin = pc.getc();
            if (numpin == 7) {
                led3 = 1;
                for (int j = 0; j < 6; j++) {
                    started[j] = false;
                }
            }
            else{
                started[numpin - 1] = false;
                //tic.attach_us(&sample, 1000000 / double(freq));
            }                
        }
        if (c == 's') {
            numpin = pc.getc();
            if (numpin == 7) {
                for (int j = 0; j < 6; j++) {
                    started[j] = true;
                }
                tic.attach_us(&sample, 1000000 / double(freq));
            }
            else{
                started[numpin - 1] = true;
                led4 = !led4;
            }
        }
        if (c == 'c') {
            tic.detach();
            int q1 = pc.getc();
            int q2 = pc.getc();
            int q3 = pc.getc();
            int q4 = pc.getc();
            numpin = 7;
            freq = q1 * 1000 + q2 * 100 + q3 * 10 + q4;
            tic.attach_us(&sample, 1000000 / double(freq));
        }
    }
    led1 = 0;
    return;
}

int main() {
    pc.baud(115200);
    pc.attach(&Rx_interrupt, RxIrq);
    while (1) {
    
    }
}