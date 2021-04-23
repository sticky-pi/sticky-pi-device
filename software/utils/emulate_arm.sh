#!/usr/bin/env bash
export $(grep -v '^#' ./.env | xargs -d '\r\n')
cp base-$OS_IMG_NAME tmp-$OS_IMG_NAME
DEV="$(losetup --show -f -P "tmp-${OS_IMG_NAME}")"
mount ${DEV}p2 $MOUNT_DIR/root
mount ${DEV}p1 $MOUNT_DIR/root/boot
set -e
{
  rsync -rvP --copy-links ./os_stub/ ${MOUNT_DIR}/root/
  chmod 700 ${MOUNT_DIR}/root/opt/sticky_pi/utils/customize_os.sh
  systemd-nspawn  --timezone=off --directory ${MOUNT_DIR}/root/  /opt/sticky_pi/utils/customize_os.sh
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
mv tmp-$OS_IMG_NAME $OS_IMG_NAME