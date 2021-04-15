#!/bin/python
import logging
from datetime import datetime
import os
import json
from sticky_pi_device.utils import device_id
from sticky_pi_device.config_handler import ConfigHandler
from sticky_pi_device.one_shooter import PiOneShooter


if __name__ == '__main__':
    config = ConfigHandler()
    metadata_file = os.path.join(config.SPI_IMAGE_DIR, config.SPI_METADATA_FILENAME)

    if not os.path.exists(metadata_file):
        init_metadata = {"lat": 0,
                         "lng": 0,
                         "alt": 0}
        with open(metadata_file, 'w') as f:
            json.dump(init_metadata, f)

    one_shooter = PiOneShooter(config)
    img_subdir = os.path.join(config.SPI_IMAGE_DIR, device_id())
    if not os.path.exists(img_subdir):
        os.makedirs(img_subdir)
    logfile = os.path.join(img_subdir, 'sticky_pi.log')
    logging.basicConfig(filename=logfile)
    logging.warning('Logging at %s' % datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sync_to_harvester = False

    try:
        if sync_to_harvester:
            from subprocess import Popen
            logging.info('Spawning sync daemon')
            command = ['sync_to_harvester.py']
            p = Popen(command)
        one_shooter.shoot(close_camera_after=True)

    finally:
        if sync_to_harvester:
            logging.info('waiting for backup')
            p.wait(timeout=600)
        one_shooter.power_off()

