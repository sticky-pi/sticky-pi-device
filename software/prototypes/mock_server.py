#!/bin/python

import shutil
import tempfile
import os
import logging
import socket
import time
import threading
import contextlib
from sticky_pi_device.utils import get_ip_address
import uvicorn
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from sticky_pi_device.sync_server import CustomServer

# IFNAME= "wlp0s20f3"
IFNAME = "enp0s20f0u2"

CURRENT_BATTERY_LEVEL = "0"
SPI_DRIVE_LABEL = "spi-drive"
SPI_LOG_FILENAME = "test.log"
SPI_METADATA_FILENAME = "metadata.json"

SPI_HARVESTER_NAME_PATTERN = "spi-harvester"
FIND_HARVESTER_TIMEOUT = 10  # s
PING_HARVESTER_TIMEOUT = 20  # s
WPA_TIMEOUT = 5  # s


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
        self._server = CustomServer("0.0.0.0", self._port)

    def _make_dummy_images(self, n=(100, 300)):
        import datetime
        import random
        from PIL import Image

        target = os.path.join(SPI_IMAGE_DIR, self._device_name)

        for i in range(int(random.uniform(*n))):
            timestamp = round(random.uniform(1.6e9, 1.7e9))
            dt = datetime.datetime.fromtimestamp(timestamp)
            filename = f'{self._device_name}.{dt.strftime("%Y-%m-%d_%H-%M-%S")}.jpg'
            path = os.path.join(target, dt.strftime("%Y-%m-%d"), filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)

            width, height = 1600, 1200
            valid_solid_color_jpeg = Image.new(mode='RGB', size=(width, height),
                                               color=tuple([int(random.uniform(0,255)) for i in range(3)]))
            valid_solid_color_jpeg.save(path)


    def run(self) -> None:
        import random
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
        SPI_VERSION = "3.1.0"
        SPI_DEVICE_SERVER_PACEMAKER_FILE = os.path.join(SPI_IMAGE_DIR, self._device_name, "pacemaker.pcmk")

        zeroconf = Zeroconf(ip_version=ip_version)
        zeroconf.register_service(info)
#        os.environ['CURRENT_BATTERY_LEVEL'] = CURRENT_BATTERY_LEVEL
        os.environ['FIRST_BOOT'] = "1"
        os.environ['SPI_DRIVE_LABEL'] = SPI_DRIVE_LABEL
        os.environ['SPI_IMAGE_DIR'] = SPI_IMAGE_DIR
        os.environ['SPI_LOG_FILENAME'] = self._device_name + "_" + SPI_LOG_FILENAME
        os.environ['SPI_IS_MOCK_DEVICE'] = "1"
        os.environ['SPI_METADATA_FILENAME'] = SPI_METADATA_FILENAME
        os.environ['SPI_VERSION'] = SPI_VERSION
        os.environ['SPI_DEVICE_SERVER_PACEMAKER_FILE'] = SPI_DEVICE_SERVER_PACEMAKER_FILE
        os.environ['MOCK_DEVICE_ID'] = self._device_name

        os.environ['CURRENT_BATTERY_LEVEL'] = "%d" % round(random.uniform(0, 110))
        print(os.environ['CURRENT_BATTERY_LEVEL'])

        logfile = os.path.join(SPI_IMAGE_DIR, os.environ['SPI_LOG_FILENAME'])


        with open(logfile, 'w') as f:
            for i in range(100):
                f.write(f"some line for my dummy log file, {i}")

        try:
            # command = f"gunicorn -b 0.0.0.0:{self._port} --threads 2  --worker-class uvicorn.workers.UvicornWorker sticky_pi_device.sync_server:app &"
            # os.system(command)
            # with open(SPI_DEVICE_SERVER_PACEMAKER_FILE, 'w') as f:
            #     f.write("")
            # while not self._to_stop:
            #     time.sleep(1)
            #     if not os.path.exists(SPI_DEVICE_SERVER_PACEMAKER_FILE):
            #         self.stop()
            #
            # uvicorn_config = uvicorn.Config("sticky_pi_device.sync_server:app",
            #                                 host="0.0.0.0", port=self._port,
            #                                 reload=False, workers=4)

            with open(SPI_DEVICE_SERVER_PACEMAKER_FILE, 'w') as f:
                f.write("")


            # httpd = HTTPServer(server_address, S)
            # print(self._port)
            # httpd.serve_forever()
            self._server.start()
            # # self._server = Server(config=uvicorn_config)
            # with self._server.run_in_thread():
            while not self._to_stop:
                time.sleep(1)
                if not os.path.exists(SPI_DEVICE_SERVER_PACEMAKER_FILE):

                    self.stop()
            print('stopping')
        except KeyboardInterrupt:
            self.stop()
        finally:

            zeroconf.unregister_service(info)
            zeroconf.close()

    def stop(self):

        self._server.stop()
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
        ip = get_ip_address(IFNAME)

        if i:
            dev = [MockDevice(8080 + i, "%08d" %i , ip)]
        else:
            dev = [
                # MockDevice(8081, "00000001", ip),
                # MockDevice(8082, "00000002", ip),
                # MockDevice(8083, "00000003", ip),
                MockDevice(8084, "00000004", ip),
                # MockDevice(8085, "00000005", ip),
                # MockDevice(8086, "00000006", ip),
                # MockDevice(8087, "00000007", ip),
                # MockDevice(8088, "00000008", ip),
                # MockDevice(8089, "00000009", ip),
                # MockDevice(8090, "00000010", ip),
                ]

        for d in dev:
            d.start()
            time.sleep(2)

        stop =False

        while not stop:
            try:
                time.sleep(1)
                keep_going = False
                for d in dev:
                    if d.is_alive():
                        keep_going = True
                if not keep_going:
                    stop = True
            except KeyboardInterrupt:
                for d in dev:
                    d.join()
                stop = True
    finally:
        shutil.rmtree(SPI_IMAGE_DIR)
