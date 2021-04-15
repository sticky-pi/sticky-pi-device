#!/usr/bin/env bash
export $(grep -v '^#' ./.env | xargs -d '\r\n')
cp custom-$OS_IMG_NAME tmp-$OS_IMG_NAME
DEV="$(losetup --show -f -P "tmp-${OS_IMG_NAME}")"
mount ${DEV}p2 $MOUNT_DIR/root
mount ${DEV}p1 $MOUNT_DIR/root/boot
set -e
{
  cp -rf sticky_pi_device-*.tar.gz $MOUNT_DIR/root/root/
  echo '#!/bin/bash' > $MOUNT_DIR/root/root/install_our_package.sh
  echo 'export $(grep -v "^\#" /etc/environment | xargs -d "\r\n")' >> $MOUNT_DIR/root/root/install_our_package.sh
  echo 'pip install /root/sticky_pi_device-*.tar.gz --no-cache-dir' >> $MOUNT_DIR/root/root/install_our_package.sh

#  echo 'TEST_ENV_VAR=hello-world' >> $MOUNT_DIR/root/etc/environment
#  echo '#!/bin/bash' > $MOUNT_DIR/root/root/install_our_package.sh
#  echo 'echo TEST: $TEST_ENV_VAR' >> $MOUNT_DIR/root/root/install_our_package.sh
  chmod 700 $MOUNT_DIR/root/root/install_our_package.sh

  systemd-nspawn  --timezone=off --directory ${MOUNT_DIR}/root/ /root/install_our_package.sh
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
mv tmp-$OS_IMG_NAME spi-$OS_IMG_NAME