import tempfile
import logging
import os
import socket
import fcntl
import struct
import requests
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
# from threading
import shutil
import time

def get_ip_address(ifname):
    ifname = bytes(ifname, "ascii")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        fd = fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )
    except OSError:
        return

    return socket.inet_ntoa(fd[20:24])

def ping(x):
    if os.system(f"ping -c 1 -W 0.2 {x} > /dev/null 2>&1") == 0:
        return x


def img_file_hash( path):
    stats = os.stat(path)
    return str(stats.st_size)


class DeviceHandler(object):

    def __init__(self, ip,  datetime, device_id, version, battery_level, available_disk_space):
        #fixme
        self._sync_dir_root = tempfile.mkdtemp(prefix="sticky-pi-harvester")

        self._ip = ip
        self._datetime = datetime
        self._device_id = device_id
        self._version = version
        self._battery_level = battery_level
        self._available_disk_space = available_disk_space

        self._update_metadata()

        self._image_list = self._images()
    def _update_metadata(self):
        payload = {"datetime": time.time(),
                   "lat": 0,
                   "lng": 0,
                   "alt": 0}
        resp = requests.post(f"http://{self._ip}/metadata", json=payload)

        if resp.status_code != 200:
            raise Exception(f"Could not update metadata on {self._device_id}")

    def status(self):
        return { "ip": self._ip,
                 "device_id": self._device_id,
                 "version": self._version,
                 "battery_level": self._battery_level,
                 "available_disk_space": self._available_disk_space,
                 "images": self._image_list}

    def _images(self):
        images = requests.get(f"http://{self._ip}/images")
        out = {}
        if requests.status_codes == 200:

            raise f"Cannot get images for {self._device_id}"
        #fixme, sort by key
        for i, hash in images.json().items():
            path = f"{self._device_id}.{i}.jpg"
            out[path] = {"hash": hash}

        return out
    def get_all_images(self):
        pool = ThreadPool(4)

        pool.map(lambda p :self._get_one_image(p), self._image_list.keys())

    def _get_one_image(self, path):
        logging.info(f"Getting {path}")
        tmp_file = tempfile.mktemp(prefix=path, suffix=".tmp")
        dst = os.path.join(self._sync_dir_root, self._device_id, path)

        if os.path.exists(dst) and self._image_list[path]["hash"] == hash(dst):
            # Skipping
            return

        try:
            url = f"http://{self._ip}/static/{path}"
            resp = requests.get(url, stream=True)
            if resp.status_code == 200:
                with open(tmp_file, 'wb') as out_file:
                    shutil.copyfileobj(resp.raw, out_file)

                # sanity check
                assert self._image_list[path]["hash"] == img_file_hash(tmp_file), f"Failed sanity check on downloaded image {path}"

                if not os.path.isdir(os.path.dirname(dst)):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(tmp_file, dst)
                logging.info(f"Downloaded {path}")
        finally:
            if os.path.isfile(tmp_file):
                os.unlink(tmp_file)



logger = logging.getLogger()
logger.setLevel(logging.INFO)
ip = get_ip_address("wlp0s20f3")
device_map = [] # id -> ip, status,...
if not ip:
    raise Exception("No connection")
ip = ".".join(ip.split(".")[0:3])
all_ips = [ip + "." + str(i) for i in range(2, 255)]
with Pool(256) as p:
    device_ips = [i for i in p.map(ping, all_ips) if i]

for dip in device_ips:
    try:
        resp = requests.get(f"http://{dip}/status")
    except requests.exceptions.ConnectionError:
        continue

    if resp.status_code == 200:
        try:
            a = resp.json()
            assert "device_id" in a
            id = a["device_id"]
            if id not in device_map:
                device_map.append(DeviceHandler(ip=dip, **a))

        except Exception as e:
            logging.error(f"Could not handle {dip}")
            logging.error(e)




for d in device_map:
    d.get_all_images()
