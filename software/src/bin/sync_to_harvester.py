#!/bin/python
import logging
from optparse import OptionParser
from datetime import datetime
import os
import json
from sticky_pi_device.utils import device_id
from sticky_pi_device.config_handler import ConfigHandler
from sticky_pi_device.data_syncer import DataSyncer, NoHostOrNetworkException


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--dummy-device",
                      dest="dummy_device",
                      help="Whether to create a dummy device, that does not need hardware and makes mock images",
                      default=False,
                      action='store_true')

    parser.add_option("-i", "--device-id",
                      dest="device_id",
                      help="The device unique id. On raspberry pi, infered from the CPU serial",
                      default=None)

    parser.add_option("-n", "--no-sync",
                      dest="no_sync",
                      help="Does not sync to data harvester",
                      default=False,
                      action='store_true')
    parser.add_option("-u", "--no-save",
                      dest="no_save",
                      help="Does does not save the picture",
                      default=False,
                      action='store_true')

    parser.add_option("-s", "--sync-only",
                      dest="sync_only",
                      help="Does not take any picture, just sync",
                      default=False,
                      action='store_true')

    parser.add_option("-v", "--verbose",
                      dest="verbose",
                      help="Show info",
                      default=False,
                      action='store_true')

    parser.add_option("-k", "--keep-alive",
                      dest="keep_alive",
                      help="Do not turn off after picture",
                      default=False,
                      action='store_true')


    (options, args) = parser.parse_args()
    option_dict = vars(options)

    config = ConfigHandler()

    if option_dict['dummy_device']:
        logging.warning("Using dummy camera (-d flag)")
        from sticky_pi_device.test.test_one_shooter import DummyOneShooter as PiOneShooter
        img_subdir = os.path.join(config.SPI_IMAGE_DIR, option_dict['device_id'])
    else:
        from sticky_pi_device.one_shooter import PiOneShooter
        assert option_dict['device_id'] is None, "Cannot set device ID on an actual device. This is reserved for dummy devices/development"
        img_subdir = os.path.join(config.SPI_IMAGE_DIR, device_id())

    metadata_file = os.path.join(config.SPI_IMAGE_DIR, config.SPI_METADATA_FILENAME)

    if not os.path.exists(metadata_file):
        init_metadata = {"lat": None,
                         "lng": None,
                         "alt": None}
        with open(metadata_file, 'w') as f:
            json.dump(init_metadata, f)

    one_shooter = PiOneShooter(config, dev_id=option_dict['device_id'])

    if not os.path.exists(img_subdir):
        os.makedirs(img_subdir)

    if option_dict["verbose"]:
       log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logfile = os.path.join(img_subdir, 'sticky_pi.log')
    logging.basicConfig(filename=logfile,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=log_level
                        )
    logging.warning('Logging at %s' % datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sync_to_harvester = not option_dict['no_sync']

    try:
        one_shooter.shoot(option_dict["no_save"])

    except Exception as e:
        logging.error(e, exc_info=True)
        raise e
    finally:
        try:
            if not option_dict["no_sync"]:
                ds = DataSyncer(config, logfile_path=logfile, dev_id=option_dict['device_id'])
                logging.info("Syncing")
                ds.sync()
        except NoHostOrNetworkException as e:
            logging.info(e)
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e
        finally:
            if not option_dict["keep_alive"]:
                one_shooter.power_off()