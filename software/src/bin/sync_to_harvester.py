#!/bin/python
from optparse import OptionParser
import os
import logging
import socket
import time
import threading
from sticky_pi_device.utils import device_id, set_wifi, set_wpa, set_direct_wifi_connection, set_wifi_from_qr

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


#
# SPI_HARVESTER_NAME_PATTERN = "spi-harvester"
# SPI_DEVICE_SERVER_PORT = 80
# SPI_DEVICE_SERVER_PACEMAKER_FILE = "/var/run/sticky-pi.pmk"
# # s after which the server is considered dead/hanging
# # we will use a pacemaker mechanism to keep it alive
# SPI_SYNC_TIMEOUT = 120


class ConfigHandler(dict):
    _type_dict = {
        "SPI_HARVESTER_NAME_PATTERN": str,
        "SPI_SYNC_TIMEOUT": int,
        "SPI_DEVICE_SERVER_PORT": int,
        "SPI_DEVICE_SERVER_PACEMAKER_FILE": str,
        'SPI_IMAGE_DIR': str,
        "SPI_FLASH_GPIO": int
    }

    def __init__(self):
        super().__init__()
        for k, t in self._type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]


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

    set_wifi()
    ip = set_wpa(WPA_TIMEOUT, config.SPI_IMAGE_DIR)

    if not ip:
        logging.warning("Could not connect to data harvester using wifi hotspot. Trying to register a new qr code")
        ip = set_wifi_from_qr(config.SPI_IMAGE_DIR, config.SPI_FLASH_GPIO)
        # if not ip:
            # logging.warning("Could not connect to data harvester using wifi hotspot. ")
            # ip = set_direct_wifi_connection(config.SPI_IMAGE_DIR, DEFAULT_P2P_CONFIG_FILE, PING_HARVESTER_TIMEOUT,
            #                                 config.SPI_HARVESTER_NAME_PATTERN, FIND_HARVESTER_TIMEOUT)
        if not ip:
            logging.warning("Wifi failed too")
            exit(1)

    import uvicorn
    from zeroconf import IPVersion, ServiceInfo, Zeroconf
    import contextlib
    # ensure dir exists
    os.makedirs(os.path.join(config.SPI_IMAGE_DIR, device_id()), exist_ok=True)


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

    try:

        uvicorn_config = uvicorn.Config("sticky_pi_device.sync_server:app",
                                        host="0.0.0.0", port=config.SPI_DEVICE_SERVER_PORT,
                                        reload=False, workers=4)

        # config = Config("example:app", host="127.0.0.1", port=5000, log_level="info")
        server = Server(config=uvicorn_config)

        with open(config.SPI_DEVICE_SERVER_PACEMAKER_FILE, 'w') as f:
            f.write("")

        pace = 0
        with server.run_in_thread():
            start = time.time()
            while time.time() - start < config.SPI_SYNC_TIMEOUT or option_dict["infinite"]:
                time.sleep(1)
                mtime = os.path.getmtime(config.SPI_DEVICE_SERVER_PACEMAKER_FILE)
                if mtime != pace:
                    start = time.time()
                    pace = mtime

    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()
