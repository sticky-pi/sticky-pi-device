set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')
SD=/dev/mmcblk0
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
echo "LABEL=${SPI_DRIVE_LABEL}  /sticky_pi_images   vfat    defaults        0       0" > /dev/fstab
