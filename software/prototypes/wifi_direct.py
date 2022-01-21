import subprocess
import os
import time
import re
import logging
import socket
import fcntl
import struct

from sticky_pi_device.utils import device_id

FIND_HARVESTER_TIMEOUT = 10  # s
PING_HARVESTER_TIMEOUT = 10  # s
HARVESTER_NAME_PATTERN = "spi-harvester"
SPI_DEVICE_SERVER_PORT = 80


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
            device = subprocess.check_output(f"wpa_cli p2p_peer {p}", shell=True, universal_newlines=True).splitlines()
            if len(device) < 2:
                continue
            mac = device[1]
            for line in device:
                match = re.match(f"device_name={HARVESTER_NAME_PATTERN}", line)
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
    os.system("wpa_supplicant -iwlan0  -B -Dnl80211 -c/etc/wpa_supplicant/wpa_supplicant.conf")
    time.sleep(1)
    os.system(f"wpa_cli  set device_name sticky-pi-{device_id()}")
    os.system("wpa_cli p2p_find")

    harvester_mac = find_harvester()
    if not harvester_mac:
        logging.warning(f"Could not find a network with name `{HARVESTER_NAME_PATTERN}'")
    os.system(f"wpa_cli  p2p_prov_disc {harvester_mac}  pbc")
    os.system(f"wpa_cli  p2p_connect {harvester_mac} pbc persistent join")

    start = time.time()
    while time.time() - start < PING_HARVESTER_TIMEOUT:
        os.system("dhclient p2p-wlan0-0 -nw")

        ip = get_ip_address('p2p-wlan0-0')
        if ip:
            go_ip = ".".join(ip.split(".")[0:3] + ["1"])
            resp = os.system(f"ping -c 1 -W 0.2 {go_ip} > /dev/null 2>&1")
            if resp == 0:
                logging.info("Host is up!")
                return True
        time.sleep(0.5)
    logging.warning("Cannot set ip or ping GO")
    return False


if __name__ == "__main__":
    if set_direct_wifi_connection():
        import uvicorn
        from zeroconf import IPVersion, ServiceInfo, Zeroconf

        ip_version = IPVersion.V4Only
        desc = {'path': '/'}
        ip = get_ip_address('p2p-wlan0-0')
        info = ServiceInfo(
            "_http._tcp.local.",
            f"StickyPi-{device_id()}._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=SPI_DEVICE_SERVER_PORT,
            properties=desc,
            server="ash-2.local.",
        )

        zeroconf = Zeroconf(ip_version=ip_version)
        zeroconf.register_service(info)
        os.environ['CURRENT_BATTERY_LEVEL'] = "100"

        try:
            uvicorn.run("sync_server:app", host="0.0.0.0", port=SPI_DEVICE_SERVER_PORT)
        finally:
            zeroconf.unregister_service(info)
            zeroconf.close()
