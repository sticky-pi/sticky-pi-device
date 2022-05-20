#!/bin/python

import time
import datetime
import os
import logging
from sticky_pi_device.utils import device_id
import RPi.GPIO as GPIO  # import RPi.GPIO module
import Adafruit_DHT
import subprocess
import picamera


# todo

# 1. test camera should show light intensity and keep light on
# 2. test camera in darkness!!

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
    out_sum = 0
    for i in range(8):
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
        out_sum += out
        GPIO.output(CS, True)  # /CS high

    logging.info("Battery level  : " + str(out_sum / 8.0))
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

    logging.info("------------- CAMERA TESTING AND CALIBRATION -------------")
    import tempfile

    tmp_image = tempfile.mktemp(suffix=".jpg")
    no_qr_code_at_least_once = False
    done = False

    with picamera.PiCamera() as camera:
        logging.info("Now manually setting up camera zoom/focus/aperture")
        logging.info("Add the QR code when done")
        time.sleep(2.0)
        camera.framerate = 10
        camera.resolution = (int(os.environ["SPI_IM_W"]), int(os.environ["SPI_IM_H"]))

        camera.zoom = (float(os.environ["SPI_ZOOM_X"]),
                       float(os.environ["SPI_ZOOM_Y"]),
                       float(os.environ["SPI_ZOOM_W"]),
                       float(os.environ["SPI_ZOOM_H"]))
        camera.flash_mode = 'off'
        try:
            SPI_FLASH_GPIO = int(os.environ["SPI_FLASH_GPIO"])
            SPI_REF_EXPOSURE_TIME = int(os.environ["SPI_REF_EXPOSURE_TIME"])
            GPIO.setup(SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output
            # SPI_TESTING_GPIO = int(os.environ["SPI_TESTING_GPIO"])
            # GPIO.setup(SPI_TESTING_GPIO, GPIO.IN)  # set a port/pin as an output
            GPIO.output(SPI_FLASH_GPIO, 1)
            while not done:
                camera.start_preview()
                time.sleep(4)
                camera.capture(tmp_image, quality = 95)
                camera.stop_preview()
                et = camera.exposure_speed / 1000
                logging.info(f"Set focus and adjust aperture until exposure time is ~{SPI_REF_EXPOSURE_TIME / 1000} ms")
                logging.info(f"Exposure time: {et} ms")

                try:

                    proc = subprocess.run(f"zbarimg  --set *.disable --set qrcode.enable  --set x-density=2 --set y-density=2  {tmp_image} -q",
                                          shell=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          universal_newlines=True)
                    decoded = proc.stdout
                    error = proc.stderr
                    proc.check_returncode()
                    if not no_qr_code_at_least_once:
                        logging.warning(
                            "QR code cannot be the first image. Put QR code only in the end of the focus process.")
                    else:
                        done = True
                except subprocess.CalledProcessError as e:
                    logging.info("No QR code in image. Continuing...")
                    logging.info(error)
                    no_qr_code_at_least_once = True

        finally:
            camera.stop_preview()
            GPIO.output(SPI_FLASH_GPIO, 0)

    logging.info("------------- TESTING DATA SYNCER -------------")
    assert os.path.isfile(tmp_image), "Did not capture any image! QR code needed to connect"
    logging.info(
        subprocess.check_output(f"sync_to_harvester.py --no-files --qr-code-file {tmp_image} ", shell=True).decode())
    os.remove(tmp_image)
    os.system("sync")

    logging.info("------------- Check time is updated -------------")
    time.sleep(2)
    os.system("hwclock --hctosys")
    logging.info("Time     : " + str(datetime.datetime.now()))
    # before 2020 seems like a dummy time!
    if time.time() < (datetime.datetime(2020, 1, 1, 0, 0) - datetime.datetime(1970, 1, 1)).total_seconds():
        logging.error("Time does not seem to have been updated!!")
        while True:
            time.sleep(.1)

    # ==============================================================

    logging.info("------------- TESTING TURNING OFF -------------")
    time.sleep(5)
    test_turn_off()
