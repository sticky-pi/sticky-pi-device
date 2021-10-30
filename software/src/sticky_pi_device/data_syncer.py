import time
import os
import logging
import requests
import glob
import json

from sticky_pi_device._version import __version__


_type_dict = {
    "SPI_DRIVE_LABEL": str,
    "SPI_IMAGE_DIR": str,
    "SPI_LOG_FILENAME": str,
    "SPI_METADATA_FILENAME": str,
    "SPI_HARVESTER_HOSTNAME": str,
    "SPI_WIFI_SSID": str,
    "SPI_WIFI_PASSWORD": str,
}

class ConfigHandler(dict):

    def __init__(self):
        self["SPI_VERSION"] = __version__,

        super().__init__()
        for k, t in self._type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]


def img_file_hash(path):
    stats = os.stat(path)
    # fixme. make a fast hash, e.g. using first and last bytes
    return f"hash-{stats.st_size}"


class NoHostOrNetworkException (Exception):
    pass

class DataSyncer(object):
    # Percent. If disk space is lower than this value, after data sync, the oldest half of the data is removed!
    _min_available_disk_space = 10
    _upload_pool_size = 4
    _interface_timeout = 5  # s
    _interface_timeout_long = 20  # s when user requested (button). we wait way longer for interface!

    def __init__(self, user_requested = False, periodic=False, battery_level=None, no_files = False, dev_id = None):
        self._config = ConfigHandler()
        self._user_requested = user_requested
        self._periodic = periodic
        self._battery_level = battery_level
        self._upload_files = not no_files
        if dev_id is None:
            from sticky_pi_device.utils import device_id
            self._device_id = device_id()

        else:
            self._device_id = dev_id
        self._logfile_path = os.path.join(self._config.SPI_IMAGE_DIR, self._config.LOG_FILENAME)

    def sync(self):
        # typically, interface is up 5s before host is ping able
        start = time.time()
        if self._user_requested:
            timeout = self._interface_timeout
        else:
            timeout = self._interface_timeout_long

        while not self._is_any_net_interface_up():
            time.sleep(1)
            if time.time() - start > timeout:
                logging.info("No network interface, not syncing")
                return
        if not self._ping_harvester():
            raise NoHostOrNetworkException(f"Cannot reach host {self._config.SPI_HARVESTER_HOSTNAME}")

        self._get_harvester_status()

        if self._upload_files:
            self._upload_images()

    def _is_any_net_interface_up(self):
        # grep all interfaces that are UP
        response = os.system("ip a | grep ^[0-9] | grep 'state UP' -q")
        return response == 0

    def _ping_harvester(self, timeout = 15):
        host = self._config.SPI_HARVESTER_HOSTNAME
        start = time.time()
        while time.time() - start < timeout:
            response = os.system(f"ping -c 1 " + host)
            if response == 0:
                return True
            time.sleep(1)
        return False

    def _get_device_status(self):
        status = {"version": self._config.SPI_VERSION,
                  "battery_level": self._battery_level,
                  "periodic": self._periodic,
                  "user_requested": self._user_requested,
                  "progress_skipping": 0, "progress_to_skip": 0,
                  "progress_uploading": 0, "progress_to_upload": 0,
                  "progress_errors": 0,
                  'in_transaction': 1,
                  'available_disk_space': self._available_disk_space()}
        return status

    def _upload_images(self):
        dev_id = self._device_id
        host = self._config.SPI_HARVESTER_HOSTNAME
        url_images_to_upload = f"http://{host}/images_to_upload/{dev_id}"
        url_upload = f"http://{host}/upload_device_images/{dev_id}"
        url_upload_log = f"http://{host}/upload_device_logfile/{dev_id}"
        url_update_status = f"http://{host}/update_device_status/{dev_id}"

        pattern = os.path.join(self._config.SPI_IMAGE_DIR, dev_id, "*.jpg")

        files = {}
        for f in sorted(glob.glob(pattern)):
            files[os.path.basename(f)] = img_file_hash(f)

        # todo
        # additional_headers['content-encoding'] = 'gzip'
        # request_body = zlib.compress(json.dumps(post_data))
        # r = requests.post('', data=request_body, headers=additional_headers)

        response = requests.post(url_images_to_upload, json=files)
        assert response.status_code == 200, response
        image_status = json.loads(response.content)
        device_status = self._get_device_status()

        for image, status in image_status.items():
            if status == "uploaded":
                device_status["progress_to_skip"] += 1
            else:
                device_status["progress_to_upload"] += 1

        def upload_one_image(image):
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
                        device_status["progress_errors"] += 1
            else:
                device_status["progress_skipping"] += 1

        # for image in sorted(image_status.keys()):
        #    upload_one_image(image)
        from multiprocessing.pool import ThreadPool as Pool
        with Pool(self._upload_pool_size) as p:
             out = p.map(upload_one_image, sorted(image_status.keys()))

        # logging.warning(device_status)
        if device_status['available_disk_space'] < self._min_available_disk_space:
            logging.warning("Removing old files")
            self._remove_old_files()

        # flush logfle to have last messages
        # logger = logging.getLogger()
        # logger.handlers[0].flush()

        # Formally finish transaction
        with open(self._logfile_path, 'rb') as f:
            #fixme, gzip loglife (or last n lines)! or roll log when large
            payload = {'logfile': (os.path.basename(self._logfile_path), f, 'application/octet-stream'),
                       'status': ('status', json.dumps(device_status), 'application/json'),
                       'hash': ('hash', json.dumps(img_file_hash(self._logfile_path)), 'application/json')
                       }
            response = requests.post(url_upload_log, files=payload)


        device_status['in_transaction'] = 0
        response = requests.post(url_update_status, json=device_status)
        assert response.status_code == 200, response
        logging.warning("sync done")

    def _get_harvester_status(self):
        url_harvester_status = f"http://{self._config.SPI_HARVESTER_HOSTNAME}/status"
        response = requests.get(url_harvester_status)
        if response.status_code != 200:
            raise Exception(f"Unexpected response from server: {response.status_code}")
        harvester_status = json.loads(response.content)
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(harvester_status["time"]))
        command = ["hwclock", "--set", "--date", time_str, "--utc", "--noadjfile"]
        p = Popen(command)
        exit_code = p.wait(5)
        if exit_code != 0:
            #fixme should be an error!
            # raise Exception(f"Cannot set localtime to {time_str}")
            logging.error(f"Cannot set localtime to {time_str}")

        meta = harvester_status["gps_coordinates"]
        meta["datetime"] = time_str
        path = os.path.join(self._config.SPI_IMAGE_DIR, self._config.SPI_METADATA_FILENAME)
        with open(path, 'w') as f:
            f.write(json.dumps(meta))

    def _available_disk_space(self):
        import re
        from subprocess import Popen, PIPE

        label = self._config.SPI_DRIVE_LABEL
        # command = "df $(blkid -o list | grep %s| cut -f 1 -d ' ') --output=used,size | tail -1 | tr -s ' '" % label
        command = "df %s --output=used,size | tail -1 | tr -s ' '" % self._config.SPI_IMAGE_DIR
        p = Popen(command,  shell=True, stderr=PIPE, stdout=PIPE)
        c = p.wait(timeout=10)
        if c != 0:
            error = p.stderr.read()
            logging.error('Failed to display available space on disk labeled %s. %s' % (label, error))
        output = p.stdout.read()
        match = re.findall(b"(\d+) (\d+)", output)
        if match:
            num, den = match[0]
            avail = 100 - (100 * int(num)) / int(den)
            return round(avail, 2)
        else:
            raise Exception("Cannot assess space left on device")

    def _remove_old_files(self):
        all_files = []
        # should not be any , but remove them if the exist
        temp_files = []

        for g in sorted(glob.glob(os.path.join(self._config.SPI_IMAGE_DIR, '**','*.jpg*'))):
            if g.endswith("-tmp"):
                temp_files.append(g)
            elif g.endswith(".jpg"):
                all_files.append(g)

        # remove all but last temp files, in case
        for r in temp_files[0: -1]:
            os.remove(r)

        # remove half of the images
        for r in all_files[0: (len(all_files) // 2)]:
            os.remove(r)
