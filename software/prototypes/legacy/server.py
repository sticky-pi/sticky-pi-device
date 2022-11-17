import socket
# import pydbus
import dbus


bus = dbus.SystemBus()
proxy_object = bus.get_object("org.bluez","/")
manager = dbus.Interface(proxy_object, "org.freedesktop.DBus.ObjectManager")
objects = manager.GetManagedObjects()

adapter_addr = str(objects['/org/bluez/hci0']['org.bluez.Adapter1']["Address"])
print(adapter_addr)

port = 3  # Normal port for rfcomm?
buf_size = 1024

with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
    s.bind((adapter_addr, port))
    s.listen()
    conn, addr = s.accept()
    try:
        print("Connected by", addr)
        while True:
            data = conn.recv(buf_size)
            if not data:
                break
            conn.sendall(data)
    finally:
        conn.close()
