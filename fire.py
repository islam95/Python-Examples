from __future__ import print_function
import sys
import spidev
import math
from twython import Twython
from time import sleep
board_type = sys.argv[-1]

import subprocess
unload_spi = subprocess.Popen('sudo rmmod spi_bcm2708', shell=True, stdout=subprocess.PIPE)
start_spi = subprocess.Popen('sudo modprobe spi_bcm2708', shell=True, stdout=subprocess.PIPE)
sleep(3)

apiKey = '7bvcREL3L0JNYDbpt2kFwUDTl'
apiSecret = 'IdxAkd8ZVqKBYqz9I9gktko9PDsRrQ0S1ZYtcei8IeQSc96LBG'
accessToken = '52664622-LRMw0WEh8j3EIniixBwXLPdBddXAUWMw6GgPhAEMm'
accessTokenSecret = '4qIjTB6gsWzkRMldwIFtdc6vK66R8AeK0OwNxh6ETStVK'

def get_adc(channel):                                   # read SPI data from MCP3002 chip
    if ((channel > 1) or (channel < 0)):                # Only 2 channels 0 and 1 else return -1
        return -1
    r = spi.xfer2([1,(2+channel)<<6,0])  # these two lines are explained in more detail at the bottom
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
	
	
channel = 1

spi = spidev.SpiDev()
spi.open(0,0)

is_warning = False

while True:
	adc_value = (get_adc(channel))
	v = cal_voltage(adc_value)
	t = cal_temp(v)
	
	if t > 50 and is_warning == False:
		api = Twython(apiKey, apiSecret, accessToken, accessTokenSecret)
                tweet_text = 'Fire Alarm, it is above 50 now!!!'
                api.update_status(status = tweet_text)
                print('Tweeted: ', tweet_text)
                print('Temperature: ', "{0:.2f}".format(t), ' C')
                is_warning = True

	if t < 40 and is_warning == True:
                api = Twython(apiKey, apiSecret, accessToken, accessTokenSecret)
                tweet_text = 'No worries, now it is fine!'
                api.update_status(status = tweet_text)
                print('Tweeted: ', tweet_text)
		is_warning = False
		
	display(adc_value, t)
	sleep(0.05)
