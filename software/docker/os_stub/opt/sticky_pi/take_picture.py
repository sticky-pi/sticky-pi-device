import json
import optparse
import logging
from datetime import datetime
import pytz
import os
import time
import tempfile
import shutil
#test

IMAGE_DIR = '/sticky_pi_images/'

class DHTException(Exception):
    pass


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
        from PIL import Image, ImageDraw, ImageFont
        import random
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


        import base64
        from io import BytesIO
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
        logging.warning(path)

        return path


class PiOneShooter(object):
    _image_dir = IMAGE_DIR
    _metadata_file = 'metadata.json'
    _resolution = (2592, 1944)
    # _resolution = (3280, 2464)
    _resolution_light_sens = (640, 480)

    # == bcm13 pins
    _off_gpio = 16  # set high to send poweroff?
    _dth_gpio = 20
    _flash_gpio = 19
    _zoom = (0.1, 0.1, 0.8, 0.8)
    _awb_gains = (1, 2)

    _dht_timeout = 4
    _dht_sensor = 'dht22'
    _flash_overwrite = False # use GPIO to force flash (instead of builtin metering)
    _max_exposure = 10000 # us ## see https://github.com/pieelab/sticky_pi/issues/39
    _preview_resolution = (1600, 1200)

    def __init__(self):
        self._camera = None
    def shoot(self, preview=False, close_camera_after=True):
        try:
            with open(os.path.join(self._image_dir, self._metadata_file), 'r') as f:
                data = json.load(f)
                assert 'lat' in data
                assert 'lng' in data
                assert 'alt' in data

        except Exception as e:
            logging.error('Could NOT parse metadata file')
            logging.error(e)
            data = {}

        try:
            filename = self._make_file_path()
            logging.info(filename)
            data.update(self._picture(filename, preview, close_camera_after))
            data.update(self._read_temp_hum())
            logging.info('adding custom field to exif')
            if not preview:
                self._add_light_info_exif(filename, data)
        except Exception as e:
            logging.error(e)
            self._report_error(e)

        finally:
            logging.info(data)
            return data

    def _report_error(self, e, n_flashes=4):
        GPIO.setup(self._flash_gpio, GPIO.OUT)  # set a port/pin as an output
        try:
            for i in range(n_flashes):
                GPIO.output(self._flash_gpio, 1)
                time.sleep(0.1)
                GPIO.output(self._flash_gpio, 0)
                time.sleep(0.1)
        finally:
            GPIO.output(self._flash_gpio, 0)

    def _make_file_path(self):
        tz_UTC = pytz.timezone('UTC')
        datetime_now = datetime.now(tz_UTC)
        date_str = datetime_now.strftime("%Y-%m-%d_%H-%M-%S")
        dev_id = self.device_id()
        basename = "%s.%s.jpg" % (dev_id, date_str)
        path = os.path.join(self._image_dir, dev_id, basename)
        if os.path.exists(path):
            raise Exception('Target path already exists. NOT overwriting existing image')
        return path

    def _read_dht_safe(self, pin):
        import board
        import adafruit_dht
        if self._dht_sensor == 'dht11':
            dhtcls = adafruit_dht.DHT11
        elif self.sensor == 'dht22':
            dhtcls = adafruit_dht.DHT22
        else:
            raise Exception('Unsupported dht sensor')

        dht_dev = dhtcls(pin)
        out = {'temp': None,
               'hum': None}
        while True:
            try:
                # Print the values to the serial port
                if not out['temp']:
                    out['temp'] = dht_dev.temperature
                if not out['hum']:
                    out['hum'] = dht_dev.humidity
                if out['hum'] and out['temp']:
                    return out
            except DHTException:
                logging.error("Could not read DHT")
                break
            except RuntimeError as error:
                logging.warning(error.args[0])
            time.sleep(.25)

        return out

    def _read_dht_safe_old(self, pin):
        import Adafruit_DHT
        if self._dht_sensor == 'dht11':
            sensor = Adafruit_DHT.DHT11
        elif self._dht_sensor == 'dht22':
            sensor = Adafruit_DHT.DHT22
        else:
            raise Exception('Sensor type not supported')

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
        signal.alarm(self._dht_timeout)
        try:
            out = self._read_dht_safe_old(self._dth_gpio)
        except Exception as e:
            logging.error(e)
        finally:
            signal.alarm(0)
            return out

    @classmethod
    def device_id(cls):
        #https://raspberrypi.stackexchange.com/questions/2086/how-do-i-get-the-serial-number

        try:
            cpuserial = cls._cpu_serial()
            if not cpuserial:
                raise Exception("Could not read serial number")

        except Exception as e:
            cpuserial = "00000000"
            logging.error(e)
        return cpuserial


    def _picture(self, path, preview=False, close_camera_after=True):

        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        out = {}

        if self._camera is None:
            self._camera = self._camera_instance()

        logging.info('precapture')
        self._camera.resolution = self._resolution_light_sens
        self._camera.flash_mode = 'off'
        self._camera.framerate = 2

        temp_file = tempfile.mktemp(".jpg", "sticky_pi")

        time.sleep(1)
        try:
            self._camera.capture(temp_file)
            out = self._get_light_exifs(temp_file)
        except Exception as e:
            logging.error(e)
        finally:
            os.remove(temp_file)

        if preview:
            try:
                self._camera.resolution = self._preview_resolution
                self._camera.start_preview()
                logging.info('Showing preview, NO PICTURE saved.')
                time.sleep(5)
            finally:
                self._camera.stop_preview()
                return out

        logging.info('capture now')
        self._camera.framerate = 30
        self._camera.resolution = self._resolution
        self._camera.flash_mode = 'on'

        #fixme makes sense to set the iso ahead, and the query exposure?
        if self._camera.exposure_speed > self._max_exposure:
            self._camera.shutter_speed = self._max_exposure
            self._camera.iso = 100

        self._camera.awb_mode = 'off'
        self._camera.awb_gains = self._awb_gains
        self._camera.zoom = self._zoom

        time.sleep(.5)
        temp_file = tempfile.mktemp(".jpg", "sticky_pi")
        logging.info(temp_file)
        try:
            self._camera.capture(temp_file)
            if close_camera_after:
                self._close_camera()
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e
        shutil.move(temp_file, path)
        logging.info('All good, img saved in' + path)
        return out

    def _close_camera(self):
        if self._camera is not None:
            logging.debug('closing camera')
            self._camera.close()
        self._camera = None

    def __del__(self):
        self._close_camera()

    def _camera_instance(self):
        import picamera
        return picamera.PiCamera()

    @staticmethod
    def _cpu_serial():
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
                    cpuserial_last_8bit = cpuserial[8:16]
                    return cpuserial_last_8bit

    @staticmethod
    def _get_light_exifs(path):
        import PIL.Image
        import PIL.ExifTags
        img = PIL.Image.open(path)

        d = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }

        out = {'no_flash_exposure_time': d['ExposureTime'],
                'no_flash_iso':d['ISOSpeedRatings'],
                'no_flash_bv':d['BrightnessValue'],
                'no_flash_shutter_speed': d['ShutterSpeedValue']}
        return out
    @staticmethod
    def _add_light_info_exif(path, dict):
        import piexif
        info = str(dict)
        flash_exif = piexif.load(path)
        flash_exif['0th'][271] = info
        exif_bytes = piexif.dump(flash_exif)
        piexif.insert(exif_bytes, path)


    def power_off(self):
        logging.info('powering off though gpio')

        GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
        GPIO.setup(self._off_gpio, GPIO.OUT)  # set a port/pin as an output
        logging.info('Syncing')
        os.sync()
        logging.info('Unplugging the juice!')
        GPIO.output(self._off_gpio, 1)


class DummyOneShooter(PiOneShooter):
    _image_dir = '/tmp/images/'
    def __init__(self, test_image=None, test_light_sensor=None):
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
    def _read_dht_safe_old(pin):
        out = {'temp': 123,
               'hum': 456}

        time.sleep(.50)
        return out

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-D", "--debug", dest="debug", default=False, help="Set DEBUG mode ON", action="store_true")
    parser.add_option("-d", "--dev", dest="dev", default=False, help="Set DEV mode ON", action="store_true")
    parser.add_option("-s", "--stdout-log", dest="std_log", default=False, help="Log to standard output instead of file, the default", action="store_true")
    #parser.add_option("-e", "--results-dir", dest="results_dir", help="Where result files are stored")
    parser.add_option("-I", "--test_image", default=None, dest="test_image", help="Path to a test image, only with --dev")
    parser.add_option("-i", "--interactive", default=False, dest="interactive", action="store_true", help="Button / keyboard to take picture")
    parser.add_option("-n", "--no-sync-to-thumbdrive", default=False, dest="no_sync_to_drive", action="store_true",
                      help="Call another process to sync all imaged onto thumbdrive, if detected")


    (options, args) = parser.parse_args()
    option_dict = vars(options)
    option_dict["sync_to_drive"] = not option_dict["no_sync_to_drive"]

    logfile = None
    if option_dict['dev']:
        ShooterCls = DummyOneShooter
    else:
        ShooterCls = PiOneShooter
        img_subdir = os.path.join(IMAGE_DIR, ShooterCls.device_id())
        if not os.path.exists(img_subdir):
            os.makedirs(img_subdir)
        if not option_dict['std_log']:
            logfile = os.path.join(img_subdir, 'sticky_pi.log')

    if option_dict["debug"]:
        logging.basicConfig(level=logging.DEBUG,
                            filename=logfile)
        logging.info("Logging using DEBUG SETTINGS")
        logging.info("Logging in %s" % logfile)

    else:
        logging.basicConfig(filename=logfile)

    logging.warning('Logging at %s' % datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if option_dict["sync_to_drive"]:
        from subprocess import Popen
        logging.info('Spawning sync daemon')
        command = ['python', os.path.join(dir_path, 'sync_to_pendrive.py')]
        if option_dict["debug"]:
            command.append('-D')
        p = Popen(command)

    if option_dict['dev']:
        one_shooter = DummyOneShooter(test_image=option_dict['test_image'])
    else:
        import RPi.GPIO as GPIO  # import RPi.GPIO module
        GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
        one_shooter = PiOneShooter()
    try:
        if option_dict['interactive']:
            import keyboard
            logging.debug('Interactive mode')
            # a push button connected between ground and pin 6 (using internal pull up resistor)
            # for lab picture taking
            PREVIEW_KEY = 'p'
            CAPTURE_KEY = 'c'
            BUTTON_PIN = 6
            GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            while True:
                button_state = GPIO.input(BUTTON_PIN)

                if keyboard.is_pressed(PREVIEW_KEY):
                    logging.info('Preview key pressed')
                    one_shooter.shoot(preview=True)

                elif button_state == False or keyboard.is_pressed(CAPTURE_KEY):
                    one_shooter.shoot()
                    if option_dict["sync_to_drive"]:
                        logging.info('Syncing all images to pendrive')
                        command = ['python', os.path.join(dir_path, 'sync_to_pendrive.py'), '-n']
                        if option_dict["debug"]:
                            command.append('-D')
                        p2 = Popen(command)
                        p2.wait()
                time.sleep(.25)
        else:
            one_shooter.shoot(close_camera_after=True)



    finally:
        if option_dict["sync_to_drive"]:
            logging.info('waiting for backup')
            p.wait(timeout=600)
            # FIXME display some output with flash??
            # show if fails, show if succeed
        one_shooter.power_off()
