import json
import time
import logging
import os
import re
import datetime
import shutil
from subprocess import Popen, PIPE, STDOUT
import sys
import glob
import serial
import optparse

LOCAL_IMAGE_PARTITION_LABEL = 'SPI_IMAGES'
SPI_DRIVE_LABEL = 'SPI_DRIVE'
LOCAL_IMAGE_DIR = '/sticky_pi_images/'
MOUNT_DIR = os.path.join('/mnt', SPI_DRIVE_LABEL)
MIN_AVAILABLE_DISK_SPACE = 10 #%

def rsync_monitor(source, target):

    if not target.endswith('/'):
        target = target + '/'

    proc = Popen(['/usr/bin/rsync', '-r', '-v', '-P', '--size-only', source, target, '--exclude', '*.json'], stdout=PIPE, stderr=STDOUT)
    # works in python 3.0+
    for line in proc.stdout:
        logging.debug(line)
        if b'rsync error' in line:
            logging.error(line)
        else:
            match = re.findall(b'\r.*to-chk=(?P<num>\d+)/(?P<den>\d+)', line)
            if match:
                num, den = match[0]
                progress_str = b'P %05d/%05d' %(int(den) - int(num), int(den))
                yield progress_str
    proc.wait()

def available_disk_space(label):
    command = "df $(blkid -o list | grep %s| cut -f 1 -d ' ') --output=used,avail | tail -1 | tr -s ' '" % label
    p = Popen(command,  shell=True, stderr=PIPE, stdout=PIPE)
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

def available_disk_space_instruction(avail):
        return b"A %0.1f" % round(avail, 2)


def remove_old_files(location):
    all_files = []
    for g in sorted(glob.glob(os.path.join(location, '**','*.jpg'))):
        all_files.append(g)

    # remove half of the images
    for r in all_files[0: (len(all_files) // 2)]:
        os.remove(r)

def cpu_serial():
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
                cpuserial_last_8bit = cpuserial[8:16]
                return cpuserial_last_8bit
def device_id():
    try:
        cpuserial = cpu_serial()
        if not cpuserial:
            raise Exception("Could not read serial number")

    except Exception as e:
        cpuserial = "00000000"
        logging.error(e)
    return b"I %s" % cpuserial.encode()



class SerialConnector(object):
    _metadata_filename = 'metadata.json'
    _baud = 9600

    def __init__(self, image_dir, port = None):
        if port is None:
            logging.debug("Scanning serial ports...")
            ports = self._serial_ports()
            if len(ports) == 0:
                raise Exception("No serial port found. "
                                "Ensure your device is plugged.")
            elif len(ports) > 2:
                logging.warning("%i serial ports found:\n %s" % (len(ports), "\n\t".join(ports)))
            port = ports[0]
            logging.info("Using %s " % port)

        self._serial_port = serial.Serial(port, self._baud, timeout=2)

        start = time.time()
        while time.time() - start < 5.0:
            line = self._serial_port.readline()
            if not line or line.startswith(b'#'):
                continue
            line = line.rstrip()
            if line == b"READY":
                self.send_status(b'BEGIN')
                logging.debug('Serial device ready sending "BEGIN"')
                break

        self._image_dir = image_dir

    def _serial_ports(self):
        """Lists serial ports, from:
        http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """


        ports = glob.glob('/dev/tty[A-Za-z]*')

        result = []
        for port in ports:
            basename = os.path.basename(port)
            logging.debug(basename)
            if basename.startswith('ttyUSB') or basename.startswith('ttyACM'):
                try:
                    s = serial.Serial(port)
                    s.close()
                    result.append(port)
                except (OSError, serial.SerialException):
                    pass
        return result


    def send_status(self, str, wait_after=0):
        logging.debug(str)
        self._serial_port.write(str + b'\n')
        time.sleep(wait_after)

    def get_metadata(self):
        # try five times. error if nothing still
        tries = 0
        while True:
            # we read a line from serial port and remove any `\r` and `\n` character
            line = self._serial_port.readline()
            logging.debug(line)
            if not line or line.startswith(b'#'):
                continue
            try:
                lat, lng, alt, datetime = line.rstrip().split(b';')

                # when no data is available for gps coordinates, we load gps data from past metadata file
                # unless this file does not exist yet
                if alt == -1000 and lng ==0 and lat==0:
                    path = os.path.join(self._image_dir, self._metadata_filename)
                    if os.path.isfile(path):
                        with open(path, 'r') as f:
                            data = json.load(f)
                            if 'lat' in data and  'lng' in data and 'alt' in data:
                                lat = data['lat']
                                lng = data['lng']
                                alt = data['alt']


                ref_time = self._set_clock(datetime)

                meta = {    'lng': float(lng),
                            'lat': float(lat),
                            'alt': float(alt),
                            'datetime': ref_time}

                self._save_metadata(meta)
                return

            except Exception as e:
                logging.error(e)
                if tries >= 5:
                    raise e
                tries = tries + 1
        

    def _save_metadata(self, metadata):

        path = os.path.join(self._image_dir, self._metadata_filename)
        out = json.dumps(metadata)
        with open(path, 'w') as f:
            f.write(out)

    def _set_clock(self, datetime_str):
        # datetime looks like 'YYYY-mm-dd HH-MM-SS UTC'
        ref_time = datetime.datetime.strptime(datetime_str.decode(), "%Y-%m-%dT%H:%M:%S%z")
        ref_datetime_str = ref_time.strftime('%Y-%m-%d %H:%M:%S')

        command = "/usr/bin/hwclock --set --date '%s' --utc --noadjfile" % ref_datetime_str
        logging.debug(command)
        p = Popen(command, shell=True, stderr=PIPE)
        c = p.wait(timeout=10)
        if c != 0:
            error = p.stderr.read()
            logging.error('Error setting the hardware clock. %i: %s' % (c, error))
        return ref_datetime_str


class DummySerialConnector(SerialConnector):

    def __init__(self, image_dir, port=None):
        self._image_dir = image_dir

    def send_status(self, str, wait_after = 0):
        logging.debug(str)

    def get_metadata(self):
        logging.debug("getting metadata")


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-D", "--debug", dest="debug", default=False, help="Set DEBUG mode ON", action="store_true")
    parser.add_option("-n", "--no-serial", dest="no_serial", default=False, help="Set DEBUG mode ON", action="store_true")

    (options, args) = parser.parse_args()
    option_dict = vars(options)

    if option_dict["debug"]:
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Logging using DEBUG SETTINGS")

    if option_dict["no_serial"]:
        logging.debug('Serial connection disabled, not expecting serial metadata')
        serial_connection = DummySerialConnector(LOCAL_IMAGE_DIR)
    else:
        serial_connection = SerialConnector(LOCAL_IMAGE_DIR)
    serial_connection.get_metadata()

    serial_connection.send_status(device_id(), wait_after=1)
    serial_connection.send_status(datetime.datetime.utcnow().strftime('T %Y-%m-%dT%H:%M:%SZ').encode(), wait_after=4)

    avail = available_disk_space(LOCAL_IMAGE_PARTITION_LABEL)
    if avail:
        serial_connection.send_status(available_disk_space_instruction(avail), wait_after=4)

        if avail < MIN_AVAILABLE_DISK_SPACE: # less than MIN_AVAILABLE_DISK_SPACE_ % => remove old files
            remove_old_files(LOCAL_IMAGE_DIR)
    else:
        logging.error('Failed to get available disk space')

    spi_drive_mounted = False

    if os.path.exists(os.path.join('/dev/disk/by-label', SPI_DRIVE_LABEL)):
        if not os.path.isdir(MOUNT_DIR):
            raise Exception('/mnt/%s  does not exist!' % SPI_DRIVE_LABEL)
        # mount by label
        p = Popen(['/usr/bin/mount', '-L', SPI_DRIVE_LABEL, MOUNT_DIR], stderr=PIPE)
        c = p.wait(timeout=20)
        if c != 0:
            error = p.stderr.read()
            logging.error('Failed to mount %s, error %i: %s' % (SPI_DRIVE_LABEL, c, error))
            if b'already mounted' in error:
                spi_drive_mounted = True
        else:
            spi_drive_mounted = True
    try:
        if spi_drive_mounted:
            logging.debug('Rsyncing')
            for p in rsync_monitor(LOCAL_IMAGE_DIR, MOUNT_DIR):
                serial_connection.send_status(p)

        else:
            serial_connection.send_status(b'P NO SPI_DRIVE')
        time.sleep(5)
    finally:
        if spi_drive_mounted:
            serial_connection.send_status(b'P UNMOUNTING')
            os.sync()
            p = Popen(['/usr/bin/umount', MOUNT_DIR])
            serial_connection.send_status(b'P DONE', wait_after=1)
            serial_connection.send_status(device_id())
