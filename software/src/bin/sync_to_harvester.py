#!/bin/python
from optparse import OptionParser
import subprocess
import os
import re
import logging
import socket
import fcntl
import struct
import contextlib
import time
import threading
import uvicorn

import netifaces

from sticky_pi_device.utils import device_id

FIND_HARVESTER_TIMEOUT = 10  # s
PING_HARVESTER_TIMEOUT = 20  # s


#
# SPI_HARVESTER_NAME_PATTERN = "spi-harvester"
# SPI_DEVICE_SERVER_PORT = 80
# SPI_DEVICE_SERVER_PACEMAKER_FILE = "/var/run/sticky-pi.pmk"
# # s after which the server is considered dead/hanging
# # we will use a pacemaker mechanism to keep it alive
# SPI_SYNC_TIMEOUT = 120


def find_harvester():
    start = time.time()
    while time.time() - start < FIND_HARVESTER_TIMEOUT:
        try:
            peers = subprocess.check_output("wpa_cli p2p_peers", shell=True, universal_newlines=True)
        except subprocess.CalledProcessError:
            time.sleep(0.5)
            continue
        peers = peers.splitlines()
        for p in peers:
            device = subprocess.check_output(f"wpa_cli p2p_peer {p}", shell=True,
                                             universal_newlines=True).splitlines()
            if len(device) < 2:
                continue
            mac = device[1]
            for line in device:
                match = re.match(f"device_name={config.SPI_HARVESTER_NAME_PATTERN}", line)
                if match:
                    logging.info(f"Found {match.string}, mac={mac}")
                    return mac
    logging.warning(f"Did not find any matching network amongst {len(peers)} peers")
    return


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


def set_direct_wifi_connection():
    os.system("rfkill unblock all")
    os.system("ip link set wlan0 up")
    config_file = os.path.join(config.SPI_IMAGE_DIR, 'p2p_wpa_supplicant.conf')
    os.system(f"wpa_supplicant -iwlan0  -B -Dnl80211 -c{config_file}")
    # os.system("wpa_supplicant -iwlan0  -B -Dnl80211 -c/etc/wpa_supplicant/p2p_wpa_supplicant.conf")
    time.sleep(1)
    os.system(f"wpa_cli  set device_name sticky-pi-{device_id()}")
    os.system("wpa_cli p2p_find")

    harvester_mac = find_harvester()
    if not harvester_mac:
        logging.warning(f"Could not find a network with name `{config.SPI_HARVESTER_NAME_PATTERN}'")
    os.system(f"wpa_cli  p2p_prov_disc {harvester_mac}  pbc")
    os.system(f"wpa_cli  p2p_connect {harvester_mac} pbc persistent join")

    start = time.time()
    ip = None
    while time.time() - start < PING_HARVESTER_TIMEOUT:

        if not ip:
            if "p2p-wlan0-0" not in netifaces.interfaces():
                logging.info("Waiting for p2p-wlan0-0")
                time.sleep(0.5)
            else:
                # we kill dhcp client if we could not get an ip
                os.system("dhclient -x")
                os.system("dhclient p2p-wlan0-0 -nw")
                time.sleep(1)
                ip = get_ip_address('p2p-wlan0-0')
        else:
            go_ip = ".".join(ip.split(".")[0:3] + ["1"])
            resp = os.system(f"ping -c 1 -W 1 {go_ip} > /dev/null 2>&1")
            if resp == 0:
                logging.info("Host is up!")
                return True
    logging.warning("Cannot set ip or ping GO")
    return False


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

class ConfigHandler(dict):
    _type_dict = {
        "SPI_HARVESTER_NAME_PATTERN": str,
        "SPI_SYNC_TIMEOUT": int,
        "SPI_DEVICE_SERVER_PORT": int,
        "SPI_DEVICE_SERVER_PACEMAKER_FILE": str,
        'SPI_IMAGE_DIR': str
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
                      default=None, type=str)


    parser.add_option("-i", "--infinite",
                      dest="infinite",
                      help="Keep server running (dev)",
                      default=False, action='store_true')


    (options, args) = parser.parse_args()
    option_dict = vars(options)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    config = ConfigHandler()

    if not set_direct_wifi_connection():
        logging.warning("Could not connect to data harvester")
        exit(1)

    import uvicorn
    from zeroconf import IPVersion, ServiceInfo, Zeroconf

    ip_version = IPVersion.V4Only
    desc = {'path': '/'}
    ip = get_ip_address('p2p-wlan0-0')
    info = ServiceInfo(
        "_http._tcp.local.",
        f"StickyPi-{device_id()}._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=config.SPI_DEVICE_SERVER_PORT,
        properties=desc,
        server="ash-2.local.",
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
