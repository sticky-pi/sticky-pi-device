#!/bin/python

import time
import datetime
import os
import logging
from sticky_pi_device.data_syncer import DataSyncer
from sticky_pi_device.utils import device_id
import RPi.GPIO as GPIO  # import RPi.GPIO module
from gpiozero import MCP3001
import Adafruit_DHT

def test_flash():
    GPIO.setmode(GPIO.BCM)
    SPI_FLASH_GPIO = int(os.environ["SPI_FLASH_GPIO"])
    GPIO.setup(SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output
    try:
        for i in range(10):
            GPIO.output(SPI_FLASH_GPIO, 1)
            time.sleep(0.1)
            GPIO.output(SPI_FLASH_GPIO, 0)
            time.sleep(1)
    finally:
        GPIO.output(SPI_FLASH_GPIO, 0)

def test_dht():
    sensor=os.environ["SPI_DHT"]
    pin=int(os.environ["SPI_DHT_GPIO"])
    supported_sensors = {'dht11': Adafruit_DHT.DHT11, 'dht22': Adafruit_DHT.DHT22}
    assert sensor in supported_sensors, "Unsupported sensor name: %s" % sensor
    sensor = supported_sensors[sensor]
    humidity, temperature = None, None
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin, retries=20, delay_seconds=.25)
    except Exception as e:
        logging.error(e, exc_info=True)
    out = {'temp': temperature,
           'hum': humidity}

    logging.info("DHT reads      : " + out)


def test_batt():
    m = MCP3001()
    logging.info("Battery level  : " + m.value)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    SPI_FLASH_GPIO = int(os.environ["SPI_FLASH_GPIO"])
    GPIO.setup(SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    time.sleep(2)

    logging.info("------------- TESTING INFO -------------")
    logging.info("Device ID: " + device_id())
    time.sleep(2)
    logging.info("Time     : " + str(datetime.datetime.now()))
    time.sleep(2)
    logging.info("Partitions     : " )
    os.system("df -h")
    time.sleep(2)
    logging.info("------------- TESTING PERIPHERALS -------------")
    test_flash()
    time.sleep(2)
    test_dht()
    time.sleep(2)
    test_batt()
    time.sleep(2)

    logging.info("------------- TESTING DATA SYNCER -------------")

    ds = DataSyncer(user_requested=True, periodic=False, battery_level=-1, no_files=True)
    ds.sync()
    time.sleep(2)
    logging.info("Time     : " + str(datetime.datetime.now()))
    time.sleep(2)
    logging.info("------------- TESTING CAMERA -------------")
    logging.info("Now manually setting up camera zoom/focus/aperture/...")
    try:
        GPIO.output(SPI_FLASH_GPIO, 1)
        os.system("/opt/vc/bin/raspistill -t 0")
    finally:
        GPIO.output(SPI_FLASH_GPIO, 0)

# try internet connection for 30s
# no internet = skip + warning!

# echo "Date is $(date)"
# sleep 3
# echo "Device name is $(device_name)"
# sleep 3
# echo "File system:"
# df -h
# sleep 3
# test dht
# test battery level reader
# blink flash
# test camera
