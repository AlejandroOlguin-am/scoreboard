/*
 * Robotics Competition Scoreboard Controller
 * Microcontroller: PIC18F4550
 * Clock: 20 MHz Crystal
 * UART: 9600 baud
 * 
 * Displays:
 * - 2 digits for timer minutes
 * - 2 digits for timer seconds
 * - 2 digits for red alliance score
 * - 2 digits for blue alliance score (total: 8 displays in multiplexed configuration)
 * 
 * Hardware Connections:
 * - RC0-RC6: 7-segment display segments (a-g)
 * - RD0-RD5: Display digit select (active low)
 * - RB0-RB1: Alliance LED indicators
 * - RC6/TX, RC7/RX: UART communication
 */

#include <xc.h>
#include <stdint.h>
#include <stdbool.h>

// Configuration bits
#pragma config FOSC = HS        // High-Speed Crystal
#pragma config WDT = OFF        // Watchdog Timer disabled
#pragma config LVP = OFF        // Low Voltage Programming disabled
#pragma config PBADEN = OFF     // PORTB digital I/O

#define _XTAL_FREQ 20000000     // 20 MHz

// Command definitions (must match Python)
#define CMD_UPDATE_SCORE  0x01
#define CMD_UPDATE_TIMER  0x02
#define CMD_START_MATCH   0x03
#define CMD_STOP_MATCH    0x04
#define CMD_RESET_MATCH   0x05
#define CMD_PING          0x06
#define CMD_SET_LED       0x07

#define START_BYTE        0xAA
#define END_BYTE          0x55

// 7-segment patterns (common cathode)
const uint8_t seg_patterns[10] = {
    0x3F,  // 0
    0x06,  // 1
    0x5B,  // 2
    0x4F,  // 3
    0x66,  // 4
    0x6D,  // 5
    0x7D,  // 6
    0x07,  // 7
    0x7F,  // 8
    0x6F   // 9
};

// Global variables
volatile uint8_t timer_minutes = 2;
volatile uint8_t timer_seconds = 30;
volatile uint8_t red_score = 0;
volatile uint8_t blue_score = 0;
volatile uint8_t display_buffer[6];  // 6 displays total
volatile uint8_t current_digit = 0;
volatile bool match_active = false;
volatile bool red_led_state = false;
volatile bool blue_led_state = false;

// Function prototypes
void system_init(void);
void uart_init(void);
void timer0_init(void);
void update_display_buffer(void);
void process_uart_command(void);
uint8_t uart_read(void);
void uart_write(uint8_t data);
uint8_t calculate_checksum(uint8_t *data, uint8_t len);

// Interrupt Service Routine
void __interrupt() ISR(void) {
    // Timer0 interrupt for display multiplexing
    if (TMR0IF) {
        TMR0IF = 0;
        TMR0 = 256 - 156;  // ~1ms interrupt at 20MHz with 1:64 prescaler
        
        // Turn off all displays
        LATD = 0x3F;  // All high (assuming active low)
        
        // Output segment data for current digit
        LATC = display_buffer[current_digit];
        
        // Enable current digit
        LATD = ~(1 << current_digit);
        
        // Move to next digit
        current_digit++;
        if (current_digit >= 6) {
            current_digit = 0;
        }
    }
}

void main(void) {
    system_init();
    uart_init();
    timer0_init();
    
    // Enable global interrupts
    GIE = 1;
    PEIE = 1;
    
    // Initial display update
    update_display_buffer();
    
    while(1) {
        // Check for UART data
        if (PIR1bits.RCIF) {
            process_uart_command();
        }
        
        // Update LED indicators
        if (match_active) {
            LATBbits.LATB0 = red_led_state;   // Red LED
            LATBbits.LATB1 = blue_led_state;  // Blue LED
        } else {
            LATBbits.LATB0 = 0;
            LATBbits.LATB1 = 0;
        }
    }
}

void system_init(void) {
    // Configure ports
    TRISA = 0x00;  // All outputs (unused)
    TRISB = 0x00;  // All outputs (LEDs)
    TRISC = 0x80;  // RC7 input (RX), rest output (segments + TX)
    TRISD = 0x00;  // All outputs (digit select)
    
    // Clear outputs
    LATA = 0x00;
    LATB = 0x00;
    LATC = 0x00;
    LATD = 0x3F;  // All displays off (active low)
    
    // Disable analog on PORTB
    ADCON1 = 0x0F;
}

void uart_init(void) {
    // UART configuration for 9600 baud @ 20MHz
    // SPBRG = (Fosc / (64 * Baud)) - 1
    // SPBRG = (20000000 / (64 * 9600)) - 1 = 31.55 ≈ 32
    
    SPBRG = 32;
    TXSTA = 0x24;  // TXEN=1, BRGH=1
    RCSTA = 0x90;  // SPEN=1, CREN=1
    
    PIE1bits.RCIE = 1;  // Enable UART receive interrupt
}

void timer0_init(void) {
    // Timer0 configuration for 1ms interrupts
    // Prescaler 1:64
    T0CON = 0xC5;  // TMR0ON=1, 8-bit, prescaler 1:64
    TMR0 = 256 - 156;  // Preload for ~1ms
    TMR0IE = 1;  // Enable Timer0 interrupt
}

void update_display_buffer(void) {
    // Timer: MM:SS (displays 0-3)
    display_buffer[0] = seg_patterns[timer_minutes / 10];
    display_buffer[1] = seg_patterns[timer_minutes % 10];
    display_buffer[2] = seg_patterns[timer_seconds / 10];
    display_buffer[3] = seg_patterns[timer_seconds % 10];
    
    // Scores (displays 4-5)
    display_buffer[4] = seg_patterns[red_score / 10];
    display_buffer[5] = seg_patterns[red_score % 10];
    
    // Note: For 8 displays, add blue score
    // display_buffer[6] = seg_patterns[blue_score / 10];
    // display_buffer[7] = seg_patterns[blue_score % 10];
}

void process_uart_command(void) {
    uint8_t start, cmd, data_len, checksum, end;
    uint8_t data[10];
    uint8_t calculated_checksum;
    
    // Read start byte
    start = uart_read();
    if (start != START_BYTE) return;
    
    // Read command
    cmd = uart_read();
    
    // Read data length
    data_len = uart_read();
    if (data_len > 10) return;  // Sanity check
    
    // Read data
    for (uint8_t i = 0; i < data_len; i++) {
        data[i] = uart_read();
    }
    
    // Read checksum
    checksum = uart_read();
    
    // Read end byte
    end = uart_read();
    if (end != END_BYTE) return;
    
    // Verify checksum
    calculated_checksum = cmd ^ data_len;
    for (uint8_t i = 0; i < data_len; i++) {
        calculated_checksum ^= data[i];
    }
    
    if (checksum != calculated_checksum) return;  // Invalid packet
    
    // Process command
    switch(cmd) {
        case CMD_UPDATE_SCORE:
            if (data_len >= 2) {
                red_score = data[0];
                blue_score = data[1];
                update_display_buffer();
            }
            break;
            
        case CMD_UPDATE_TIMER:
            if (data_len >= 2) {
                timer_minutes = data[0];
                timer_seconds = data[1];
                update_display_buffer();
            }
            break;
            
        case CMD_START_MATCH:
            match_active = true;
            red_led_state = true;
            blue_led_state = true;
            break;
            
        case CMD_STOP_MATCH:
            match_active = false;
            red_led_state = false;
            blue_led_state = false;
            break;
            
        case CMD_RESET_MATCH:
            timer_minutes = 2;
            timer_seconds = 30;
            red_score = 0;
            blue_score = 0;
            match_active = false;
            update_display_buffer();
            break;
            
        case CMD_PING:
            // Respond to ping (optional)
            uart_write(0xAA);
            uart_write(0xCC);  // Acknowledgment
            uart_write(0x55);
            break;
            
        case CMD_SET_LED:
            if (data_len >= 2) {
                if (data[0] == 0x01) {  // Red alliance
                    red_led_state = data[1];
                } else if (data[0] == 0x02) {  // Blue alliance
                    blue_led_state = data[1];
                }
            }
            break;
    }
}

uint8_t uart_read(void) {
    while(!PIR1bits.RCIF);  // Wait for data
    return RCREG;
}

void uart_write(uint8_t data) {
    while(!PIR1bits.TXIF);  // Wait for transmit ready
    TXREG = data;
}

uint8_t calculate_checksum(uint8_t *data, uint8_t len) {
    uint8_t checksum = 0;
    for (uint8_t i = 0; i < len; i++) {
        checksum ^= data[i];
    }
    return checksum;
}