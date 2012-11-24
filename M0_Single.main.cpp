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
Ticker tic1, tic2, tic3, tic4, tic5, tic6;

int count = 0;
char str[4];

void putv(unsigned short x) {
    if (x == 0) {
        pc.putc('0');
        pc.putc('\r');
        pc.putc('\n');
        return;
    }
    count = 0;
    while (x != 0) {
        str[count++] = '0' + (x % 10);
        x /= 10;
    }
    for (int i = 0; i < count; i++) {
        pc.putc(str[count - 1 - i]);
    }
    pc.putc('\n');
    return;
}

void plot1() {
    led1 = !led1;
    unsigned short v = ain1.read_u16();
    putv(v);
}

void plot2() {
    led2 = !led2;
    unsigned short v = ain2.read_u16();
    putv(v);
}

void plot3() {
    led3 = !led3;
    unsigned short v = ain3.read_u16();
    putv(v);
}

void plot4() {
    led4 = !led4;
    unsigned short v = ain4.read_u16();
    putv(v);
}

void plot5() {
    led4 = !led4;
    unsigned short v = ain5.read_u16();
    putv(v);
}

void plot6() {
    led4 = !led4;
    unsigned short v = ain6.read_u16();
    putv(v);
}

void sample1() {
    led1 = !led1;
    double t = ain1;
}

void sample2() {
    led2 = !led2;
    double t = ain2;
}

void sample3() {
    led3 = !led3;
    double t = ain3;
}

void sample4() {
    led4 = !led4;
    double t = ain4;
}

void sample5() {
    led4 = !led4;
    double t = ain5;
}

void sample6() {
    led4 = !led4;
    double t = ain6;
}

int main() {
    led1 = 1;
    led2 = 1;
    pc.baud(115200);
    char c;
    int freq = 200;
    int curpin = 1;
    int numpin = 1;
    bool started[6] = {false, false, false, false, false, false};
    int plot = 1;
    
    while(1) {
        if ((c = pc.getc()) != NULL) {
            if (c == 's') {
                numpin = pc.getc();
                led1 = 1;
                if (!started[numpin - 1]){
                    if (numpin == 1) {
                        if (plot == 0) {
                            tic1.attach_us(&plot1, 1000000 / double(freq));
                        }
                        else {
                            tic1.attach_us(&sample1, 1000000 / double(freq));
                        }
                    }
                    else if (numpin == 2) { 
                        if (plot == 1) {
                            tic2.attach_us(&plot2, 1000000 / double(freq));
                        }
                        else {
                            tic2.attach_us(&sample2, 1000000 / double(freq));
                        }
                    }
                    else if (numpin == 3) { 
                        if (plot == 2) {
                            tic3.attach_us(&plot3, 1000000 / double(freq));
                        }
                        else {
                            tic3.attach_us(&sample3, 1000000 / double(freq));
                        }
                    }
                    else if (numpin == 4) { 
                        if (plot == 3) {
                            tic4.attach_us(&plot4, 1000000 / double(freq));
                        }
                        else {
                            tic4.attach_us(&sample4, 1000000 / double(freq));
                        }
                    }
                    else if (numpin == 5) { 
                        if (plot == 4) {
                            tic5.attach_us(&plot5, 1000000 / double(freq));
                        }
                        else {
                            tic5.attach_us(&sample5, 1000000 / double(freq));
                        }
                    }
                    else if (numpin == 6) { 
                        if (plot == 5) {
                            tic6.attach_us(&plot6, 1000000 / double(freq));
                        }
                        else {
                            tic6.attach_us(&sample6, 1000000 / double(freq));
                        }
                    }
                    else if (numpin == 7) { 
                        led2 = 1;
                        tic6.attach_us(&sample6, 1000000 / double(freq));
                        tic5.attach_us(&sample5, 1000000 / double(freq));
                        tic4.attach_us(&sample4, 1000000 / double(freq));
                        tic3.attach_us(&sample3, 1000000 / double(freq));
                        tic2.attach_us(&sample2, 1000000 / double(freq));
                        tic1.attach_us(&sample1, 1000000 / double(freq));
                        led3 = 1;
                        for (int j = 0; j < 6; j++) {
                            started[j] = true;
                        }
                    }
                    started[numpin - 1] = true;
                }
            }
            else if (c == 'p') {
                numpin = pc.getc();
                led1 = 0;
                if (started[numpin - 1]) {
                    if (numpin == 1) {
                        tic1.detach();
                    }
                    else if (numpin == 2) { 
                        tic2.detach();
                    }
                    else if (numpin == 3) { 
                        tic3.detach();
                    }
                    else if (numpin == 4) { 
                        tic4.detach();
                    }
                    else if (numpin == 5) { 
                        tic5.detach();
                    }
                    else if (numpin == 6) { 
                        tic6.detach();
                    }
                    else if (numpin == 7) { 
                        led2 = 0;
                        tic6.detach();
                        tic5.detach();
                        tic4.detach();
                        tic3.detach();
                        tic2.detach();
                        tic1.detach();
                        for (int j = 0; j < 6; j++) {
                            started[j] = false;
                        }
                        led3 = 0;
                    }
                    started[numpin - 1] = false;
                }
            }
            else if (c == 'c') {
                int q1 = pc.getc();
                int q2 = pc.getc();
                int q3 = pc.getc();
                int q4 = pc.getc();
                freq = q1 * 1000 + q2 * 100 + q3 * 10 + q4;
                if (started[0]) {
                    tic1.detach();
                    if (plot == 0) {
                        tic1.attach_us(&plot1, 1000000 / double(freq));
                    }
                    else {
                        tic1.attach_us(&sample1, 1000000 / double(freq));
                    }
                }
                if (started[1]) {
                    tic2.detach();
                    if (plot == 1) {
                        tic2.attach_us(&plot2, 1000000 / double(freq));
                    }
                    else {
                        tic2.attach_us(&sample2, 1000000 / double(freq));
                    }
                }
                if (started[2]) {
                    tic3.detach();
                    if (plot == 2) {
                        tic3.attach_us(&plot3, 1000000 / double(freq));
                    }
                    else {
                        tic3.attach_us(&sample3, 1000000 / double(freq));
                    }
                }
                if (started[3]) {
                    tic4.detach();
                    if (plot == 3) {
                        tic4.attach_us(&plot4, 1000000 / double(freq));
                    }
                    else {
                        tic4.attach_us(&sample4, 1000000 / double(freq));
                    }
                }
                if (started[4]) {
                    tic5.detach();
                    if (plot == 4) {
                        tic5.attach_us(&plot5, 1000000 / double(freq));
                    }
                    else {
                        tic5.attach_us(&sample5, 1000000 / double(freq));
                    }
                }
                if (started[5]) {
                    tic6.detach();
                    if (plot == 5) {
                        tic6.attach_us(&plot6, 1000000 / double(freq));
                    }
                    else {
                        tic6.attach_us(&sample6, 1000000 / double(freq));
                    }
                }
                
            }
            else if (c == 'x') {
                numpin = pc.getc();
                if (!started[numpin - 1]) {
                    started[numpin - 1] = true;
                }
                if (numpin == 1) {
                    led4 = 1;
                    plot = 0;
                    tic1.detach();
                    tic1.attach_us(&plot1, 1000000 / double(freq));
                }
                else if (numpin == 2) { 
                    plot = 1;
                    tic2.detach();
                    tic2.attach_us(&plot2, 1000000 / double(freq));
                }
                else if (numpin == 3) { 
                    plot = 2;
                    tic3.detach();
                    tic3.attach_us(&plot3, 1000000 / double(freq));
                }
                else if (numpin == 4) { 
                    plot = 3;
                    tic4.detach();
                    tic4.attach_us(&plot4, 1000000 / double(freq));
                }
                else if (numpin == 5) { 
                    plot = 4;
                    tic5.detach();
                    tic5.attach_us(&plot5, 1000000 / double(freq));
                }
                else if (numpin == 6) { 
                    plot = 5;
                    tic6.detach();
                    tic6.attach_us(&plot6, 1000000 / double(freq));
                }
            }
        }
    }
}