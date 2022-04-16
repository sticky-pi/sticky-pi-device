#!/bin/bash

mount -t proc proc /proc
mount -a
modprobe brcmfmac
modprobe brcmutil
# fixme possibly we need some of these just for transfer -> can be lazy-loaded
modprobe ip_tables
modprobe x_tables
modprobe cfg80211
modprobe ipv6
modprobe snd-bcm2835
modprobe i2c-bcm2835
modprobe i2c-dev
modprobe rtc-ds1307

export $(grep -v '^#' /etc/environment | xargs -d '\r\n')


LOG_FILE=${SPI_IMAGE_DIR}/${SPI_LOG_FILENAME}


# If logfile does not exist, we launch the first boot!
# To run a  new first boot, we can also delete this file
if [ ! -f "${LOG_FILE}" ]; then
    set -e
    echo "${LOG_FILE} does NOT exist. Performing first boot."
#    sh /opt/sticky_pi/utils/first_boot.sh &&
    sh /opt/sticky_pi/utils/first_boot.sh &&
    touch ${LOG_FILE} && sync &&
    # this restarts the system, at low level
    echo b > /proc/sysrq-trigger
else
  # we rotate the log file when it is to large

  if [[ $(wc -l <${LOG_FILE}) -ge 1000 ]]; then
    sed -i '1,500d' ${LOG_FILE}
    echo "Rotating log file" | tee -a ${LOG_FILE}
  fi

  # our custom c program
  take_picture | tee -a  ${LOG_FILE}
fi
bash
#
# # sudo rsync -rvP  --copy-links ./os_stub/  /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/ && sudo rsync  -r /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/tmp/ /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/opt/tmp/  && sudo systemd-nspawn  --timezone=off --directory  /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/ bash -c 'cd /opt/tmp/sticky_pi/take_picture &&   ./build.sh'

