#!/usr/bin/env bash
set -e
export $(grep -v '^#' ./.env | xargs -d '\r\n')
wget $ALARM_URL  -nc
dd bs=1M count=5000 if=/dev/zero of=tmp-$OS_IMG_NAME
DEV="$(losetup --show -f -P "tmp-$OS_IMG_NAME")"

fdisk $DEV << EOF
n
p
1

+100M
t
c
n
p
2

+3G
w
EOF

mkfs.vfat ${DEV}p1
mkfs.ext4 ${DEV}p2

mkdir -p $MOUNT_DIR/boot
mkdir -p $MOUNT_DIR/root

mount ${DEV}p2 $MOUNT_DIR/root
mount ${DEV}p1 $MOUNT_DIR/boot

bsdtar -xpf $ZIP_IMG -C $MOUNT_DIR/root
sync

mv $MOUNT_DIR/root/boot/* $MOUNT_DIR/boot/
umount ${DEV}p1

mount ${DEV}p1 $MOUNT_DIR/root/boot
cp $(which qemu-arm-static) ${MOUNT_DIR}/root/usr/bin

#cp  utils/customize_os.sh ${MOUNT_DIR}/root/root/ -v
#cp  .env ${MOUNT_DIR}/root/ -v

# fixme this seems to be the point of --bind-root=/etc/resolv.conf
# as in `systemd-nspawn -D /mnt/sdcard -M myARMMachine --bind-root=/etc/resolv.conf`
# from https://wiki.archlinux.org/index.php/QEMU#Starting_QEMU_virtual_machines_on_boot
rm ${MOUNT_DIR}/root/etc/resolv.conf
cat /etc/resolv.conf > ${MOUNT_DIR}/root/etc/resolv.conf
umount ${DEV}p1
umount ${DEV}p2
losetup -d $DEV
mv tmp-$OS_IMG_NAME base-$OS_IMG_NAME
