# import PIL.Image
# import PIL.ExifTags
import piexif
import picamera
import Adafruit_DHT
import RPi.GPIO as GPIO  # import RPi.GPIO module
import json
import logging
from datetime import datetime
import pytz
import os
import time
import tempfile
import shutil
from sticky_pi_device.utils import device_id
from sticky_pi_device.config_handler import ConfigHandler
import signal

GPIO.setmode(GPIO.BCM)


class Metadata(dict):
    _expected_fields = {'lat': float, 'lng': float, 'alt': float}
    def  __init__(self, path):
        super().__init__()
        with open(path, 'r') as f:
            data = json.load(f)
        for k, t in self._expected_fields.items():
            assert k in data
            if data[k] is None:
                self[k] = None
            else:
                self[k] = t(data[k])


class PiOneShooter(object):
    _max_exposure = 50000  # us ## see https://github.com/pieelab/sticky_pi/issues/39
    _camera_timeout = 5

    def __init__(self, config: ConfigHandler, dev_id = None):
        self._config = config
        self._resolution = (self._config.SPI_IM_W, self._config.SPI_IM_H)
        self._resolution_light_sens = (self._config.SPI_LIGHT_SENSOR_W, self._config.SPI_LIGHT_SENSOR_H)
        self._zoom = (self._config.SPI_ZOOM_X,
                      self._config.SPI_ZOOM_Y,
                      self._config.SPI_ZOOM_W,
                      self._config.SPI_ZOOM_H)
        self._awb_gains = (self._config.SPI_AWB_RED,
                           self._config.SPI_AWB_BLUE)
        if dev_id is None:
            self._device_id = device_id()
        else:
            self._device_id = dev_id


    def shoot(self, preview=False):
        data = Metadata(os.path.join(self._config.SPI_IMAGE_DIR, self._config.SPI_METADATA_FILENAME))
        try:
            filename = self._make_file_path()
            data.update(self._picture(filename + ".tmp", preview))
            data.update(self._read_temp_hum())
            self._add_light_info_exif(filename+ ".tmp", data)
            os.rename(filename+ ".tmp", filename)
        except Exception as e:
            self._report_error(e)
            raise e

    def _report_error(self, e, n_flashes=5):
        GPIO.setup(self._config.SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output
        try:
            for i in range(n_flashes):
                GPIO.output(self._config.SPI_FLASH_GPIO, 1)
                time.sleep(0.1)
                GPIO.output(self._config.SPI_FLASH_GPIO, 0)
                time.sleep(1)
        finally:
            GPIO.output(self._config.SPI_FLASH_GPIO, 0)

    def _make_file_path(self):
        tz_UTC = pytz.timezone('UTC')
        datetime_now = datetime.now(tz_UTC)
        date_str = datetime_now.strftime("%Y-%m-%d_%H-%M-%S")

        basename = "%s.%s.jpg" % (self._device_id, date_str)
        path = os.path.join(self._config.SPI_IMAGE_DIR, self._device_id, basename)
        if os.path.exists(path):
            raise Exception('Target path already exists. NOT overwriting existing image')
        return path

    def _read_dht_safe(self, pin):
        supported_sensors = {'dht11': Adafruit_DHT.DHT11, 'dht22': Adafruit_DHT.DHT22}
        assert self._config.SPI_DHT in supported_sensors, "Unsupported sensor name: %s" % self._config.SPI_DHT
        sensor = supported_sensors[self._config.SPI_DHT]
        humidity, temperature = None, None
        try:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin, retries=10, delay_seconds=.25)
        except Exception as e:
            logging.error(e, exc_info=True)
        out = {'temp': temperature,
               'hum': humidity}
        return out

    def _read_temp_hum(self):
        def handler(signum, frame):
            raise Exception("DHT timed out")

        out = {'temp': None,
               'hum': None}
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(self._config.SPI_DHT_TIMEOUT)
        try:
            out = self._read_dht_safe(self._config.SPI_DHT_GPIO)
        except Exception as e:
            logging.error(e, exc_info=True)
        finally:
            signal.alarm(0)
            return out

    def _picture(self, path, preview=False):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        out = {}

        camera = self._camera_instance()
        try:
            logging.info('Capture')
            # warm up
            time.sleep(1.0)
            camera.framerate = 10
            camera.resolution = self._resolution
            camera.flash_mode = 'on'
            camera.zoom = self._zoom

            out = {'no_flash_exposure_time': camera.exposure_speed,
                   'no_flash_analog_gain': float(camera.analog_gain),
                   'no_flash_analog_gain': float(camera.digital_gain)}

            # fixme makes sense to set the iso ahead, and the query exposure?
            if camera.exposure_speed > self._max_exposure:
                camera.shutter_speed = self._max_exposure
                camera.iso = 100
            camera.awb_mode = 'off'
            camera.awb_gains = self._awb_gains
            temp_file = tempfile.mktemp(".jpg", "sticky_pi")
            try:
                def handler(signum, frame):
                    raise Exception("Camera timed out")

                signal.signal(signal.SIGALRM, handler)
                signal.alarm(self._camera_timeout) # if no picture after some time, we kill raise an exception!
                try:
                    camera.capture(temp_file, quality=self._config.SPI_IM_JPEG_QUALITY)
                finally:
                    signal.alarm(0)

            except Exception as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise e
            shutil.move(temp_file, path)
        finally:
            camera.close()
        return out


    def _camera_instance(self):
        return picamera.PiCamera()


    @staticmethod
    def _add_light_info_exif(path, dict):
        info = str(dict)
        flash_exif = piexif.load(path)
        flash_exif['0th'][271] = info
        exif_bytes = piexif.dump(flash_exif)
        piexif.insert(exif_bytes, path)

    def power_off(self):
        logging.info('Powering off though gpio')
        GPIO.setup(self._config.SPI_OFF_GPIO, GPIO.OUT)  # set a port/pin as an output
        logging.info('Syncing file system and powering off')
        os.sync()
        GPIO.output(self._config.SPI_OFF_GPIO, 1)
