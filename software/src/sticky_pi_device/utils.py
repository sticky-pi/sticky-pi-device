import re
from subprocess import Popen, PIPE
import logging
import glob
import os


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
