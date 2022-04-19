import json
import re
import glob
import time
import os
import logging
from subprocess import Popen, PIPE
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler


from sticky_pi_device.utils import device_id
from sticky_pi_device._version import __version__

MIN_AVAILABLE_DISK_SPACE = 10  # %


class ConfigHandler(dict):
    _type_dict = {
        "SPI_DRIVE_LABEL": str,
        "SPI_IMAGE_DIR": str,
        "SPI_LOG_FILENAME": str,
        "SPI_METADATA_FILENAME": str,
        "CURRENT_BATTERY_LEVEL": int,
        "FIRST_BOOT": int,
        "SPI_VERSION": str,
        "SPI_DEVICE_SERVER_PACEMAKER_FILE": str,
        "SPI_IS_MOCK_DEVICE": int
    }

    def __init__(self):
        self["SPI_VERSION"] = __version__,
        super().__init__()
        for k, t in self._type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]


def img_file_hash(path):
    stats = os.stat(path)
    return str(stats.st_size)



class S(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):

        self._config = ConfigHandler()

        if "MOCK_DEVICE_ID" in os.environ and os.environ["MOCK_DEVICE_ID"]:
            self._dev_id = os.environ["MOCK_DEVICE_ID"]
        else:
            self._dev_id = device_id()

        self._img_dir = os.path.join(self._config.SPI_IMAGE_DIR, self._dev_id)
        super(S, self).__init__(request, client_address, server)

    def _set_headers(self, resp=200, type="application/json"):
        self.send_response(resp)
        self.send_header("Content-type", type)
        self.end_headers()

    def _json(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = json.dumps(message)
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def _get_static_file(self, path):

        file = os.path.join(self._config.SPI_IMAGE_DIR, self._dev_id, path)
        if not os.path.exists(file):
            self._set_headers(400)
            self.wfile.write(self._json(f"No such file {path}"))
            return

        with open(file, 'rb') as f:
            file_data = f.read()

        self.send_response(200)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Disposition", "attachment")
        self.send_header("Content-Length", str(len(file_data)))
        self.send_header("Content-type", "image/jpeg")
        self.end_headers()
        self.wfile.write(file_data)

    def do_GET(self):
        if self.path.startswith("/static"):
            # todo, prevent getting ../../...
            # i.e. secure path
            path = os.path.relpath(self.path, "/static")
            return  self._get_static_file(path)

        self._get_methods = {"/status": "_status", "/images": "_images"}
        try:

            method = self._get_methods[self.path]
            resp = 200
            m = getattr(self, method)
            out = m()

        except Exception as e:
            logging.error(e)
            resp = 500
            out = None

        finally:
            self._set_headers(resp)
            self.wfile.write(self._json(out))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):

        self._post_methods = {
                "/metadata": "_metadata",
                    "/keep_alive":"_keep_alive",
                    "/stop":"_stop",
                    "/clear_disk":"_clear_disk",
                              }
        try:

            method = self._post_methods[self.path]

            m = getattr(self, method)

            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)
            logging.info(post_data)
            content = json.loads(post_data)
            logging.info(f"{self.path}: {content}")
            resp, out = m(content)

        except Exception as e:
            logging.error(e)
            resp = 500
            out = None

        finally:
            self._set_headers(resp)
            self.wfile.write(self._json(out))

    def _status(self):
        out = {"device_id": self._dev_id,
               "datetime": time.time(),
               "version": self._config.SPI_VERSION,
               "is_mock_device": self._config.SPI_IS_MOCK_DEVICE,
               "battery_level": self._config.CURRENT_BATTERY_LEVEL,
               "first_boot": bool(self._config.FIRST_BOOT),
               'available_disk_space': self._available_disk_space(),
               }
        return out

    def _images(self):
        out = {}
        if not os.path.isdir(os.path.join(self._config.SPI_IMAGE_DIR, self._dev_id)):
            return out

        for g in glob.glob(os.path.join(self._config.SPI_IMAGE_DIR, self._dev_id, '*.jpg')):
            s = os.path.relpath(g, os.path.join(self._config.SPI_IMAGE_DIR, self._dev_id))
            datetime_field = s.split(".")[1]
            out[datetime_field] = img_file_hash(g)
        return out

    def _keep_alive(self, info):
        if self._dev_id != info["device_id"]:
            return 400, "Wrong device id"

        with open(self._config.SPI_DEVICE_SERVER_PACEMAKER_FILE, 'w') as f:
            f.write("")
        return 200, ""

    def _metadata(self, meta):
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(meta["datetime"]))
        if self._config.SPI_IS_MOCK_DEVICE == 0:
            command = ["hwclock", "--set", "--date", time_str, "--utc", "--noadjfile"]
            p = Popen(command)
            exit_code = p.wait(5)
            if exit_code != 0:
                # fixme should be an error!
                logging.error(f"Cannot set localtime to {time_str}")
        else:
            logging.info("Mock device, not setting RTC")
        path = os.path.join(self._config.SPI_IMAGE_DIR, self._config.SPI_METADATA_FILENAME)
        with open(path, 'w') as f:
            f.write(json.dumps(meta))

        return 200, self._status()


    def _remove_old_files(self):
        all_files = []
        # should not be any , but remove them if the exist
        temp_files = []

        for g in sorted(glob.glob(os.path.join(self._config.SPI_IMAGE_DIR, '**', '*.jpg*'))):
            if g.endswith("~"):
                temp_files.append(g)
            elif g.endswith(".jpg"):
                all_files.append(g)

        # remove all but last temp files, in case
        for r in temp_files[0: -1]:
            os.remove(r)

        # remove half of the images
        for r in all_files[0: (len(all_files) // 2)]:
            os.remove(r)

    def _stop(self, info):
        if self._dev_id != info["device_id"]:
            return 400, "Wrong device id"
        if os.path.exists(self._config.SPI_DEVICE_SERVER_PACEMAKER_FILE):
            os.remove(self._config.SPI_DEVICE_SERVER_PACEMAKER_FILE)

        return 200, ""

    def _clear_disk(self, info):
        if self._dev_id != info["device_id"]:
            return 400, "Wrong device id"
        if self._config.SPI_IS_MOCK_DEVICE == 0:
            if self._status()['available_disk_space'] < MIN_AVAILABLE_DISK_SPACE:
                logging.warning("Removing old files")
                self._remove_old_files()
        else:
            logging.info("Not clearing disk on mock device")
        return 200, ""


    def _available_disk_space(self):
        label = self._config.SPI_DRIVE_LABEL
        command = "df %s --output=used,size | tail -1 | tr -s ' '" % self._config.SPI_IMAGE_DIR
        p = Popen(command, shell=True, stderr=PIPE, stdout=PIPE)
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



class CustomServer(Thread):
    def __init__(self, addr, port):
        super(CustomServer, self).__init__()
        server_address = (addr, port)
        self._httpd = HTTPServer(server_address, S)

    def run(self):
        self._httpd.serve_forever()

    def stop(self):
        self._httpd.shutdown()
