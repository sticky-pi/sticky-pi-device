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
systemctl --now disable systemd-timesyncd.service
timedatectl set-time "2000-01-01 00:00:00"

/usr/bin/take_picture.py --no-save -k
systemctl enable ${SPI_TARGET_SERVICE}
echo "Disabling  first boot script"
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

  cp /etc/systemd/journald.conf /etc/systemd/journald.conf-backup
  cat /etc/systemd/journald.conf-backup > /etc/systemd/journald.conf
  echo Storage="none" >> /etc/systemd/journald.conf

  ##fixme TEST THIS
#  systemctl  disable systemd-logind.service
  systemctl mask systemd-logind.service systemd-random-seed systemd-user-sessions.service

  history -c -w) ||
  umount ${SD}p1
fi
systemctl disable first_boot.service  &&  echo "All good." && sync && reboot