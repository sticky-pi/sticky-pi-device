set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')
SD=/dev/mmcblk0

grep 'Model.*Raspberry Pi' /proc/cpuinfo -c || (
  echo "Not booted in Raspberry pi"; exit 1
  )

echo "Making partition?"
(lsblk | grep $(basename ${SD})p3  -c) ||
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
mkfs.vfat ${SD}p3
sync
fatlabel  ${SD}p3 ${SPI_DRIVE_LABEL}
sync
echo "New partition labelled"
)

echo "Mounting partition?"

grep "^LABEL=${SPI_DRIVE_LABEL}" /etc/fstab -c || (
  echo "Adding new partition to fstab"
  echo "LABEL=${SPI_DRIVE_LABEL}  ${SPI_IMAGE_DIR}   vfat    defaults        0       0" > /etc/fstab &&
  mkdir -p ${SPI_IMAGE_DIR}  &&
  mount -a &&
  sync &&
  echo "Partition mounted"
)

echo "Setting dummy time"
hwclock --set --date "2000-01-01 00:00:00" --utc --noadjfile
hwclock --hctosys --utc --noadjfile

echo "Getting time from data harvester"
# todo here, try to sync time from harvester or from the internet?
cat something_that_fails ||(
echo "Failed. Getting time from public server"
cat another_fail || echo "Failed too. Check internet connection"
)


#/usr/bin/sync_to_harvester.py --no-save -k
# make the image read only if defined in env file

if [[ ${SPI_MAKE_READ_ONLY} == 1 ]]; then
  echo "Making read-only FS"
  (mount ${SD}p1 /boot
  cp /boot/cmdline.txt /boot/cmdline.txt-backup
  sed s/rw/ro/g /boot/cmdline.txt-backup > /boot/cmdline.txt

  cp /etc/fstab /etc/fstab-backup
  cat /etc/fstab-backup > /etc/fstab
  echo 'tmpfs   /var/log    tmpfs   nodev,nosuid    0   0' >> /etc/fstab
  echo 'tmpfs   /var/tmp    tmpfs   nodev,nosuid    0   0' >> /etc/fstab
  echo 'tmpfs   /tmp    tmpfs   nodev,nosuid    0   0' >> /etc/fstab
  echo 'resolv_conf="/tmp/resolv.conf"' > /etc/resolvconf.conf
  history -c -w) ||
  umount ${SD}p1
fi

