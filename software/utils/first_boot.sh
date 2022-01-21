set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')
SD=/dev/mmcblk0

gpio -g mode ${SPI_FLASH_GPIO} out
#


blink(){
  while true
  do
    for i in $(seq $1)
    do
      gpio -g write ${SPI_FLASH_GPIO} 1
      sleep 0.05
      gpio -g write ${SPI_FLASH_GPIO} 0
      sleep 0.2
    done
    sleep 1
  done
}

# turn on wifi interface
rfkill unblock all
ip link set wlan0 up
# in the background, initiate wpa_supplicant. We are not waiting for success
wpa_supplicant -Dnl80211 -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant.conf -B
# we will requests a dynamic IP from the router. also not waiting (-nw)
dhclient wlan0 -nw



blink 1 &
BLINKER=$!

grep 'Model.*Raspberry Pi' /proc/cpuinfo -c || (
  echo "Not booted in Raspberry pi"; exit 1
  )

echo "Making partition?"
(lsblk | grep $(basename ${SD})p4  -c) ||
(
echo "Making new partition"
fdisk $SD << EOF
n
p
3


t
3
c
w
EOF

partprobe $SD
mkfs.vfat ${SD}p4
sync
fatlabel  ${SD}p4 ${SPI_DRIVE_LABEL}
sync
echo "New partition labelled"
)

kill ${BLINKER} >/dev/null 2>&1
blink 2 &
BLINKER=$!

echo "Mounting partition?"

grep "^LABEL=${SPI_DRIVE_LABEL}" /etc/fstab -c || (
  echo "Adding new partition to fstab"
  echo "LABEL=${SPI_DRIVE_LABEL}  ${SPI_IMAGE_DIR}   vfat    defaults        0       0" > /etc/fstab &&
  mkdir -p ${SPI_IMAGE_DIR}  &&
  mount -a &&
  sync &&
  echo "Partition mounted"
)

kill ${BLINKER} >/dev/null 2>&1
blink 3 &
BLINKER=$!

echo "Setting dummy time"
hwclock --set --date "2000-01-01 00:00:00" --utc --noadjfile
hwclock --hctosys --utc --noadjfile

#echo "Getting time from data harvester"
## todo here, try to sync time from harvester or from the internet?
#cat something_that_fails ||(
#echo "Failed. Getting time from public server"
#cat another_fail || echo "Failed too. Check internet connection"
#)


# /usr/bin/sync_to_harvester.py --no-save -k
# make the image read only if defined in env file

kill ${BLINKER} >/dev/null 2>&1
blink 4 &
BLINKER=$!

if [[ ${SPI_MAKE_READ_ONLY} == 1 ]]; then
  echo "Making read-only FS"
  (
  cp /etc/fstab /etc/fstab-backup
  cat /etc/fstab-backup > /etc/fstab


  echo 'tmpfs   /var/log    tmpfs   nodev,nosuid    0   0' >> /etc/fstab
  echo 'tmpfs   /var/tmp    tmpfs   nodev,nosuid    0   0' >> /etc/fstab
  echo 'tmpfs   /tmp    tmpfs   nodev,nosuid    0   0' >> /etc/fstab
  echo 'resolv_conf="/tmp/resolv.conf"' > /etc/resolvconf.conf
#  # to save bluetooth pairing in RW partition
#  mkdir /var/lib/ -p
#  mkdir ${SPI_IMAGE_DIR}/bluetooth
#  ln -s ${SPI_IMAGE_DIR}/bluetooth /var/lib/bluetooth

  mount ${SD}p1 /boot
  cp /boot/cmdline.txt /boot/cmdline.txt-backup
  sed s/rw/ro/g /boot/cmdline.txt-backup > /boot/cmdline.txt
  history -c -w) ||
  umount ${SD}p1
fi

