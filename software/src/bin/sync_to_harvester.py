#!/bin/python
from optparse import OptionParser
from sticky_pi_device.data_syncer import DataSyncer

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-n", "--no-files",
                      dest="no_files",
                      help="Only connect for metadata. Do not upload any files.",
                      default=False,
                      action='store_true')


    parser.add_option("-p", "--periodic",
                      dest="periodic",
                      help="whether sync was automatically triggered",
                      default=False,
                      action='store_true')


    parser.add_option("-u", "--user-requested",
                      dest="user_requested",
                      help="whether the user explicitly requested sync -- as opposed to an automatic trigger",
                      default=False,
                      action='store_true')

    parser.add_option("-b", "--battery-level",
                      dest="battery_level",
                      help="The remaining battery percent",
                      default=None, type=int)


    (options, args) = parser.parse_args()
    option_dict = vars(options)

    ds = DataSyncer(**option_dict)
    ds.sync()
