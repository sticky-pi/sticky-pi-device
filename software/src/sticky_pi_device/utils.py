import tempfile
from subprocess import Popen, PIPE
import logging
import glob
import os
import time
import netifaces
import subprocess
import re



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

def mount_persistent_partition(label, taget):
    os.system(f"mount -L {label} {taget}")


def unmount_persistent_partition(path):
    os.system(f"umount {path}")



def set_wifi(interface="wlan0"):
    os.system("rfkill unblock all")
    os.system(f"ip link set {interface} up")

def set_wpa(wpa_timeout, persistent_dir, additional_config = None, dhc_only=False):

    if not dhc_only:
        sys_config_file = '/etc/wpa_supplicant/wpa_supplicant.conf'
        if additional_config is None:
            additional_config = os.path.join(persistent_dir, 'qr_wpa_supplicant.conf')

        logging.info(f"Restarting  wpa_supplicant.")
        os.system(f"pkill wpa_supplicant")

        if os.path.exists(additional_config):
            additional_config_cmd = f"-I{additional_config}"
        else:
            additional_config_cmd = ""

        time.sleep(5)

        os.system(f"wpa_supplicant -iwlan0  -B -Dnl80211 -c{sys_config_file} {additional_config_cmd}")
        time.sleep(3)
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


def set_wifi_from_qr(persistent_dir, img_file = None):
    # if img_file is set, we go for a non-persistent option.
    # we just use the provided image path to decode the qr code and try an ad hoc connection ONCE
    #  this connects to the harvester through a local only hotspot that is a temporary SSID/password

    import re
    import shutil

    try:
        logging.info(f"Looking for QR code to connect to wifi")
        decoded = subprocess.check_output(f"zbarimg --set x-density=2 --set y-density=2  {img_file} -q", shell=True, universal_newlines=True)

        m = re.match("QR-Code:WIFI:(?P<credentials>.*)", decoded)

        if not m:
            logging.warning(f"Could not read QR code in {img_file}")
            return ""

        creds = m.group('credentials')
        logging.info(f"Found qr code {creds}")
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

        if "F" in fields and int(fields["F"]) == 1:
            logging.info(f"Temporary local network: {fields['S']}")
            forget = True
        else:
            logging.info(f"Persistent network: {fields['S']}")
            forget = False

        config = tempfile.mktemp(suffix=".conf")
        os.system(f"pkill wpa_supplicant")
        os.system(f'echo "ctrl_interface=DIR=/var/run/wpa_supplicant" > {config}')
        os.system(f"wpa_passphrase {fields['S']} {fields['P']} >> {config}")
        os.system(f"wpa_supplicant -Dnl80211 -B -i wlan0 -c {config}")
        os.remove(config)
        time.sleep(2)

        if forget:
            ip = set_wpa(5, None, None, dhc_only=True)
            if not ip:
                logging.error("Trying direct connection though QR code, but failed! Not trying other methods")
                exit(1)
            return ip

        try:
            #we try to append credentials to our config AND to load it. we only keep it if we get an IP
            tmp_cfg_file = os.path.join(persistent_dir, 'qr_wpa_supplicant.conf.tmp')
            cfg_file = os.path.join(persistent_dir, 'qr_wpa_supplicant.conf')
            if not os.path.isfile(cfg_file):
                with open(cfg_file, 'w') as f:
                    f.write("ctrl_interface=DIR=/var/run/wpa_supplicant\n")

            shutil.copyfile(cfg_file, tmp_cfg_file)

            os.system(f"wpa_passphrase {fields['S']} {fields['P']} >> {tmp_cfg_file}")
            ip = set_wpa(5, persistent_dir, tmp_cfg_file)
            if ip:
                shutil.copyfile(tmp_cfg_file, cfg_file)
                return ip
        finally:
            os.remove(tmp_cfg_file)

        time.sleep(1)

    except AssertionError:
        logging.error(f"Assertion process error {e}")
        return ""
    except subprocess.CalledProcessError as e:
        logging.error(f"Sub process error {e}")
        return ""
