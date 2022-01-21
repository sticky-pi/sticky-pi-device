"""
pi = server
on server side:
create agent/server
wait for connections
accept all pairing
handle requests:
    For status file (/tmp/status)
    Index file (/tmp/index)

allow for file download

"""


from gi.repository import GLib
import pydbus
import dbus

BUS_NAME = 'org.bluez.obex'
PATH = '/org/bluez/obex'
AGENT_MANAGER_INTERFACE = 'org.bluez.obex.AgentManager1'
AGENT_INTERFACE = 'org.bluez.obex.Agent1'
SESSION_INTERFACE = 'org.bluez.obex.Session1'
TRANSFER_INTERFACE = 'org.bluez.obex.Transfer1'

# ses_bus = pydbus.SessionBus()
ses_bus = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

def transfer_status_handler(iface, props_changed, props_removed):
    if iface == TRANSFER_INTERFACE:
        status = props_changed.get('Status')
        if status == 'complete':
            print('Transfer complete')
        elif status == 'queued':
            print('Still queued')
        elif status == 'active':
            print('transferring')
        elif status == 'suspended':
            print('Suspended')
        elif status == 'error':
            print('error')

def iface_added_handler(dbus_path, interfaces):
    if SESSION_INTERFACE in interfaces and 'server' in dbus_path:
        print('Server session added')
    elif TRANSFER_INTERFACE in interfaces and 'server' in dbus_path:
        print('Transfer started')
        transfer = ses_bus.get(BUS_NAME, dbus_path)
        transfer.onPropertiesChanged = transfer_status_handler


class Agent:
    def AuthorizePush(self, path):
            raise pybus.DBusException(
                "org.bluez.obex.Error.Rejected: "
                "Not Authorized")

    def Cancel(self):
        print('Authorization Cancelled')

    def Release(self):
        pass


if __name__ == '__main__':
    obex_mngr = ses_bus.get('org.bluez.obex', '/')
    obex_mngr.onInterfacesAdded = iface_added_handler
    mainloop = GLib.MainLoop()
    ses_bus.register_object('/test/agent', Agent(), None)
    print('Agent created')
    agnt_mngr = ses_bus.get(BUS_NAME, PATH)
    agnt_mngr.RegisterAgent('/test/agent')
    print('Agent registered')
    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()
#
# import gi
# from gi.repository import GLib
#
# import sys
# import dbus
# import dbus.service
# import dbus.mainloop.glib
#
# BUS_NAME = 'org.bluez.obex'
# PATH = '/org/bluez/obex'
# AGENT_MANAGER_INTERFACE = 'org.bluez.obex.AgentManager1'
# AGENT_INTERFACE = 'org.bluez.obex.Agent1'
# TRANSFER_INTERFACE = 'org.bluez.obex.Transfer1'
#
#
# def ask(prompt):
#     try:
#         return raw_input(prompt)
#     except:
#         return input(prompt)
#
#
# class Agent(dbus.service.Object):
#     def __init__(self, conn=None, obj_path=None):
#         dbus.service.Object.__init__(self, conn, obj_path)
#         self.pending_auth = False
#
#     @dbus.service.method(AGENT_INTERFACE, in_signature="o",
#                          out_signature="s")
#     def AuthorizePush(self, path):
#             raise dbus.DBusException(
#                 "org.bluez.obex.Error.Rejected: "
#                 "Not Authorized")
#
#     @dbus.service.method(AGENT_INTERFACE, in_signature="",
#                          out_signature="")
#     def Cancel(self):
#         print("Authorization Canceled")
#         self.pending_auth = False
#
#
# if __name__ == '__main__':
#     dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
#
#     bus = dbus.SessionBus()
#     manager = dbus.Interface(bus.get_object(BUS_NAME, PATH),
#                              AGENT_MANAGER_INTERFACE)
#
#     path = "/test/agent"
#     agent = Agent(bus, path)
#
#     mainloop = GLib.MainLoop()
#
#     # manager.RegisterAgent(path)
#     # print("Agent registered")
#
#     cont = True
#     while cont:
#         try:
#             mainloop.run()
#         except KeyboardInterrupt:
#             if agent.pending_auth:
#                 agent.Cancel()
#             # elif len(transfers) > 0:
#             #     for a in transfers:
#             #         a.cancel()
#             else:
#                 cont = False
