## C code to be implemented from scratch

# PWM
PWM waveform with 1.520ms period
'0' sends out a signal with 25% duty_cycle
'1' sends a signal with 75% duty_cycle

# Preamble
Create a function preamble that initializes the process that send 10x '1' bits

# Switch between PWM modes and Timer Count modes
PWM mode is when sending a code
Timer count mode is to wait between repeating the code signal

# Timer Count Mode
Used for the Delta codes which is 15*1.520

# Implementation
1. Implement the PWM mode for a '1' and '0' signal
2. Implement the preamble function
3. Delta code Timer

