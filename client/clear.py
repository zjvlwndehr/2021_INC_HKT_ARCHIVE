try:
    import I2C
except:
    pass

lcd = I2C.lcd()
lcd.lcd_clear()

import RPi.GPIO as GPIO
import time

led_channel = 17
lcd_channel = 27

GPIO.setmode(GPIO.BCM)

GPIO.setup(led_channel, GPIO.OUT)
GPIO.setup(lcd_channel, GPIO.OUT)


GPIO.output(led_channel, GPIO.LOW)
GPIO.output(lcd_channel, GPIO.LOW)

