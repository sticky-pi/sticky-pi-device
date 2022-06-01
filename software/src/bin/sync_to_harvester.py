#!/bin/python
from optparse import OptionParser
import os
import logging
import socket
import time
import threading
import tempfile

import RPi.GPIO as GPIO  # import RPi.GPIO module


from sticky_pi_device.utils import device_id, set_wifi, set_wpa,  \
    set_wifi_from_qr, mount_persistent_partition, unmount_persistent_partition
from sticky_pi_device.sync_server import CustomServer


WPA_TIMEOUT = 8  # s

class ConfigHandler(dict):
    _type_dict = {
        "SPI_HARVESTER_NAME_PATTERN": str,
        "SPI_SYNC_TIMEOUT": int,
        "SPI_DEVICE_SERVER_PORT": int,
        "SPI_DEVICE_SERVER_PACEMAKER_FILE": str,
        'SPI_IMAGE_DIR': str,
        "SPI_FLASH_GPIO": int,
        'SPI_PERSISTENT_PARTITION_LABEL': str,
    }

    def __init__(self):
        super().__init__()
        for k, t in self._type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]

class Blinker(threading.Thread):
    def __init__(self, period: float, flash_gpio:int):
        self._period = period
        self._flash_gpio = flash_gpio
        self._to_stop = False
        super().__init__()


    def run(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._flash_gpio, GPIO.OUT)  # set a port/pin as an output
        try:
            while not self._to_stop:
                time.sleep(self._period)
                GPIO.output(self._flash_gpio, 1)
                time.sleep(0.01)
                GPIO.output(self._flash_gpio, 0)
        finally:
            GPIO.output(self._flash_gpio, 0)

    def set_period(self, period: float):
        self._period = period

    def stop(self):
        self._to_stop = True


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-n", "--no-files",
                      dest="no_files",
                      help="Only connect for metadata. Do not upload any files.",
                      default=False,
                      action='store_true')

    parser.add_option("-p", "--periodic",
                      dest="periodic",
                      help="whether sync was automatically triggered",
                      default=False,
                      action='store_true')

    parser.add_option("-f", "--first-boot",
                      dest="first_boot",
                      help="whether this is a first boot",
                      default=False,
                      action='store_true')

    parser.add_option("-q", "--qr-code-file",
                      dest="qr_code_file",
                      help="A file containing a qrcode to describe a network to try direct, non-persistent connection",
                      default=None,
                      type=str)

    parser.add_option("-u", "--user-requested",
                      dest="user_requested",
                      help="whether the user explicitly requested sync -- as opposed to an automatic trigger",
                      default=False,
                      action='store_true')

    parser.add_option("-b", "--battery-level",
                      dest="battery_level",
                      help="The remaining battery percent",
                      default="0", type=str)

    parser.add_option("-i", "--infinite",
                      dest="infinite",
                      help="Keep server running (dev)",
                      default=False, action='store_true')

    (options, args) = parser.parse_args()
    option_dict = vars(options)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    config = ConfigHandler()
    blinker = Blinker(2.0, config.SPI_FLASH_GPIO)
    blinker.start()

    tmp_mount = tempfile.mkdtemp()
    mount_persistent_partition(config.SPI_PERSISTENT_PARTITION_LABEL, tmp_mount)
    try:
        set_wifi()

        ip = None

        if option_dict["qr_code_file"] is None:
            logging.info("Trying to connect to pre-paired networks")
            ip = set_wpa(WPA_TIMEOUT, tmp_mount)

        # try to scan image for qr code
        # register the qr code unless it has a F:1 field (forget)
        # this is for temporary networks (android ap)
        # we do that only for button pushed (i.e. non-periodic)
        if not ip and  not option_dict["periodic"]:
            ip = ""
            logging.info("Connecting using QR code")
            ip = set_wifi_from_qr(tmp_mount, img_file=option_dict["qr_code_file"])
        # failed to find any IP or irrelevant as it is a periodic boot
        if not ip:
            if not ip:
                logging.warning("Wifi from registered net failed too")
                exit(1)

        blinker.set_period(5.0)


        from zeroconf import IPVersion, ServiceInfo, Zeroconf
        import contextlib
        # ensure dir exists
        os.makedirs(os.path.join(config.SPI_IMAGE_DIR, device_id()), exist_ok=True)

        ip_version = IPVersion.V4Only
        # ip_version = IPVersion.V6Only
        desc = {'path': '/'}
        info = ServiceInfo(
            "_http._tcp.local.",
            f"StickyPi-{device_id()}._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=config.SPI_DEVICE_SERVER_PORT,
            properties=desc,
            server=f"spi-{device_id()}.local.",
        )

        zeroconf = Zeroconf(ip_version=ip_version)
        zeroconf.register_service(info)
        os.environ['CURRENT_BATTERY_LEVEL'] = option_dict["battery_level"]
        os.environ['FIRST_BOOT'] = str(int(option_dict["first_boot"]))
        os.environ['SPI_IS_MOCK_DEVICE'] = "0"

        server = CustomServer("0.0.0.0", config.SPI_DEVICE_SERVER_PORT)
        try:
            logging.info(f'Starting server at {time.time()}')
            server.start()
            logging.info('Started')

            with open(config.SPI_DEVICE_SERVER_PACEMAKER_FILE, 'w') as f:
                f.write("")

            pace = 0
            # with server.run_in_thread():
            start = time.time()
            while time.time() - start < config.SPI_SYNC_TIMEOUT or option_dict["infinite"]:
                if not os.path.exists(config.SPI_DEVICE_SERVER_PACEMAKER_FILE):
                    logging.info(f'No pacemaker file. exiting {time.time()}')
                    break
                mtime = os.path.getmtime(config.SPI_DEVICE_SERVER_PACEMAKER_FILE)

                time.sleep(1)
                if mtime != pace:
                    start = time.time()
                    pace = mtime

        finally:
            logging.info(f'Closing http server')
            server.stop()
            logging.info(f'Closing zeroconf')
            zeroconf.unregister_service(info)
            zeroconf.close()
    finally:
        logging.info(f'Stopping blinker')
        blinker.stop()
        logging.info(f'Unmounting persistent partition')
        unmount_persistent_partition(tmp_mount)
