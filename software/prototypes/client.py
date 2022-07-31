import tempfile

import re
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

import logging

from typing import cast

from IPython.lib.display import IFrame
from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes

SPI_ZEROCONF_SERVICE_PREFIX = "StickyPi-"
IFNAME= "wlp0s20f3"


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


def img_file_hash(path):
    stats = os.stat(path)
    return str(stats.st_size)


from threading import Thread


class DeviceHandler(Thread):
    _initial_attempts = 5
    _pace_interval = 10 #s
    def __init__(self, ip, prospective_device_name):
        # fixme

        self._status = {}
        self._ip = ip
        self._device_id = prospective_device_name
        self._n_to_download = None
        self._n_downloaded = 0
        self._n_skipped = 0
        self._n_errored = 0

        self._datetime = None
        self._version = None
        self._battery_level = None
        self._available_disk_space = None
        self._last_pace = time.time()
        super().__init__()

    def run(self) -> None:
        sync_dir_root = tempfile.mkdtemp(prefix=f"sticky-pi-harvester-{self._device_id}-")
        try:

            retry = 0
            a = None
            while retry < self._initial_attempts:
                try:
                    resp = requests.get(f"http://{self._ip}/status")
                    if resp.status_code == 200:
                        a = resp.json()
                        break
                except requests.exceptions.ConnectionError as e:
                    time.sleep(1)
                    pass

            if not a:
                raise Exception(f"Failed to sync {self._ip}, {self._device_id}")

            logging.info(a)
            assert "device_id" in a
            id = a["device_id"]

            assert id == self._device_id, f"{id} != {self._device_id}"

            self._datetime = a["datetime"]
            self._version = a["version"]
            self._battery_level = a["battery_level"]
            self._available_disk_space = a["available_disk_space"]

            self._update_metadata()
            image_list = self._images()
            self._get_all_images(image_list, sync_dir_root)

        finally:
            shutil.rmtree(sync_dir_root)

    def _update_metadata(self):
        payload = {"datetime": time.time(),
                   "lat": 0,
                   "lng": 0,
                   "alt": 0}
        resp = requests.post(f"http://{self._ip}/metadata", json=payload)

        if resp.status_code != 200:
            raise Exception(f"Could not update metadata on {self._device_id}")

    def _keep_alive(self):
        now = time.time()
        if now - self._last_pace < self._pace_interval:
            return

        payload = {"device_id": self._device_id}
        resp = requests.post(f"http://{self._ip}/keep_alive", json=payload)

        if resp.status_code != 200:
            raise Exception(f"Could not keep alive {self._device_id}")

        self._last_pace = now

    def status(self):
        return {"ip": self._ip,
                "device_id": self._device_id,
                "version": self._version,
                "battery_level": self._battery_level,
                "available_disk_space": self._available_disk_space,
                "n_downloaded": self._n_downloaded,
                "n_to_download": self._n_to_download,
                "is_alive": self.is_alive()}

    def _images(self):
        images = requests.get(f"http://{self._ip}/images")
        out = {}
        if requests.status_codes == 200:
            raise f"Cannot get images for {self._device_id}"
        # fixme, sort by key
        for i, hash in images.json().items():
            path = f"{self._device_id}.{i}.jpg"
            out[path] = {"hash": hash}
        self._n_to_download = len(out)
        return out

    def _get_all_images(self, images, target_dir):
        pool = ThreadPool(4)
        pool.map(lambda p: self._get_one_image(p, target_dir, images), images.keys())

    def _get_one_image(self, path, target_dir, image_map):
        logging.info(f"Getting {path}")
        tmp_file = tempfile.mktemp(prefix=path, suffix=".tmp")
        dst = os.path.join(target_dir, self._device_id, path)

        if os.path.exists(dst) and image_map[path]["hash"] == hash(dst):
            self._n_skipped += 1
            return

        try:
            url = f"http://{self._ip}/static/{path}"
            resp = requests.get(url, stream=True)
            if resp.status_code == 200:
                with open(tmp_file, 'wb') as out_file:
                    shutil.copyfileobj(resp.raw, out_file)

                # sanity check
                assert image_map[path]["hash"] == img_file_hash(
                    tmp_file), f"Failed sanity check on downloaded image {path}"

                if not os.path.isdir(os.path.dirname(dst)):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(tmp_file, dst)
                self._keep_alive()
                logging.info(f"Downloaded {path}")
                self._n_downloaded += 1

        except Exception as e:
            self._n_errored += 1
            logging.error(e)

        finally:
            if os.path.isfile(tmp_file):
                os.unlink(tmp_file)


def on_service_state_change(
        zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange) -> None:
    print(f"Service {name} of type {service_type} state changed: {state_change}")
    global device_map

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        print("Info from zeroconf.get_service_info: %r" % (info))
        if not info:
            logging.warning(" No info")
            return

        pattern = f'{SPI_ZEROCONF_SERVICE_PREFIX}(?P<device_id>.{{8}})\\._http\\._tcp\\.local\\.'
        a = re.match(pattern, info.name)
        if not a:
            logging.info(f"Excluding device {info.name}: does not match {pattern}")
            return
        prospective_device_name = a.groupdict()["device_id"]

        addresses = [f"{addr}:{cast(int, info.port)}" for addr in info.parsed_scoped_addresses()]
        assert len(addresses) > 0
        dip = addresses[0]
        if prospective_device_name in device_map and not device_map[prospective_device_name].is_alive():
            device_map[prospective_device_name].join(5)
            del device_map[prospective_device_name]

        if prospective_device_name not in device_map:
            device_map[prospective_device_name] = DeviceHandler(ip=dip, prospective_device_name=prospective_device_name)
            device_map[prospective_device_name].start()

        # except Exception as e:
        #     logging.error(f"Could not handle {dip}")
        #     logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    device_map = {}

    ip_version = IPVersion.V4Only
    zeroconf = Zeroconf(ip_version=ip_version)

    services = ["_http._tcp.local."]

    browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    try:
        while True:
            time.sleep(1)
            logging.info("Monitoring threads")
            for did, d in device_map.items():
                logging.info(d.status())




    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# ip = get_ip_address("wlp0s20f3")
# device_map = [] # id -> ip, status,...
# if not ip:
#     raise Exception("No connection")
# ip = ".".join(ip.split(".")[0:3])
# all_ips = [ip + "." + str(i) for i in range(2, 255)]
# with Pool(256) as p:
#     device_ips = [i for i in p.map(ping, all_ips) if i]
#
# for dip in device_ips:
#     try:
#         resp = requests.get(f"http://{dip}/status")
#     except requests.exceptions.ConnectionError:
#         continue
#
#     if resp.status_code == 200:
#         try:
#             a = resp.json()
#             assert "device_id" in a
#             id = a["device_id"]
#             if id not in device_map:
#                 device_map.append(DeviceHandler(ip=dip, **a))
#
#         except Exception as e:
#             logging.error(f"Could not handle {dip}")
#             logging.error(e)
#
#
#
#
# for d in device_map:
#     d.get_all_images()
