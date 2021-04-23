#!/bin/python
import logging
import os
from sticky_pi_device.config_handler import ConfigHandler
from sticky_pi_device.data_syncer import DataSyncer
from sticky_pi_device.utils import device_id
from datetime import datetime

if __name__ == '__main__':
    config = ConfigHandler()

    img_subdir = os.path.join(config.SPI_IMAGE_DIR, device_id())
    if not os.path.exists(img_subdir):
        os.makedirs(img_subdir)
    logfile = os.path.join(img_subdir, 'sticky_pi_data_sync.log')
    logging.basicConfig(filename=logfile)
    logging.warning('Logging at %s' % datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    try:
        ds = DataSyncer(config)
        ds.sync()
    except Exception as e:
        logging.error(e)
