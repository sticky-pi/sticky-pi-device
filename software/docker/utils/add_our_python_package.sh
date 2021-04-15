#!/usr/bin/env bash
source .env
cp base-$OS_IMG_NAME tmp-$OS_IMG_NAME
DEV="$(losetup --show -f -P "tmp-${OS_IMG_NAME}")"
mount ${DEV}p2 $MOUNT_DIR/root
mount ${DEV}p1 $MOUNT_DIR/root/boot
set -e
{
  systemd-nspawn  --timezone=off --directory ${MOUNT_DIR}/root/  /os_stub/root/customize_os.sh
} ||
{
umount ${DEV}p1
umount ${DEV}p2
losetup -d $DEV
exit 1
}

umount ${DEV}p1
umount ${DEV}p2
losetup -d $DEV
mv tmp-$OS_IMG_NAME custom-$OS_IMG_NAME