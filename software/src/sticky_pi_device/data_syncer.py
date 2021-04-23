
import datetime
from subprocess import Popen, PIPE, STDOUT
import time
import logging
import os
import requests
import glob
import json
import re
from sticky_pi_device.utils import device_id
from sticky_pi_device.config_handler import ConfigHandler

def img_file_hash(path):
    stats = os.stat(path)
    # fixme. make a fast hash, e.g. using first and last bytes
    return f"hash-{stats.st_size}"


class DataSyncer(object):
    # Percent. If disk space is lower than this value, after data sync, the oldest half of the data is removed!
    _min_available_disk_space = 10

    def __init__(self, config: ConfigHandler):
        self._config = config

    def sync(self):
        if not self._ping_harvester():
            logging.info("Cannot reach host. Trying wifi")
            self._start_network_interface()
            # we don't have network immediately after the interface starts'
            start = time.time()
            while not self._ping_harvester():
                time.sleep(.5)
                # after 15s, we give up
                if time.time() - start > 15:
                    raise Exception(f"Cannot reach host {self._config.SPI_HARVESTER_HOSTNAME}")
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
                  "progress_errors":0,
                  'in_transaction': 1,
                  'available_disk_space': self._available_disk_space()}
        return status

    def _upload_images(self):
        dev_id = device_id()
        host = self._config.SPI_HARVESTER_HOSTNAME
        url_images_to_upload = f"http://{host}/images_to_upload/{dev_id}"
        url_upload = f"http://{host}/upload_device_images/{dev_id}"
        url_update_status = f"http://{host}/update_device_status/{dev_id}"

        pattern = os.path.join(self._config.SPI_IMAGE_DIR, dev_id, "*.jpg")

        files = {}
        for f in sorted(sorted(glob.glob(pattern))):
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
                        device_status["progress_errors"] += 1
            else:
                device_status["progress_skipping"] += 1
        # logging.warning(device_status)
        if device_status['available_disk_space'] < self._min_available_disk_space:
            logging.warning("Removing old files")
            self._remove_old_files()

        # Formally finish transaction
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

    def _available_disk_space(self):
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
            return round(avail,2)
        else:
            raise Exception("Cannot assess space left on device")

    def _remove_old_files():
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