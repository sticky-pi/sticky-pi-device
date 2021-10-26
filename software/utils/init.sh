#!/bin/bash

mount -t proc proc /proc
mount -a
modprobe brcmfmac
modprobe brcmutil
modprobe ip_tables
modprobe x_tables
modprobe cfg80211
modprobe ipv6
modprobe snd-bcm2835
modprobe spi-bcm2835
modprobe i2c-dev
modprobe rtc-ds1307

export $(grep -v '^#' /etc/environment | xargs -d '\r\n')


# todo, here turn watchdog on ?

LOG_FILE = ${SPI_IMAGE_DIR}/${SPI_LOG_FILENAME}
FIRST_BOOT_LOG_FILE = ${SPI_IMAGE_DIR}/${SPI_FIRST_BOOT_LOG_FILENAME}

# turn on wifi interface
ip link set wlan0 up
# in the background, initiate wpa_supplicant. We are not waiting for success
wpa_supplicant -Dnl80211 -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant.conf &
# we will requests a dynamic IP from the router. also not waiting (-nw)
dhclient wlan0 -nw

# test if our logfile exists if not, it means we have not gone through the first boot
# during first boot, we log output on FIRST_BOOT_LOG_FILE
cat ${LOG_FILE} || (sh /opt/sticky_pi/utils/first_boot.sh  &>  FIRST_BOOT_LOG_FILE && touch LOG_FILE)

# our custom c program
take_picture


bash


#
# # sudo rsync -rvP  --copy-links ./os_stub/  /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/ && sudo rsync  -r /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/tmp/ /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/opt/tmp/  && sudo systemd-nspawn  --timezone=off --directory  /run/media/quentin/a33f80ed-ac88-44e8-a129-d5551a4a58a3/ bash -c 'cd /opt/tmp/sticky_pi/take_picture &&   ./build.sh'

