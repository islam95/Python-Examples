from __future__ import print_function
import RPi.GPIO as GPIO
import wiringpi
import sys
import spidev
import math
from Pubnub import Pubnub
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)
GPIO.setup(25,GPIO.IN, pull_up_down=GPIO.PUD_UP)
board_type = sys.argv[-1]


import subprocess
unload_spi = subprocess.Popen('sudo rmmod spi_bcm2708', shell=True, stdout=subprocess.PIPE)
start_spi = subprocess.Popen('sudo modprobe spi_bcm2708', shell=True, stdout=subprocess.PIPE)
sleep(3)

pubnub = Pubnub(publish_key="pub-c-60323a7c-cd05-4174-ad76-c58dcd176b61", subscribe_key="sub-c-bfc5e744-ddf3-11e4-adc7-0619f8945a4f")

def _callback(message):
	print(message)
	
def _error(message):
	print(message)

def call(message, channel):
    print(message)
    if message['text'] == "on":
        GPIO.output(4, True)
        sleep(1)

    if message['text'] == "off":
        GPIO.output(4, False)
        sleep(1)
    
wiringpi.wiringPiSetupGpio()                # Initialise wiringpi GPIO
wiringpi.pinMode(18,2)                      # Set up GPIO 18 to PWM mode
wiringpi.pinMode(17,1)                      # GPIO 17 to output
wiringpi.digitalWrite(17, 0)                # port 17 off for rotation one way
wiringpi.pwmWrite(18,0)                     # set pwm to zero initially

def button_callback(channel):
    GPIO.output(4, True)
    sleep(1)

def get_adc(adcChannel):                                   # read SPI data from MCP3002 chip
    r = spi.xfer2([1,(2+adcChannel)<<6,0])  # these two lines are explained in more detail at the bottom
    ret = ((r[1]&31) << 6) + (r[2] >> 2)
    return ret

def cal_voltage(adc_value):
	voltage = ((3.3/1024)*adc_value)
	return voltage

def cal_temp(voltage):
	temp = (voltage-0.5)/0.01
	return temp

def display(adc_value, temp):        # function handles the display of ##### 
    print ('\r', 'ADC value: ',"{0:04d}".format(adc_value),', Temperature: ',"{0:.2f}".format(temp), '\r', sep='', end='') 
    sys.stdout.flush()

def reset_ports():                          # resets the ports for a safe exit
    wiringpi.pwmWrite(18,0)                 # set pwm to zero
    wiringpi.digitalWrite(18, 0)            # ports 17 & 18 off
    wiringpi.digitalWrite(17, 0)
    wiringpi.pinMode(17,0)                  # set ports back to input mode
    wiringpi.pinMode(18,0)

def stop():                              # Stops the motor
    wiringpi.pwmWrite(18,0)
    wiringpi.digitalWrite(17, 0)

def runMotor():                                  # Runs the motor
    wiringpi.pwmWrite(18,300)

def speed():                            # Speeds up the motor
     wiringpi.pwmWrite(18, 900)

adcChannel = 1
spi = spidev.SpiDev()
spi.open(0,0)

is_warning = False


try:
    GPIO.add_event_detect(25, GPIO.FALLING, callback=button_callback, bouncetime=300)
    pubnub.subscribe(channels = "text", callback=call, error=_error)
    while True:
        
        adc_value = (get_adc(adcChannel))
        v = cal_voltage(adc_value)
        t = cal_temp(v)

        
        if t > 50 and is_warning == False:
                message = 'The room temperature is ' + str(int(t)) + ' C'
                pubnub.publish("my_channel", message, callback=_callback, error=_error)
                runMotor()
                is_warning = True

        if t < 40 and is_warning == True:
                message = 'Now it is fine. T: ' + str(int(t)) + ' C'
                pubnub.publish("my_channel", message, callback=_callback, error=_error)
                print('Temperature: ', "{0:.2f}".format(t), ' C')
                stop()
                is_warning = False
        
        display(adc_value, t)
        sleep(0.05)
        
except KeyboardInterrupt:
    reset_ports()
    GPIO.cleanup()
    pubnub.unsubscribe(channel = "text")
        
GPIO.cleanup()

