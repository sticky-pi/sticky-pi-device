set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')
SD=/dev/mmcblk0

grep 'Model.*Raspberry Pi' /proc/cpuinfo -c || (
  echo "Not booted in Raspberry pi"; exit 1
  )

echo "Making partition?"
(lsblk | grep ${SD}p3  -c) ||
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
fatlabel  ${SD}p3 ${SPI_DRIVE_LABEL}
echo "New partition labelled"
)

echo "Mounting partition?"

grep "^LABEL=${SPI_DRIVE_LABEL}" /etc/fstab -c || (
  echo "Adding new partition to fstab"
  echo "LABEL=${SPI_DRIVE_LABEL}  ${SPI_IMAGE_DIR}   vfat    defaults        0       0" > /etc/fstab &&
  mkdir -p ${SPI_IMAGE_DIR}  &&
  mount -a &&
  echo "Partition mounted"
)

echo "Disabling NTP time sync"
systemctl --now disable systemd-timesyncd.service

systemctl --now enable ${SPI_TARGET_SERVICE}
echo "Disabling  first boot script"
systemctl disable first_boot.service
echo "All good"
