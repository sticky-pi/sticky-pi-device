import json
import socket
import logging
import os
import time

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import socket
#
# BUS_NAME = 'org.bluez'
# ADAPTER_IFACE = 'org.bluez.Adapter1'
# ADAPTER_ROOT = '/org/bluez/hci'
# AGENT_IFACE = 'org.bluez.Agent1'
# AGNT_MNGR_IFACE = 'org.bluez.AgentManager1'
# AGENT_PATH = '/my/app/agent'
# AGNT_MNGR_PATH = '/org/bluez'
# CAPABILITY = 'KeyboardDisplay'
# DEVICE_IFACE = 'org.bluez.Device1'
#
#
# class Adapter(object):
#     def __init__(self, bus, idx=0):
#         self.path = f'{ADAPTER_ROOT}{idx}'
#         self.adapter_object = bus.get_object(BUS_NAME, self.path)
#         self.adapter_props = dbus.Interface(self.adapter_object,
#                                             dbus.PROPERTIES_IFACE)
#         self.adapter_props.Set(ADAPTER_IFACE,
#                                'DiscoverableTimeout', dbus.UInt32(0))
#         self.adapter_props.Set(ADAPTER_IFACE,
#                                'Discoverable', False)
#         self.adapter_props.Set(ADAPTER_IFACE,
#                                'PairableTimeout', dbus.UInt32(0))
#         self.adapter_props.Set(ADAPTER_IFACE,
#                                'Pairable', False)
#
#         # self.adapter_props.Set(ADAPTER_IFACE,
#         #                        'Scanning', True)
#
#
# class Agent(dbus.service.Object):
#     pass
#
# dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
#
# bus = dbus.SystemBus()
# agent = Agent(bus, AGENT_PATH)
#
# agnt_mngr = dbus.Interface(bus.get_object(BUS_NAME, AGNT_MNGR_PATH),
#                            AGNT_MNGR_IFACE)
# agnt_mngr.RegisterAgent(AGENT_PATH, CAPABILITY)
# agnt_mngr.RequestDefaultAgent(AGENT_PATH)
# adapter = Adapter(bus)
# mainloop = GLib.MainLoop()
#
# try:
#     mainloop.run()
# except KeyboardInterrupt:
#     agnt_mngr.UnregisterAgent(AGENT_PATH)
#     mainloop.quit()



server_addr = "B8:27:EB:19:98:2A"
hostPort = 3
backlog = 1
size = 1024

with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
    s.connect((server_addr, hostPort))
    payload={"action": 'metadata',
             "value": {"alt": 1,
                       "lng": 0.0,
                       "lat": 0.0,
                       "datetime": time.time()}}

    payload = json.dumps(payload).encode("ascii")

    s.sendall(payload)
    metadata = json.loads(s.recv(size))
    images = {}
    payload = json.dumps({"action":"images", "value": None}).encode("ascii")
    s.sendall(payload)
    while True:
        data = json.loads(s.recv(size))
        if data:
            data = {".".join([metadata["device_id"], k, "jpg"]) : v for k,v in data.items()}
            images.update(data)
        else:
            break

    print(metadata)
    print(images)

# s.listen(backlog)
# print("Listening...")
#
# try:
#     while True:
#         client, address = s.accept()
#         print("Accepted client")
#         data = client.recv(size)
#         if data:
#             print(data)
#             client.send(data)
# except:
#     print("Error: Closing socket")