from unittest.mock import Mock
import sys

from PIL import Image, ImageDraw
import random
import logging
from io import BytesIO
import time
sys.modules['picamera'] = Mock()
sys.modules['Adafruit_DHT'] = Mock()
sys.modules['RPi'] = Mock()
sys.modules['RPi.GPIO'] = Mock()
from sticky_pi_device.config_handler import ConfigHandler
from sticky_pi_device.one_shooter import PiOneShooter



logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)




class DummyCamera(object):
    def __init__(self, test_image = None, test_light_sensor=None):
        self._resolution = None
        self._flash_mode = "off"
        self._test_light_sensor = test_light_sensor
        self._test_image = test_image
        self.exposure_speed = 0
        self.shutter_speed = 0
        self.iso = 0

        logging.info("Starting virtual camera")

    def make_jpeg_buffer(self, stream, resolution,
                iso=200,
                awb_gains=(1,1),
                shutter_speed=1):

        w, h = resolution
        if iso == 123:
            raise Exception("dummy exception when iso == 123")
        image = Image.new('RGB',
                          (w, h),
                          (0, 128, 255))
        pixels = image.load()  # create the pixel map

        for i in range(image.size[0]):  # for every col:
            for j in range(image.size[1]):  # For every row
                pixels[i, j] = (i, j, random.randint(0, 255))  # set the colour accordingly

        draw = ImageDraw.Draw(image)

        draw.text((w // 2, h // 2),
                  str(time.time() % 256)
                  )

        image.save(stream, format="JPEG")

    def get_resolution(self):
        return self._resolution

    def set_resolution(self, var):
            self._resolution = var

    resolution = property(get_resolution, set_resolution)

    def get_flash_mode(self):
        return self._flash_mode

    def set_flash_mode(self, var):
            self._flash_mode = var

    flash_mode = property(get_flash_mode, set_flash_mode)

    def close(self):
        logging.info("Closing virtual camera")


    def capture(self, path,
                iso=200,
                awb_gains=(1,1),
                shutter_speed=1):

        if self._test_image and self._flash_mode == "on":
            from shutil import copyfile
            copyfile(self._test_image, path)
            return path

        if self._test_light_sensor and self._flash_mode == "off":
            from shutil import copyfile
            copyfile(self._test_light_sensor, path)
            return path

        logging.info("Capturing with virtual camera:" + str({'resolution': self._resolution,
                                              'iso': iso,
                                              'awb_gains': awb_gains,
                                              'shutter_speed': shutter_speed,
                                              }))

        buffered = BytesIO()
        self.make_jpeg_buffer(buffered, self.resolution,
                                        iso=200,
                                        awb_gains=(1,1),
                                        shutter_speed=1)

        # img_str = base64.b64encode(buffered.getvalue())
        time.sleep(1)

        with open(path, 'wb') as f:
            f.write(buffered.getvalue())
        return path


class DummyOneShooter(PiOneShooter):
    def __init__(self, config, test_image=None, test_light_sensor=None):
        super().__init__(config)

        self._image_dir = '/tmp/images/'

        self._test_image = test_image
        self._test_light_sensor = test_light_sensor
        self._camera = None

    @staticmethod
    def _cpu_serial():
        return "01234567"

    def power_off(self):
        logging.info("Powering device off")

    def _camera_instance(self):
        logging.debug('Mock camera instance')
        return DummyCamera(self._test_image, self._test_light_sensor)

    @staticmethod
    def _read_dht_safe(pin):
        out = {'temp': 123,
               'hum': 456}

        time.sleep(.50)
        return out
    @staticmethod
    def _get_light_exifs(path):

        out = {'no_flash_exposure_time': 1,
               'no_flash_iso': 2,
               'no_flash_bv': 3,
               'no_flash_shutter_speed': 4}
        return out


import os
import json
c = ConfigHandler()
metadata_file = os.path.join(c.SPI_IMAGE_DIR, c.SPI_METADATA_FILENAME)
init_metadata = {"lat": 0,
                 "lng": 0,
                 "alt": 0}
with open(metadata_file, 'w') as f:
    json.dump(init_metadata, f)

a = DummyOneShooter(c)
a.shoot()
a.shoot()
a.shoot()
