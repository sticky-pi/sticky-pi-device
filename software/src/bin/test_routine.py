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
import subprocess
import picamera


# todo

# 1. test camera should show light intensity and keep light on
# 2. test camera in darkness!!
# 3. button state holder issues:
#        * does not hold long?! leak?
#        * If button is push long, smokeeeeeeee! -> resistor between battery and delay/m drive?

# 3. sync optimisation?
# 4. pull down resistor to so we can test without a pi?
# 5. file list faster? | make file index? faster than glob?

def test_flash():
    logging.info("Blinking flash 10 times")
    SPI_FLASH_GPIO = int(os.environ["SPI_FLASH_GPIO"])
    GPIO.setup(SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output
    try:
        for i in range(10):
            GPIO.output(SPI_FLASH_GPIO, 1)
            time.sleep(0.05)
            GPIO.output(SPI_FLASH_GPIO, 0)
            time.sleep(.5)
    finally:
        logging.info("Turning flash off")
        GPIO.output(SPI_FLASH_GPIO, 0)


def test_turn_off():
    logging.info("Turning off")
    SPI_OFF_GPIO = int(os.environ["SPI_OFF_GPIO"])
    GPIO.setup(SPI_OFF_GPIO, GPIO.OUT)  # set a port/pin as an output
    GPIO.output(SPI_OFF_GPIO, 1)


def test_dht():
    logging.info("Reading DHT")
    sensor = os.environ["SPI_DHT"]
    pin = int(os.environ["SPI_DHT_GPIO"])
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

    logging.info("DHT reads      : " + str(out))


def test_batt():
    logging.info("Reading battery through MCP3001")
    CLK = 11
    CS = 8
    MISO = 9
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(CS, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)

    GPIO.output(CLK, False)  # CLK low
    GPIO.output(CS, True)  # /CS high
    GPIO.output(CS, False)  # /CS low

    lout = []
    for i in range(2):
        GPIO.output(CLK, True)
        GPIO.output(CLK, False)
        time.sleep(.01)
        v = GPIO.input(MISO)
        lout.append(v)

    out = 0
    for i in range(10):
        GPIO.output(CLK, True)
        GPIO.output(CLK, False)
        v = GPIO.input(MISO)
        lout.append(v)
        out <<= 1
        if v:
            out |= 0x1

    GPIO.output(CS, True)  # /CS high
    logging.info("Battery level  : " + str(out))
    time.sleep(.2)
    return 0


def test_push_button():
    SPI_MANUAL_ON_GPIO = int(os.environ["SPI_MANUAL_ON_GPIO"])
    GPIO.setup(SPI_MANUAL_ON_GPIO, GPIO.IN)  # set a port/pin as an output
    if GPIO.input(SPI_MANUAL_ON_GPIO):
        logging.info("Device was turned on with push button")
        return
    logging.info("Waiting for push button. Please press")
    while not GPIO.input(SPI_MANUAL_ON_GPIO):
        time.sleep(.2)


if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    logging.info("------------- TESTING INFO -------------")
    logging.info("Device ID: " + device_id())
    time.sleep(2)
    logging.info("Time     : " + str(datetime.datetime.now()))
    time.sleep(2)
    logging.info("Partitions     :\n" + subprocess.check_output("df -h", shell=True).decode())
    time.sleep(2)
    # ==============================================================

    logging.info("------------- TESTING PERIPHERALS -------------")
    test_flash()
    time.sleep(2)
    test_dht()
    time.sleep(2)
    test_batt()

    logging.info("------------- TESTING PUSH BUTTON-------------")
    time.sleep(2)
    test_push_button()

    # ==============================================================

    logging.info("------------- TESTING DATA SYNCER -------------")
    # try:
    ds = DataSyncer(user_requested=True, periodic=False, battery_level=-1, no_files=True)
    ds.sync()
    time.sleep(2)
    logging.info("Time     : " + str(datetime.datetime.now()))
    # except Exception as e:
    #     logging.error(e)

    # ==============================================================

    time.sleep(5)
    # ==============================================================

    # ==============================================================

    logging.info("------------- CAMERA TESTING AND CALIBRATION -------------")

    with picamera.PiCamera() as camera:
        logging.info("Now manually setting up camera zoom/focus/aperture")
        logging.info("Remove testing bridge when done")
        time.sleep(2.0)
        camera.framerate = 10
        camera.resolution = (int(os.environ["SPI_IM_W"]), int(os.environ["SPI_IM_H"]))

        camera.zoom = (int(os.environ["SPI_ZOOM_X"]),
                       int(os.environ["SPI_ZOOM_Y"]),
                       int(os.environ["SPI_ZOOM_W"]),
                       int(os.environ["SPI_ZOOM_H"]))
        camera.flash_mode = 'off'
        try:
            SPI_FLASH_GPIO = int(os.environ["SPI_FLASH_GPIO"])
            SPI_REF_EXPOSURE_TIME = int(os.environ["SPI_REF_EXPOSURE_TIME"])
            GPIO.setup(SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output
            SPI_TESTING_GPIO = int(os.environ["SPI_TESTING_GPIO"])
            GPIO.setup(SPI_TESTING_GPIO, GPIO.IN)  # set a port/pin as an output
            GPIO.output(SPI_FLASH_GPIO, 1)
            while GPIO.input(SPI_TESTING_GPIO, ):
                camera.start_preview()
                time.sleep(2)
                camera.stop_preview()
                et = camera.exposure_speed / 1000
                logging.info(f"Set focus and adjust aperture until exposure time is ~{SPI_REF_EXPOSURE_TIME / 1000} ms")
                logging.info(f"Exposure time: {et} ms")
                time.sleep(1)

        finally:
            camera.stop_preview()
            GPIO.output(SPI_FLASH_GPIO, 0)
    test_turn_off()
    # ==============================================================

    logging.info("------------- TESTING TURNING OFF -------------")
    time.sleep(2)
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
