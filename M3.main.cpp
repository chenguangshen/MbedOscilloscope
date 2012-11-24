/*
 * Demonstrates sending a buffer repeatedly to the DAC using DMA.
 * Connect an oscilloscope to Mbed pin 18. This example doesn't
 * output anything else (nothing on any serial ports).
 */
#include "mbed.h"
#include "MODDMA.h"

// Make the buffer size match the number of degrees
// in a circle since we are going to output a sinewave.
#define BUFFER_SIZE 360

// Set DAC output power mode.
#define DAC_POWER_MODE  (1 << 16)

DigitalOut led1(LED1);
DigitalOut led3(LED3);
DigitalOut led4(LED4);
LocalFileSystem local("local"); 

int buffer[2][BUFFER_SIZE];

AnalogOut signal(p18);

MODDMA dma;
MODDMA_Config *conf0, *conf1;

char type;
float freq, v1, v2;
int a1, a2;

void read_file(void) {
    FILE *fin = fopen("/local/waveform.txt", "r");
    type = fgetc(fin);
    fscanf(fin, "%f %f %f", &freq, &v1, &v2);
    fclose(fin);
}


void TC0_callback(void);
void ERR0_callback(void);

void TC1_callback(void);
void ERR1_callback(void);

int mainloop() {
    volatile int life_counter = 0;
    float gap = v2 - v1;
    float sum = v2 + v1;
    
    if (type == 'S') {
        // Create a sinewave buffer for testing.
        for (int i =   0; i <  360; i++) {
            buffer[0][i] =  (512 * (gap / 3.3) * sin(3.14159/180.0 * i)) + 512 * (sum / 3.3);
        }             
    }
    else if(type == 'Q') {
        // Create a square wave buffer
        for (int i =   0; i < 180; i++) {
            buffer[0][i] =  1024 * (v2 / 3.3);
        }
        for (int i =   180; i < 360; i++) {
            buffer[0][i] =  1024 * (v1 / 3.3);
        }
    }
    else if(type == 'R') {
        // Create a triangle wave buffer
        float high = 1024.0 * (v2 / 3.3);
        float low = 1024.0 * (v1 / 3.3);
        for (int i = 0; i < 180; i++) {
            buffer[0][i] = low + ((float)i / 180.0) * (high - low);
        }
        for (int i = 180; i < 360; i++) {
            buffer[0][i] = low + (360 - (float)i) / 180.0 * (high - low);
        }
    }

    // Adjust the sinewave buffer for use with DAC hardware.
    for (int i = 0; i < 360; i++) {
        buffer[0][i] = DAC_POWER_MODE | ((buffer[0][i] << 6) & 0xFFC0);
        buffer[1][i] = buffer[0][i]; // Just create a copy of buffer0 to continue sinewave.
    }
    // Prepare the GPDMA system for buffer0.
    conf0 = new MODDMA_Config;
    conf0
    ->channelNum    ( MODDMA::Channel_0 )
    ->srcMemAddr    ( (uint32_t) &buffer[0] )
    ->dstMemAddr    ( MODDMA::DAC )
    ->transferSize  ( 360 )
    ->transferType  ( MODDMA::m2p )
    ->dstConn       ( MODDMA::DAC )
    ->attach_tc     ( &TC0_callback )
    ->attach_err    ( &ERR0_callback );
 
    // Prepare the GPDMA system for buffer1.
    conf1 = new MODDMA_Config;
    conf1
    ->channelNum    ( MODDMA::Channel_1 )
    ->srcMemAddr    ( (uint32_t) &buffer[1] )
    ->dstMemAddr    ( MODDMA::DAC )
    ->transferSize  ( 360 )
    ->transferType  ( MODDMA::m2p )
    ->dstConn       ( MODDMA::DAC )
    ->attach_tc     ( &TC1_callback )
    ->attach_err    ( &ERR1_callback );
   
    // Calculating the transfer frequency:
    // By default, the Mbed library sets the PCLK_DAC clock value
    // to 24MHz. One complete sinewave cycle in each buffer is 360
    // points long. So, for a 1Hz wave we would need to transfer 360
    // values per second. That would be 24000000/360 which is approx
    // 66,666. But that's no good! The count val is only 16bits in size
    // so bare this in mind. If you need to go slower you will need to
    // alter PCLK_DAC from CCLK/4 to CCLK/8.
    // For our demo we are going to have the sinewave run at 1kHz.
    // That's 24000000/360000 which is approx 66. Experimentation
    // however showed 65 to get closer to 1kHz (on my Mbed and scope 
    // at least).
    LPC_DAC->DACCNTVAL = (1000.0 / freq) * 65 ;
    if (freq <= 10) {
        LPC_SC->PCLKSEL0 &= ~(3UL << 12);
    }
    // Prepare first configuration.
    if (!dma.Prepare( conf0 )) {
        error("Doh!");
    }
    
    // Begin (enable DMA and counter). Note, don't enable
    // DBLBUF_ENA as we are using DMA double buffering.
    LPC_DAC->DACCTRL |= (3UL << 2);
    
    while (1) { 
        if (life_counter++ > 1000000) {
            led1 = !led1; // Show some sort of life.
            life_counter = 0;
        }
    } 
}

// Configuration callback on TC
void TC0_callback(void) {
    
    // Just show sending buffer0 complete.
    led3 = !led3; 
        
    // Get configuration pointer.
    MODDMA_Config *config = dma.getConfig();
    
    // Finish the DMA cycle by shutting down the channel.
    dma.Disable( (MODDMA::CHANNELS)config->channelNum() );
   
    // Swap to buffer1
    dma.Prepare( conf1 );

    // Clear DMA IRQ flags.
    if (dma.irqType() == MODDMA::TcIrq) dma.clearTcIrq(); 
}

// Configuration callback on Error
void ERR0_callback(void) {
    error("Oh no! My Mbed EXPLODED! :( Only kidding, go find the problem");
}

// Configuration callback on TC
void TC1_callback(void) {
    
    // Just show sending buffer1 complete.
    led4 = !led4; 
        
    // Get configuration pointer.
    MODDMA_Config *config = dma.getConfig();
    
    // Finish the DMA cycle by shutting down the channel.
    dma.Disable( (MODDMA::CHANNELS)config->channelNum() );
    
    // Swap to buffer0
    dma.Prepare( conf0 );
    
    // Clear DMA IRQ flags.
    if (dma.irqType() == MODDMA::TcIrq) dma.clearTcIrq(); 
}

// Configuration callback on Error
void ERR1_callback(void) {
    error("Oh no! My Mbed EXPLODED! :( Only kidding, go find the problem");
}

int main() {
    read_file();
    mainloop();
}