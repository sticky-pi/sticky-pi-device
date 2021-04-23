#!/bin/python
import logging
from optparse import OptionParser
from datetime import datetime
import os
import json
from sticky_pi_device.utils import device_id
from sticky_pi_device.config_handler import ConfigHandler


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--dummy-device",
                      dest="dummy_device",
                      help="Whether to create a dummy device, that does not need hardware and makes mock images",
                      default=False,
                      action='store_true')

    parser.add_option("-n", "--no-sync",
                      dest="no_sync",
                      help="Does not sync to data harvester",
                      default=False,
                      action='store_true')


    (options, args) = parser.parse_args()
    option_dict = vars(options)

    if option_dict['dummy_device']:
        logging.warning("Using dummy camera (-d flag)")
        from sticky_pi_device.test.test_one_shooter import DummyOneShooter as PiOneShooter
    else:
        from sticky_pi_device.one_shooter import PiOneShooter

    config = ConfigHandler()
    metadata_file = os.path.join(config.SPI_IMAGE_DIR, config.SPI_METADATA_FILENAME)

    if not os.path.exists(metadata_file):
        init_metadata = {"lat": None,
                         "lng": None,
                         "alt": None}
        with open(metadata_file, 'w') as f:
            json.dump(init_metadata, f)

    one_shooter = PiOneShooter(config)
    img_subdir = os.path.join(config.SPI_IMAGE_DIR, device_id())
    if not os.path.exists(img_subdir):
        os.makedirs(img_subdir)
    logfile = os.path.join(img_subdir, 'sticky_pi.log')
    logging.basicConfig(filename=logfile,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        #    level=logging.INFO
                        )
    logging.warning('Logging at %s' % datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sync_to_harvester = not option_dict['no_sync']

    try:
        if sync_to_harvester:
            from subprocess import Popen
            logging.info('Spawning sync daemon')
            command = ['sync_to_harvester.py']
            p = Popen(command)
        one_shooter.shoot(close_camera_after=True)
    except Exception as e:
        logging.error(e)
        raise e
    finally:
        if sync_to_harvester:
            logging.info('waiting for backup')
            p.wait(timeout=600)
        one_shooter.power_off()

