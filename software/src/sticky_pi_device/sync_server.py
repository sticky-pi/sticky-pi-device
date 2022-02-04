import json
import re
import glob
import time
import os
import logging
from subprocess import Popen, PIPE

import fastapi
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sticky_pi_device.utils import device_id
from sticky_pi_device._version import __version__

MIN_AVAILABLE_DISK_SPACE = 10  # %


class Metadata(BaseModel):
    datetime: float
    lat: float
    lng: float
    alt: float


class ClearDiskInfo(BaseModel):
    dev_id: str


class ConfigHandler(dict):
    _type_dict = {
        "SPI_DRIVE_LABEL": str,
        "SPI_IMAGE_DIR": str,
        "SPI_LOG_FILENAME": str,
        "SPI_METADATA_FILENAME": str,
        "CURRENT_BATTERY_LEVEL": int,
        "SPI_VERSION": str
    }

    def __init__(self):
        self["SPI_VERSION"] = __version__,
        super().__init__()
        for k, t in self._type_dict.items():
            self[k] = t(os.environ[k])

    def __getattr__(self, attr):
        return self[attr]


config = ConfigHandler()
dev_id = device_id()
app = FastAPI()
img_dir = os.path.join(config.SPI_IMAGE_DIR, dev_id)

app.mount("/static", StaticFiles(directory=img_dir), name="static")


def remove_old_files():
    all_files = []
    # should not be any , but remove them if the exist
    temp_files = []

    for g in sorted(glob.glob(os.path.join(config.SPI_IMAGE_DIR, '**', '*.jpg*'))):
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


def img_file_hash(path):
    stats = os.stat(path)
    return str(stats.st_size)


def available_disk_space():
    label = config.SPI_DRIVE_LABEL
    command = "df %s --output=used,size | tail -1 | tr -s ' '" % config.SPI_IMAGE_DIR
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


def _status():
    out = {"device_id": dev_id,
           "datetime": time.time(),
           "version": config.SPI_VERSION,
           "battery_level": config.CURRENT_BATTERY_LEVEL,
           'available_disk_space': available_disk_space()}
    return out


@app.get("/status")
async def status():
    out = _status()
    return out


@app.post("/metadata")
async def metadata(meta_item: Metadata):
    meta = meta_item.dict()
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(meta["datetime"]))
    command = ["hwclock", "--set", "--date", time_str, "--utc", "--noadjfile"]
    p = Popen(command)
    exit_code = p.wait(5)
    if exit_code != 0:
        # fixme should be an error!
        logging.error(f"Cannot set localtime to {time_str}")

    path = os.path.join(config.SPI_IMAGE_DIR, config.SPI_METADATA_FILENAME)
    with open(path, 'w') as f:
        f.write(json.dumps(meta))

    return _status()


@app.post("/clear_disk")
async def clear_disk(info: ClearDiskInfo):
    if dev_id != info.dev_id:
        raise fastapi.HTTPException(400, "Wrong device id")

    if device_status['available_disk_space'] < MIN_AVAILABLE_DISK_SPACE:
        logging.warning("Removing old files")
        remove_old_files()


@app.get("/images")
async def images():
    out = {}
    # unsure if needed
    if not os.path.isdir(os.path.join(config.SPI_IMAGE_DIR, dev_id)):
        return out

    for g in glob.glob(os.path.join(config.SPI_IMAGE_DIR, dev_id, '*.jpg')):
        s = os.path.relpath(g, os.path.join(config.SPI_IMAGE_DIR, dev_id))
        datetime_field = s.split(".")[1]
        out[datetime_field] = img_file_hash(g)
    return out
