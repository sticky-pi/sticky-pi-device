import logging
import os
import glob
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import socket
from threading import Thread
import json
import re
from subprocess import Popen, PIPE
from optparse import OptionParser
import time

from sticky_pi_device.utils import device_id
from sticky_pi_device._version import __version__

#todo /var/lib/bluetooth should be symlinked to a rw partition so we remember pairing data ?

BUS_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
ADAPTER_ROOT = '/org/bluez/hci'
AGENT_IFACE = 'org.bluez.Agent1'
AGNT_MNGR_IFACE = 'org.bluez.AgentManager1'
AGENT_PATH = '/my/app/agent'
AGNT_MNGR_PATH = '/org/bluez'
CAPABILITY = 'KeyboardDisplay'
DEVICE_IFACE = 'org.bluez.Device1'
OBEX_BLUETOOTH_CHANNEL = 8


def init_bluetooth(config):
    os.system("rfkill unblock all")
    os.system("modprobe hci_uart")
    # a small rw  partition to save pairing data
    os.system("mount /dev/mmcblk0p3 /var/lib")
    os.makedirs("/run/dbus", exist_ok=True)
    os.system("dbus-launch --config-file=/usr/share/dbus-1/system.conf")
    os.system("/usr/lib/bluetooth/bluetoothd &")
    time.sleep(1)
    os.system("bluetoothctl power on")

def set_trusted(path):
    props = dbus.Interface(bus.get_object(BUS_NAME, path), dbus.PROPERTIES_IFACE)
    props.Set(DEVICE_IFACE, "Trusted", True)


class Agent(dbus.service.Object):
    @dbus.service.method(AGENT_IFACE,
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method(AGENT_IFACE,
                         in_signature='o', out_signature='s')
    def RequestPinCode(self, device):
        print(f'RequestPinCode {device}')
        return '0000'

    @dbus.service.method(AGENT_IFACE,
                         in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        set_trusted(device)
        return

    @dbus.service.method(AGENT_IFACE,
                         in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        auth = input("Authorize? (yes/no): ")
        if (auth == "yes"):
            return
        raise Rejected("Pairing rejected")

    @dbus.service.method(AGENT_IFACE,
                         in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = input("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_IFACE,
                         in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" %
              (device, passkey, entered))

    @dbus.service.method(AGENT_IFACE,
                         in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))


class Adapter(object):
    def __init__(self, bus, idx=0):
        self.path = f'{ADAPTER_ROOT}{idx}'
        self.adapter_object = bus.get_object(BUS_NAME, self.path)
        self.adapter_props = dbus.Interface(self.adapter_object,
                                            dbus.PROPERTIES_IFACE)
        self.adapter_props.Set(ADAPTER_IFACE,
                               'DiscoverableTimeout', dbus.UInt32(0))
        self.adapter_props.Set(ADAPTER_IFACE,
                               'Discoverable', True)
        self.adapter_props.Set(ADAPTER_IFACE,
                               'PairableTimeout', dbus.UInt32(0))
        self.adapter_props.Set(ADAPTER_IFACE,
                               'Pairable', True)

        self.adapter_props.Set(ADAPTER_IFACE,
                               'Alias', dbus.String(f"Sticky Pi {device_id()}"))


class ConfigHandler(dict):
    _type_dict = {
        "SPI_DRIVE_LABEL": str,
        "SPI_IMAGE_DIR": str,
        "SPI_LOG_FILENAME": str,
        "SPI_METADATA_FILENAME": str,
    }

    def __init__(self):
        self["SPI_VERSION"] = __version__,
        super().__init__()
        for k, t in self._type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]



class SocketServer(Thread):
    _port = 3  # Normal port for rfcomm?
    _buf_size = 1024
    _encoding = "ascii"
    _metadata_fields = {"datetime", "alt", "lat", "lng"}
    _timeout = 300
    _image_info_length = 4 # when listing images, we list N by N

    def __init__(self, bus, config, battery_level):
        proxy_object = bus.get_object("org.bluez", "/")
        manager = dbus.Interface(proxy_object, "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        self._adapter_addr = str(objects['/org/bluez/hci0']['org.bluez.Adapter1']["Address"])
        self._config = config
        self._battery_level = battery_level
        self._device_id = device_id()
        self._available_disk = self._available_disk_space()

        self._action_map = {"metadata": lambda x: self._metadata(x),
                            "images": lambda x: self._images(x)}

        super().__init__()

    def _metadata(self, value):
        metadata = value
        if not isinstance(metadata, dict):
            raise TypeError(f"Expected a dictionary of metadata, got {metadata}")
        if self._metadata_fields !=  set(metadata.keys()):
            raise TypeError(f"metadata has unexpected or missing fields: {set(metadata.keys())} != {self._metadata_fields}")

        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(metadata["datetime"]))
        command = ["hwclock", "--set", "--date", time_str, "--utc", "--noadjfile"]
        p = Popen(command)
        exit_code = p.wait(5)
        if exit_code != 0:
            # fixme should be an error!
            logging.error(f"Cannot set localtime to {time_str}")

        path = os.path.join(self._config.SPI_IMAGE_DIR, self._config.SPI_METADATA_FILENAME)
        with open(path, 'w') as f:
            f.write(json.dumps(metadata))

        out = {   "device_id": self._device_id,
                   "version": self._config.SPI_VERSION,
                  "battery_level": self._battery_level,
                  'available_disk_space': self._available_disk}

        yield out

    def _available_disk_space(self):

        label = self._config.SPI_DRIVE_LABEL
        # command = "df $(blkid -o list | grep %s| cut -f 1 -d ' ') --output=used,size | tail -1 | tr -s ' '" % label
        command = "df %s --output=used,size | tail -1 | tr -s ' '" % self._config.SPI_IMAGE_DIR
        p = Popen(command,  shell=True, stderr=PIPE, stdout=PIPE)
        c = p.wait(timeout=10)
        if c != 0:
            error = p.stderr.read()
            logging.error('Failed to display available space on disk labeled %s. %s' % (label, error))
        output = p.stdout.read()
        match = re.findall(b"(\d+) (\d+)", output)
        if match:
            num, den = match[0]
            avail = 100 - (100 * int(num)) / int(den)
            return round(avail, 2)
        else:
            raise Exception("Cannot assess space left on device")

    def _img_file_hash(self, path):
        stats = os.stat(path)
        return str(stats.st_size)

    def _images(self, value):
        to_yield = {}
        for g in glob.glob(os.path.join(self._config.SPI_IMAGE_DIR, '**', '*.jpg*')):
            out = os.path.relpath(g, os.path.join(self._config.SPI_IMAGE_DIR, self._device_id))
            datetime_field = out.split(".")[1]
            to_yield[datetime_field] = self._img_file_hash(g)
            if len(to_yield) == self._image_info_length:
                print(f"yielding {to_yield}")
                yield to_yield
                to_yield = {}
        print(f"yielding {to_yield}")
        yield to_yield
        yield None

    def run(self):
        start = time.time()
        while time.time() - start < self._timeout:
            try:
                with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
                    s.bind((self._adapter_addr, self._port))
                    s.listen()
                    conn, addr = s.accept()
                    try:
                        print("Connected by", addr)
                        while True:
                            data = conn.recv(self._buf_size)
                            if not data:
                                break
                            for response in self._request(data):
                                response = json.dumps(response).encode(self._encoding)
                                conn.sendall(response)
                    finally:
                        conn.close()
            except Exception as e:
                logging.error(e)

    def _request(self, data):
        #"{action: , value:}"
        print(f"received data: {data}")
        data = data.decode(self._encoding)
        data = json.loads(data)
        if not isinstance(data, dict):
            raise TypeError(f"Expected a json dictionary, got {data}")
        if "action" not in data:
            raise TypeError(f"Data has no 'action' field {data}")
        if "value" not in data:
            raise TypeError(f"Data has no 'value' field {data}")
        action = data["action"]
        value = data["value"]
        if action not in  self._action_map:
            raise TypeError(f"Unknown action: {action}. Allowed actions are {self._action_map.keys()}")
        return self._action_map[action](value)



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-b", "--battery-level",
                      dest="battery_level",
                      help="The remaining battery percent",
                      default=None, type=int)
    (options, args) = parser.parse_args()
    option_dict = vars(options)

    config = ConfigHandler()
    battery_level = option_dict["battery_level"]
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    init_bluetooth(config)
    bus = dbus.SystemBus()
    agent = Agent(bus, AGENT_PATH)
    socket_server = SocketServer(bus,config, battery_level)
    agnt_mngr = dbus.Interface(bus.get_object(BUS_NAME, AGNT_MNGR_PATH),
                               AGNT_MNGR_IFACE)
    agnt_mngr.RegisterAgent(AGENT_PATH, CAPABILITY)
    agnt_mngr.RequestDefaultAgent(AGENT_PATH)
    adapter = Adapter(bus)

    socket_server.start()

    os.system(f"obex-server-tool -b -c {OBEX_BLUETOOTH_CHANNEL} -r {os.path.join(config.SPI_IMAGE_DIR, device_id())} -o 1024 &")

    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        agnt_mngr.UnregisterAgent(AGENT_PATH)
        mainloop.quit()
