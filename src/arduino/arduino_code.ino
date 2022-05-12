#include <avr/interrupt.h>
#include <avr/io.h>

#define BIT1 758
#define BIT0 2276
#define TOP 3035
#define BIT_INIT 1517
#define CODE_LEN 56

char code[56] = "1111011101100001111011101000011001000011110101001111000";
uint8_t string_pos = 0, state = 0, wait_counter = 0;
uint8_t wait_flag=0, bit_init=0;

// Starts a PWM waveform with a period = 1.520ms
void T1_pwm_mode() {
    DDRB = 0b1<<PB5;
    TCCR1A = 0b11<<COM1A0 | 0b10<<WGM10;
    TCCR1B = 0b11<<WGM12 | 0b010<<CS10;
    OCR1A = TOP+2;
    ICR1 = TOP;
    TIMSK1 = 1<<ICIE1;
}

void send_pilot() {
    if(string_pos<=10) {
        OCR1A = BIT1;
        string_pos++;
    }
    if(string_pos == 11) {
        OCR1A = TOP+2;
        string_pos = 0;
        state++;
        wait_flag=1;
        bit_init=1;
        //Serial.print("\nended pilot: ");
        //Serial.print(OCR1A);
        //Serial.print('\n');
    }
}

void send_code() {
    if(bit_init) {
        OCR1A = BIT_INIT;
        bit_init=0;
    }
    else if(code[string_pos]=='0') {
        OCR1A = BIT0;
    }
    else if (code[string_pos]=='1') {
        OCR1A = BIT1;
    }

    string_pos++;
    if(string_pos == CODE_LEN) {
        string_pos=0;
        wait_flag = 1;
        bit_init=1;
        state++;

        OCR1A = TOP + 2;
        //Serial.print("Ended code\n");
        return;   
    }
}
// Handle OVFLW for Timer0
ISR(TIMER1_CAPT_vect) {
    
    if(!wait_flag) {
        if(state==0) {
            send_pilot();
        }
        else if(state>0 and state<6) {
            send_code();
        }

    }
    else {
        wait_counter++;
        //Serial.print('-');
        if(wait_counter>=14) {
            //Serial.print('\n');
            wait_flag =0;
            wait_counter=0;
        }
    }
}

void setup() {
    cli();
    Serial.begin(9600);
    
    sei(); // enable global interrupts
    T1_pwm_mode();
}


void loop() {
    
  
}
