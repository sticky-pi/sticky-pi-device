#!/bin/python
import shutil
import tempfile
from optparse import OptionParser
import subprocess
import os
import re
import logging
import socket
import fcntl
import struct
import time
import threading
import netifaces
import contextlib
from sticky_pi_device.utils import device_id, get_ip_address, set_wpa, set_direct_wifi_connection
import uvicorn
from zeroconf import IPVersion, ServiceInfo, Zeroconf


IFNAME= "wlp0s20f3"
# IFNAME = "enp0s20f0u2"
USE_DIRECT_WIFI = False
CURRENT_BATTERY_LEVEL = "0"
SPI_DRIVE_LABEL = "spi-drive"
SPI_LOG_FILENAME = "test.log"
SPI_METADATA_FILENAME = "metadata.json"

SPI_HARVESTER_NAME_PATTERN = "spi-harvester"
FIND_HARVESTER_TIMEOUT = 10  # s
PING_HARVESTER_TIMEOUT = 20  # s
WPA_TIMEOUT = 5  # s
DEFAULT_P2P_CONFIG_FILE = """
ctrl_interface=DIR=/var/run/wpa_supplicant
driver_param=use_p2p_group_interface=1
persistent_reconnect=1
device_name=DIRECT-sticky-pi
device_type=6-0050F204-1
config_methods=virtual_push_button
p2p_go_intent=0
p2p_go_ht40=1
country=US
"""


class ConfigHandler(dict):
    _type_dict = {
        "SPI_HARVESTER_NAME_PATTERN": str,
        "SPI_SYNC_TIMEOUT": int,
        "SPI_DEVICE_SERVER_PACEMAKER_FILE": str,
        'SPI_IMAGE_DIR': str
    }

    def __init__(self):
        super().__init__()
        for k, t in self._type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]


class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


from multiprocessing import Process

class MockDevice(Process):
    def __init__(self, port, device_name, ip_addr):
        super().__init__()
        self._port = port
        self._device_name = device_name
        self._ip = ip_addr
        self._to_stop = False

    def _make_dummy_images(self, n=(8,20)):
        import datetime
        import random
        from PIL import Image

        target = os.path.join(SPI_IMAGE_DIR, self._device_name)
        for i in range(int(random.uniform(*n))):
            timestamp = round(random.uniform(1.6e9, 1.7e9))
            dt = datetime.datetime.fromtimestamp(timestamp)
            filename = f'{self._device_name}.{dt.strftime("%Y-%m-%d_%H-%M-%S")}.jpg'
            path = os.path.join(target, filename)


            width, height = 1600, 1200
            valid_solid_color_jpeg = Image.new(mode='RGB', size=(width, height),
                                               color=tuple([int(random.uniform(0,255)) for i in range(3)]))
            valid_solid_color_jpeg.save(path)
            # with open(path, 'wb') as f:
            #     f.write(os.urandom(1024 * 1024))

    def run(self) -> None:
        os.makedirs(os.path.join(SPI_IMAGE_DIR, self._device_name), exist_ok=True)
        self._make_dummy_images()
        ip_version = IPVersion.V4Only

        desc = {'path': '/'}
        info = ServiceInfo(
            "_http._tcp.local.",
            f"StickyPi-{self._device_name}._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=self._port,
            properties=desc,
            server=f"spi-{self._device_name}.local.",
        )
        SPI_VERSION = "1"
        SPI_DEVICE_SERVER_PACEMAKER_FILE = os.path.join(SPI_IMAGE_DIR, self._device_name, "pacemaker.pcmk")

        zeroconf = Zeroconf(ip_version=ip_version)
        zeroconf.register_service(info)
        os.environ['CURRENT_BATTERY_LEVEL'] = CURRENT_BATTERY_LEVEL
        os.environ['FIRST_BOOT'] = "1"
        os.environ['SPI_DRIVE_LABEL'] = SPI_DRIVE_LABEL
        os.environ['SPI_IMAGE_DIR'] = SPI_IMAGE_DIR
        os.environ['SPI_LOG_FILENAME'] = SPI_LOG_FILENAME
        os.environ['SPI_IS_MOCK_DEVICE'] = "1"
        os.environ['SPI_METADATA_FILENAME'] = SPI_METADATA_FILENAME
        os.environ['SPI_VERSION'] = SPI_VERSION
        os.environ['SPI_DEVICE_SERVER_PACEMAKER_FILE'] = SPI_DEVICE_SERVER_PACEMAKER_FILE
        os.environ['MOCK_DEVICE_ID'] = self._device_name

        try:

            uvicorn_config = uvicorn.Config("sticky_pi_device.sync_server:app",
                                            host="0.0.0.0", port=self._port,
                                            reload=False, workers=4)

            self._server = Server(config=uvicorn_config)
            with self._server.run_in_thread():
                while not self._to_stop:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

        finally:

            zeroconf.unregister_service(info)
            zeroconf.close()

    def stop(self):
        self._server.should_exit =True
        self._to_stop = True


if __name__ == '__main__':
    import sys

    try :
        i = int(sys.argv[1])
    except IndexError as e:
        i = None
    SPI_IMAGE_DIR = tempfile.mkdtemp()
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        os.makedirs(SPI_IMAGE_DIR, exist_ok=True)
        if USE_DIRECT_WIFI:
            ip = set_direct_wifi_connection(SPI_IMAGE_DIR, DEFAULT_P2P_CONFIG_FILE, PING_HARVESTER_TIMEOUT,
                                            SPI_HARVESTER_NAME_PATTERN, FIND_HARVESTER_TIMEOUT,
                                            interface=IFNAME)
        else:
            ip = get_ip_address(IFNAME)

        if i:
            dev = [MockDevice(8080 + i, "%08d" %i , ip)]
        else:
            dev = [
                MockDevice(8081, "00000001", ip),
                MockDevice(8082, "00000002", ip),
                MockDevice(8083, "00000003", ip),
                MockDevice(8084, "00000004", ip),
                MockDevice(8085, "00000005", ip),
                MockDevice(8086, "00000006", ip),
                ]

        for d in dev:
            d.start()
            time.sleep(2)

        stop =False
        while not stop:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                for d in dev:
                    d.join()
                stop = True
    finally:
        shutil.rmtree(SPI_IMAGE_DIR)
