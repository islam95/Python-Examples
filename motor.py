
# all print statements in this prog must now be in python 3 format
from __future__ import print_function               
import wiringpi
import sys
from time import sleep
board_type = sys.argv[-1]

wiringpi.wiringPiSetupGpio()                # Initialise wiringpi GPIO
wiringpi.pinMode(18,2)                      # Set up GPIO 18 to PWM mode
wiringpi.pinMode(17,1)                      # GPIO 17 to output
wiringpi.digitalWrite(17, 0)                # port 17 off for rotation one way
wiringpi.pwmWrite(18,0)                     # set pwm to zero initially

def reset_ports():                          # resets the ports for a safe exit
    wiringpi.pwmWrite(18,0)                 # set pwm to zero
    wiringpi.digitalWrite(18, 0)            # ports 17 & 18 off
    wiringpi.digitalWrite(17, 0)
    wiringpi.pinMode(17,0)                  # set ports back to input mode
    wiringpi.pinMode(18,0)

def stop():                              # Stops the motor
    wiringpi.pwmWrite(18,0)
    wiringpi.digitalWrite(17, 0)

def run():                                  # Runs the motor
    wiringpi.pwmWrite(18,300)

def change():                               # Changes the direction of the motor
    if wiringpi.digitalRead(17) == 0:
        wiringpi.digitalWrite(17, 1)
        wiringpi.pwmWrite(18,100) 
    else:
        wiringpi.digitalWrite(17, 0)
        wiringpi.pwmWrite(18,900) 


def speed(value):                            # Speeds up the motor
     wiringpi.pwmWrite(18, value)

try:
    while True:
        command = raw_input("Enter your command: ")
        
        if command == 'r':          # Runs the motor
            run()

        if command == 's':              # Stops the motor
            stop()

        if command == 'd':              # Changes the direction of the motor
            change()

        if command == 'sp':             # Speeds up the motor
            cSpeed = raw_input("Enter speed from 0 to 1023: ")
            speed(int(cSpeed))

        if command == 'p':
            reset_ports()
            
except KeyboardInterrupt:      # trap a CTRL+C keyboard interrupt
    reset_ports()                   # reset ports on interrupt 



