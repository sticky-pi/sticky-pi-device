import PIL.Image
import PIL.ExifTags
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
    _max_exposure = 10000  # us ## see https://github.com/pieelab/sticky_pi/issues/39
    _preview_resolution = (1600, 1200)
    def __init__(self, config: ConfigHandler):
        self._config = config
        self._resolution = (self._config.SPI_IM_W, self._config.SPI_IM_H)
        self._resolution_light_sens = (self._config.SPI_LIGHT_SENSOR_W, self._config.SPI_LIGHT_SENSOR_H)
        self._zoom = (self._config.SPI_ZOOM_X,
                      self._config.SPI_ZOOM_Y,
                      self._config.SPI_ZOOM_W,
                      self._config.SPI_ZOOM_H)
        self._awb_gains = (self._config.SPI_AWB_RED,
                           self._config.SPI_AWB_BLUE)

    # def __del__(self):
    #     self._close_camera()

    def shoot(self, preview=False, close_camera_after=True):
        data = Metadata(os.path.join(self._config.SPI_IMAGE_DIR, self._config.SPI_METADATA_FILENAME))
        logging.warning("metadata parsed")
        try:
            filename = self._make_file_path()
            logging.warning("Filename made")
            data.update(self._picture(filename + ".tmp", preview, close_camera_after))
            logging.warning("picture taken")
            data.update(self._read_temp_hum())
            logging.warning("temp read")
            self._add_light_info_exif(filename+ ".tmp", data)
            logging.warning("exif modifis")
            os.rename(filename+ ".tmp", filename)
        except Exception as e:
            self._report_error(e)
            raise e

    def _report_error(self, e, n_flashes=4):
        GPIO.setup(self._config.SPI_FLASH_GPIO, GPIO.OUT)  # set a port/pin as an output
        try:
            for i in range(n_flashes):
                GPIO.output(self._config.SPI_FLASH_GPIO, 1)
                time.sleep(0.1)
                GPIO.output(self._config.SPI_FLASH_GPIO, 0)
                time.sleep(0.1)
        finally:
            GPIO.output(self._config.SPI_FLASH_GPIO, 0)

    def _make_file_path(self):
        tz_UTC = pytz.timezone('UTC')
        datetime_now = datetime.now(tz_UTC)
        date_str = datetime_now.strftime("%Y-%m-%d_%H-%M-%S")
        dev_id = device_id()
        basename = "%s.%s.jpg" % (dev_id, date_str)
        path = os.path.join(self._config.SPI_IMAGE_DIR, dev_id, basename)
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
            logging.error(e)
        out = {'temp': temperature,
               'hum': humidity}
        return out

    def _read_temp_hum(self):
        import signal

        def handler(signum, frame):
            raise Exception("DHT timed out")

        out = {'temp': None,
               'hum': None}
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(self._config.SPI_DHT_TIMEOUT)
        try:
            out = self._read_dht_safe(self._config.SPI_DHT_GPIO)
        except Exception as e:
            logging.error(e)
        finally:
            signal.alarm(0)
            return out

    def _picture(self, path, preview=False, close_camera_after=True):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        out = {}

        self._camera = self._camera_instance()
        try:
            logging.warning('precapture')
            self._camera.resolution = self._resolution_light_sens
            self._camera.flash_mode = 'off'
            self._camera.framerate = 2
            temp_file = tempfile.mktemp(".jpg", "sticky_pi")
            time.sleep(1)
            self._camera.capture(temp_file)
            try:
                out = self._get_light_exifs(temp_file)
            except Exception as e:
                logging.error(e)
            finally:
                os.remove(temp_file)

            logging.warning('capture now')
            self._camera.framerate = 30
            self._camera.resolution = self._resolution
            self._camera.flash_mode = 'on'

            # fixme makes sense to set the iso ahead, and the query exposure?
            if self._camera.exposure_speed > self._max_exposure:
                self._camera.shutter_speed = self._max_exposure
                self._camera.iso = 100

            self._camera.awb_mode = 'off'
            self._camera.awb_gains = self._awb_gains
            self._camera.zoom = self._zoom

            time.sleep(.5)
            temp_file = tempfile.mktemp(".jpg", "sticky_pi")
            try:
                self._camera.capture(temp_file, quality=self._config.SPI_IM_JPEG_QUALITY)
                logging.warning("capture Done")
            except Exception as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise e
            shutil.move(temp_file, path)
        finally:
            self._camera.close()
            logging.warning("Camera closed")
        return out


    def _camera_instance(self):
        return picamera.PiCamera()

    @staticmethod
    def _get_light_exifs(path):
        img = PIL.Image.open(path)

        d = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }

        out = {'no_flash_exposure_time': d['ExposureTime'],
               'no_flash_iso': d['ISOSpeedRatings'],
               'no_flash_bv': d['BrightnessValue'],
               'no_flash_shutter_speed': d['ShutterSpeedValue']}
        return out

    @staticmethod
    def _add_light_info_exif(path, dict):
        info = str(dict)
        flash_exif = piexif.load(path)
        flash_exif['0th'][271] = info
        exif_bytes = piexif.dump(flash_exif)
        piexif.insert(exif_bytes, path)

    def power_off(self):
        logging.info('powering off though gpio')
        GPIO.setup(self._config.SPI_OFF_GPIO, GPIO.OUT)  # set a port/pin as an output
        logging.info('Syncing')
        os.sync()
        logging.info('Unplugging the juice!')
        GPIO.output(self._config.SPI_OFF_GPIO, 1)
