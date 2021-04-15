
import datetime
from subprocess import Popen, PIPE, STDOUT
import time
import logging
import os
import requests
import glob
import json
from sticky_pi_device.utils import device_id
from sticky_pi_device.config_handler import ConfigHandler

def img_file_hash(path):
    stats = os.stat(path)
    # fixme. make a fast hash, e.g. using first and last bytes
    return f"hash-{stats.st_size}"


class DataSyncer(object):

    def __init__(self, config: ConfigHandler):
        self._config = config

    def sync(self):
        if not self._ping_harvester():
            logging.info("Cannot reach host. Trying wifi")
            self._start_network_interface()
            assert self._ping_harvester(), f"Cannot reach host {self._config.SPI_HARVESTER_HOSTNAME}"
        else:
            logging.info("Host is reached without wifi")

        self._get_harvester_status()
        self._upload_images()

    def _ping_harvester(self):
        import os
        host = self._config.SPI_HARVESTER_HOSTNAME
        response = os.system("ping -c 1 " + host)
        return response == 0

    def _get_device_status(self):
        status = {"version": self._config.SPI_VERSION,
                  "progress_skipping": 0, "progress_to_skip": 0, "progress_uploading": 0, "progress_to_upload": 0,
                  'in_transaction': 1}
        return status

    def _upload_images(self):
        dev_id = device_id()
        host = self._config.SPI_HARVESTER_HOSTNAME
        url_images_to_upload = f"http://{host}/images_to_upload/{dev_id}"
        url_upload = f"http://{host}/upload_device_images/{dev_id}"
        url_update_status = f"http://{host}/update_device_status/{dev_id}"

        pattern = os.path.join(self._config.SPI_IMAGE_DIR, dev_id, "*.jpg")

        files = {}
        for f in sorted(glob.glob(pattern)):
            files[os.path.basename(f)] = img_file_hash(f)

        response = requests.post(url_images_to_upload, json=files)
        assert response.status_code == 200, response
        image_status = json.loads(response.content)

        device_status = self._get_device_status()

        for image, status in image_status.items():
            if status == "uploaded":
                device_status["progress_to_skip"] += 1
            else:
                device_status["progress_to_upload"] += 1

        for image in sorted(image_status.keys()):
            image_path = os.path.join(self._config.SPI_IMAGE_DIR, dev_id, image)
            logging.info((image_path, image_status[image]))
            if image_status[image] != "uploaded":

                assert os.path.exists(image_path), f"Cannot find {image_path}"
                device_status["progress_uploading"] += 1
                # post = {'status': device_status, 'hash': img_file_hash(image_path)}
                # can also do multiple files in one payload...

                with open(image_path, 'rb') as f:
                    payload = {'image': (image, f, 'application/octet-stream'),
                               'status': ('status', json.dumps(device_status), 'application/json'),
                               'hash': ('hash', json.dumps(img_file_hash(image_path)), 'application/json')
                               }

                    response = requests.post(url_upload, files=payload)
                    if response.status_code != 200:
                        logging.error(response)
                    # fixme here, retry if server cannot be reached
            else:
                device_status["progress_skipping"] += 1

        # Formally finish transaction
        device_status['in_transaction'] = 0
        response = requests.post(url_update_status, json=device_status)
        assert response.status_code == 200, response

    def _get_harvester_status(self):
        url_harvester_status = f"http://{self._config.SPI_HARVESTER_HOSTNAME}/status"
        response = requests.get(url_harvester_status)
        if response.status_code != 200:
            raise Exception(f"Unexpected response from server: {response.status_code}")
        harvester_status = json.loads(response.content)
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(harvester_status["time"]))
        command = ["timedatectl", "set-time", time_str]
        p = Popen(command)
        exit_code = p.wait(5)
        if exit_code != 0:
            #fixme should be an error!
            # raise Exception(f"Cannot set localtime to {time_str}")
            logging.error(f"Cannot set localtime to {time_str}")

        meta = harvester_status["gps_coordinates"]
        meta["datetime"] = time_str
        path = os.path.join(self._config.SPI_IMAGE_DIR, self._config.SPI_METADATA_FILENAME)
        logging.error("meta")
        logging.error(meta)
        with open(path, 'w') as f:
            f.write(json.dumps(meta))

    def _start_network_interface(self):
        from subprocess import Popen
        logging.info('Starting network interface')
        command = ["netctl", "start", self._config.SPI_NET_INTERFACE]
        p = Popen(command)
        exit_code = p.wait(10)
        if exit_code != 0:
            raise Exception(f"Cannot start interface {self._config.SPI_NET_INTERFACE}")

#
# class DataSyncer(object):
#
#     def __init__(self, image_dir, port=None):
#         if port is None:
#             logging.debug("Scanning serial ports...")
#             ports = self._serial_ports()
#             if len(ports) == 0:
#                 raise Exception("No serial port found. "
#                                 "Ensure your device is plugged.")
#             elif len(ports) > 2:
#                 logging.warning("%i serial ports found:\n %s" % (len(ports), "\n\t".join(ports)))
#             port = ports[0]
#             logging.info("Using %s " % port)
#
#         self._serial_port = serial.Serial(port, self._baud, timeout=2)
#
#         start = time.time()
#         while time.time() - start < 5.0:
#             line = self._serial_port.readline()
#             if not line or line.startswith(b'#'):
#                 continue
#             line = line.rstrip()
#             if line == b"READY":
#                 self.send_status(b'BEGIN')
#                 logging.debug('Serial device ready sending "BEGIN"')
#                 break
#
#         self._image_dir = image_dir
#
#     def get_metadata(self):
#         # try five times. error if nothing still
#         tries = 0
#         while True:
#             # we read a line from serial port and remove any `\r` and `\n` character
#             line = self._serial_port.readline()
#             logging.debug(line)
#             if not line or line.startswith(b'#'):
#                 continue
#             try:
#                 lat, lng, alt, datetime = line.rstrip().split(b';')
#
#                 # when no data is available for gps coordinates, we load gps data from past metadata file
#                 # unless this file does not exist yet
#                 if alt == -1000 and lng == 0 and lat == 0:
#                     path = os.path.join(self._image_dir, self._metadata_filename)
#                     if os.path.isfile(path):
#                         with open(path, 'r') as f:
#                             data = json.load(f)
#                             if 'lat' in data and 'lng' in data and 'alt' in data:
#                                 lat = data['lat']
#                                 lng = data['lng']
#                                 alt = data['alt']
#
#                 ref_time = self._set_clock(datetime)
#
#                 meta = {'lng': float(lng),
#                         'lat': float(lat),
#                         'alt': float(alt),
#                         'datetime': ref_time}
#
#                 self._save_metadata(meta)
#                 return
#
#             except Exception as e:
#                 logging.error(e)
#                 if tries >= 5:
#                     raise e
#                 tries = tries + 1
#
#     def _save_metadata(self, metadata):
#         path = os.path.join(self._image_dir, self._metadata_filename)
#         out = json.dumps(metadata)
#         with open(path, 'w') as f:
#             f.write(out)
#
#     def _set_clock(self, datetime_str):
#         # datetime looks like 'YYYY-mm-dd HH-MM-SS UTC'
#         ref_time = datetime.datetime.strptime(datetime_str.decode(), "%Y-%m-%dT%H:%M:%S%z")
#         ref_datetime_str = ref_time.strftime('%Y-%m-%d %H:%M:%S')
#         #fixme here use timedatectl set-time "$t"
#         command = "/usr/bin/hwclock --set --date '%s' --utc --noadjfile" % ref_datetime_str
#         logging.debug(command)
#         p = Popen(command, shell=True, stderr=PIPE)
#         c = p.wait(timeout=10)
#         if c != 0:
#             error = p.stderr.read()
#             logging.error('Error setting the hardware clock. %i: %s' % (c, error))
#         return ref_datetime_str


#
# if __name__ == '__main__':
#     parser = optparse.OptionParser()
#     parser.add_option("-D", "--debug", dest="debug", default=False, help="Set DEBUG mode ON", action="store_true")
#     parser.add_option("-n", "--no-serial", dest="no_serial", default=False, help="Set DEBUG mode ON",
#                       action="store_true")
#
#     (options, args) = parser.parse_args()
#     option_dict = vars(options)
#
#     if option_dict["debug"]:
#         logging.basicConfig(level=logging.DEBUG)
#         logging.info("Logging using DEBUG SETTINGS")
#
#     if option_dict["no_serial"]:
#         logging.debug('Serial connection disabled, not expecting serial metadata')
#         serial_connection = DummySerialConnector(LOCAL_IMAGE_DIR)
#     else:
#         serial_connection = SerialConnector(LOCAL_IMAGE_DIR)
#     serial_connection.get_metadata()
#
#     serial_connection.send_status(device_id(), wait_after=1)
#     serial_connection.send_status(datetime.datetime.utcnow().strftime('T %Y-%m-%dT%H:%M:%SZ').encode(), wait_after=4)
#
#     avail = available_disk_space(LOCAL_IMAGE_PARTITION_LABEL)
#     if avail:
#         serial_connection.send_status(available_disk_space_instruction(avail), wait_after=4)
#
#         if avail < MIN_AVAILABLE_DISK_SPACE:  # less than MIN_AVAILABLE_DISK_SPACE_ % => remove old files
#             remove_old_files(LOCAL_IMAGE_DIR)
#     else:
#         logging.error('Failed to get available disk space')
#
#     spi_drive_mounted = False
#
#     if os.path.exists(os.path.join('/dev/disk/by-label', SPI_DRIVE_LABEL)):
#         if not os.path.isdir(MOUNT_DIR):
#             raise Exception('/mnt/%s  does not exist!' % SPI_DRIVE_LABEL)
#         # mount by label
#         p = Popen(['/usr/bin/mount', '-L', SPI_DRIVE_LABEL, MOUNT_DIR], stderr=PIPE)
#         c = p.wait(timeout=20)
#         if c != 0:
#             error = p.stderr.read()
#             logging.error('Failed to mount %s, error %i: %s' % (SPI_DRIVE_LABEL, c, error))
#             if b'already mounted' in error:
#                 spi_drive_mounted = True
#         else:
#             spi_drive_mounted = True
#     try:
#         if spi_drive_mounted:
#             logging.debug('Rsyncing')
#             for p in rsync_monitor(LOCAL_IMAGE_DIR, MOUNT_DIR):
#                 serial_connection.send_status(p)
#
#         else:
#             serial_connection.send_status(b'P NO SPI_DRIVE')
#         time.sleep(5)
#     finally:
#         if spi_drive_mounted:
#             serial_connection.send_status(b'P UNMOUNTING')
#             os.sync()
#             p = Popen(['/usr/bin/umount', MOUNT_DIR])
#             serial_connection.send_status(b'P DONE', wait_after=1)
#             serial_connection.send_status(device_id())
