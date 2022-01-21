#!/usr/bin/env bash
export $(grep -v '^#' ./.env | xargs -d '\r\n')

gunzip -c  base-$OS_IMG_NAME.gz > tmp-$OS_IMG_NAME
DEV="$(losetup --show -f -P "tmp-${OS_IMG_NAME}")"
#DEV="$(losetup --show -f -P test.img)"
mount ${DEV}p2 ${MOUNT_DIR}/root
mount ${DEV}p1 ${MOUNT_DIR}/root/boot
set -e
{
  rsync -rvP --copy-links ./os_stub/ ${MOUNT_DIR}/root/
  chmod 700 ${MOUNT_DIR}/root/opt/sticky_pi/utils/customize_os.sh
  systemd-nspawn  --timezone=off --directory ${MOUNT_DIR}/root/  /opt/sticky_pi/utils/customize_os.sh
  # this is in case package update overwrote our own configuration files
  rsync -rvP --copy-links ./os_stub/ ${MOUNT_DIR}/root/
} ||
{
echo "Failed. Cleaning up"
umount ${DEV}p1
umount ${DEV}p2
losetup -d $DEV
exit 1
}

umount ${DEV}p1
umount ${DEV}p2
losetup -d $DEV
mv tmp-$OS_IMG_NAME $CUSTOM_OS_IMG_NAME