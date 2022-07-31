#!/bin/python

import os 
import time
import RPi.GPIO as GPIO  # import RPi.GPIO module

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    SPI_FLASH_GPIO = int(os.environ["SPI_FLASH_GPIO"])
    GPIO.setup(SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output

    try:
        while True:
            GPIO.output(SPI_FLASH_GPIO, 1)
            time.sleep(0.1)
            GPIO.output(SPI_FLASH_GPIO, 0)
            time.sleep(3)
    finally:
        GPIO.output(SPI_FLASH_GPIO, 0)
