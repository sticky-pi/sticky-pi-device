import tempfile
from subprocess import Popen, PIPE
import logging
import glob
import os
import time
import netifaces
import subprocess
import re
import fcntl
import struct
import socket

def device_id():
    cpuserial = ""
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
                cpuserial_last_8bit = cpuserial[8:16]
                return cpuserial_last_8bit
    if not cpuserial:
        logging.warning("Could not read serial number setting to 00000000")
        cpuserial = "00000000"
    return cpuserial


def available_disk_space(label):
    command = "df $(blkid -o list | grep %s| cut -f 1 -d ' ') --output=used,avail | tail -1 | tr -s ' '" % label
    p = Popen(command, shell=True, stderr=PIPE, stdout=PIPE)
    c = p.wait(timeout=20)
    if c != 0:
        error = p.stderr.read()
        logging.error('Failed to display available space on disk labeled %s. %s' % (label, error))
    output = p.stdout.read()
    match = re.findall(b"(\d+) (\d+)", output)
    if match:
        num, den = match[0]
        avail = 100 - (100 * int(num)) / int(den)
        return avail


def remove_old_files(location):
    all_files = []
    for g in sorted(glob.glob(os.path.join(location, '**', '*.jpg'))):
        all_files.append(g)

    # remove half of the images
    for r in all_files[0: (len(all_files) // 2)]:
        os.remove(r)


def set_direct_wifi_connection(persistent_dir, default_content, ping_harvester_timeout, spi_harvester_name_pattern, find_harvseter_timeout, interface="wlan0"):
    config_file = os.path.join(persistent_dir, 'p2p_wpa_supplicant.conf')

    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            f.write(default_content)

    os.system(f"pkill wpa_supplicant")
    os.system(f"wpa_supplicant -i{interface}  -B -Dnl80211 -c{config_file}")
    # os.system("wpa_supplicant -iwlan0  -B -Dnl80211 -c/etc/wpa_supplicant/p2p_wpa_supplicant.conf")
    time.sleep(1)
    os.system(f"wpa_cli  set device_name sticky-pi-{device_id()}")
    os.system("wpa_cli p2p_find")

    harvester_mac = find_harvester(spi_harvester_name_pattern, find_harvseter_timeout)
    if not harvester_mac:
        logging.warning(f"Could not find a network with name `{spi_harvester_name_pattern}'")
    os.system(f"wpa_cli  p2p_prov_disc {harvester_mac}  pbc")

    wpa_cli_output = subprocess.check_output(f"wpa_cli  p2p_connect {harvester_mac} pbc persistent join", shell=True, universal_newlines=True)
    p2p_if_name = re.findall("'p2p.*'", wpa_cli_output)
    assert len(p2p_if_name) == 1
    p2p_if_name = eval(p2p_if_name[0])

    start = time.time()
    ip = None
    while time.time() - start < ping_harvester_timeout:

        if not ip:
            if f"{p2p_if_name}" not in netifaces.interfaces():
                logging.info(f"Waiting for {p2p_if_name}")
                time.sleep(0.5)
            else:
                # we kill dhcp client if we could not get an ip
                os.system("dhclient -x")
                os.system(f"dhclient {p2p_if_name} -nw")
                time.sleep(1)
                ip = get_ip_address(f'{p2p_if_name}')
        else:
            go_ip = ".".join(ip.split(".")[0:3] + ["1"])
            resp = os.system(f"ping -c 1 -W 1 {go_ip} > /dev/null 2>&1")
            if resp == 0:
                logging.info("Host is up!")
                return ip
    logging.warning("Cannot set ip or ping GO")
    return ""



def find_harvester(spi_harvester_name_pattern, find_harvester_timeout):
    start = time.time()
    while time.time() - start < find_harvester_timeout:
        try:
            peers = subprocess.check_output("wpa_cli p2p_peers", shell=True, universal_newlines=True)
        except subprocess.CalledProcessError:
            peers = []
            time.sleep(0.5)
            continue
        peers = peers.splitlines()
        logging.info(f"p2p peers: {peers}")
        for p in peers:
            device = subprocess.check_output(f"wpa_cli p2p_peer {p}", shell=True,
                                             universal_newlines=True).splitlines()
            if len(device) < 2:
                continue
            mac = device[1]
            for line in device:
                match = re.match(f"device_name={spi_harvester_name_pattern}", line)
                if match:
                    logging.info(f"Found {match.string}, mac={mac}")
                    return mac
    logging.warning(f"Did not find any matching network amongst {len(peers)} peers")
    return


def get_ip_address(ifname, version = "v4"):
    try:
        if version == "v6":
            addr = netifaces.ifaddresses(ifname)[netifaces.AF_INET6][0]['addr']
            addr = addr.split("%")[0]
        else:
            addr = netifaces.ifaddresses(ifname)[netifaces.AF_INET][0]['addr']

        return addr
    except KeyError:
        return
    #
    #
    # ifname = bytes(ifname, "ascii")
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # try:
    #     fd = fcntl.ioctl(
    #         s.fileno(),
    #         0x8915,  # SIOCGIFADDR
    #         struct.pack('256s', ifname[:15])
    #     )
    # except OSError as e:
    #     logging.error(e)
    #     return

def mount_persistent_partition(label, taget):
    os.system(f"mount {label} {taget}")


def unmount_persistent_partition(label):
    os.system(f"umount {label}")



def set_wifi(interface="wlan0"):
    os.system("rfkill unblock all")
    os.system(f"ip link set {interface} up")

def set_wpa(wpa_timeout, persistent_dir):
    sys_config_file = '/etc/wpa_supplicant/wpa_supplicant.conf'
    config_file = os.path.join(persistent_dir, 'wpa_supplicant.conf')

    if not os.path.exists(config_file):
        import shutil
        shutil.copyfile(sys_config_file, config_file)

    logging.info(f"Restarting  wpa_supplicant.")
    os.system(f"pkill wpa_supplicant")
    os.system(f"wpa_supplicant -iwlan0  -B -Dnl80211 -c{config_file}")
    time.sleep(2)
    logging.info(f"Restarting dhclient.")
    os.system("dhclient -x")
    logging.info(f"Getting ip address now.")
    os.system("dhclient wlan0 -nw")
    start = time.time()
    while time.time() - start < wpa_timeout:
        ip = get_ip_address('wlan0')
        if ip:
            logging.info(f"Connected to WPA router as {ip}")
            return ip
        time.sleep(.5)
    return ""


def set_wifi_from_qr(persistent_dir):
    import re
    import shutil
    # import RPi.GPIO as GPIO  # import RPi.GPIO module

    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(spi_flash_gpio, GPIO.OUT)  # set a port/pin as an output
    tmp_file = tempfile.mktemp(suffix=".jpg")
    try:
        for i in range(5):
            os.system(f"/opt/vc/bin/raspistill -o {tmp_file} -w 1296 -h 972 -vf -t 1")
            try:
                decoded = subprocess.check_output(f"zbarimg {tmp_file} -q", shell=True, universal_newlines=True)
            except subprocess.CalledProcessError:
                continue

            m = re.match("QR-Code:WIFI:(?P<credentials>.*)", decoded)

            if m:
                creds = m.group('credentials')
                fields = {}
                for c in creds.split(';'):
                    if c:
                        try:
                            key, val = c.split(":")
                            fields[key] = val
                        except ValueError:
                            pass
                assert "P" in fields, 'No password field, P in qr code text'
                assert "S" in fields, 'No ssid field, S in qr code text'
                config = tempfile.mktemp(suffix=".conf")

                os.system(f"pkill wpa_supplicant")
                os.system(f'echo "ctrl_interface=DIR=/var/run/wpa_supplicant" > {config}')
                os.system(f"wpa_passphrase {fields['S']} {fields['P']} >> {config}")
                os.system(f"wpa_supplicant -B -i wlan0 -c {config}")
                time.sleep(2)
                os.remove(config)

                os.system("dhclient -x")
                os.system("dhclient wlan0 -nw")
                for j in range(10):
                    ip = get_ip_address("wlan0")
                    if ip:
                        tmp_cfg_file = os.path.join(persistent_dir,'wpa_supplicant.conf.tmp')
                        cfg_file = os.path.join(persistent_dir, 'wpa_supplicant.conf')
                        shutil.copyfile(cfg_file, tmp_cfg_file)
                        os.system(f"wpa_passphrase {fields['S']} {fields['P']} >> {tmp_cfg_file}")
                        os.rename(tmp_cfg_file, cfg_file)
                        return ip
                    time.sleep(1)

        time.sleep(1)
    finally:
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)
