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

def set_wpa(wpa_timeout, persistent_dir, additional_configs = None, dhc_only=False):

    if not dhc_only:
        logging.info(f"Restarting  wpa_supplicant.")
        os.system(f"pkill wpa_supplicant")

        sys_config_file = '/etc/wpa_supplicant/wpa_supplicant.conf'

        if additional_configs is None:
            additional_configs = [f for f in sorted(glob.glob(os.path.join(persistent_dir, '*.conf')))]



        additional_config_cmd = ""
        concatenated_config = tempfile.mktemp(suffix=".conf")
        with open(concatenated_config, "w") as conf_file:
            conf_file.write("ctrl_interface=DIR=/var/run/wpa_supplicant\n")
            for conf in additional_configs:
                if not os.path.exists(conf):
                    logging.warning(f"no such file {conf}")
                    continue
                with open(conf, "r") as f:
                    for line in f:
                        if not line.startswith("ctrl_interface"):
                            conf_file.write(line)

        additional_config_cmd += f" -I{concatenated_config}"
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


# def is_ssid_in_wpa_conf(ssid, conf_file):
#     all_ssids = set()
#     try:
#         with open(conf_file, "r") as f:
#             for s in f:
#                 # print(s)
#                 m = re.match('\s*ssid="(.*)"$', s)
#                 if m:
#                     if len(m.groups()) == 1:
#                         all_ssids.add(m.groups()[0])
#     except Exception as e:
#         logging.error(e)
#
#     return ssid in all_ssids



def set_wifi_from_qr(persistent_dir, img_file = None):
    # if img_file is set, we go for a non-persistent option.
    # we just use the provided image path to decode the qr code and try an ad hoc connection ONCE
    #  this connects to the harvester through a local only hotspot that is a temporary SSID/password

    import re
    import shutil

    try:
        if not img_file:
            img_file = tempfile.mktemp(suffix=".jpg")
            im_w, im_h = 4056/2, 3040/2

            command = f"/opt/vc/bin/raspistill -t 1000 -h {im_h} -w  {im_w} --quality 100  --sharpness -50 " \
                      f"--contrast 75 --saturation -100  --roi \"0.1, 0.1, 0.8, 0.8\" -o {img_file} "
            os.system(command)

        logging.info(f"Looking for QR code to connect to wifi")
        decoded = subprocess.check_output(f"zbarimg  --set *.disable --set qrcode.enable  --set x-density=2 --set y-density=2  {img_file} -q", shell=True, universal_newlines=True)

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
            logging.info(f"Pairing with temporary network: {fields['S']}")
            return ip

        tmp_cfg_file = os.path.join(persistent_dir, f'{fields["S"]}.conf.tmp')
        cfg_file = os.path.join(persistent_dir, f'{fields["S"]}.conf')
        try:
            os.system(f"wpa_passphrase {fields['S']} {fields['P']} > {tmp_cfg_file}")

            ip = set_wpa(5, persistent_dir, [tmp_cfg_file])
            if ip:
                logging.info(f"Pairing with new network: {fields['S']}")
                shutil.move(tmp_cfg_file, cfg_file)

                return ip
        finally:
            if os.path.exists(tmp_cfg_file):
                os.remove(tmp_cfg_file)
        time.sleep(1)

    except AssertionError as e:
        logging.error(f"Assertion process error {e}")
        return ""
    except subprocess.CalledProcessError as e:
        logging.error(f"Sub process error {e}")
        return ""
