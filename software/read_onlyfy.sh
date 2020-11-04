#TARGET=2020-03-27_sticky_pi_rpi.img
MOUNT_DIR=/mnt/sticky_pi_root
OS_IMG_NAME=${TARGET%.*}-RO.img

cp $TARGET $OS_IMG_NAME


DEV="$(losetup --show -f -P "$OS_IMG_NAME")"

mkdir -p $MOUNT_DIR/root
mount ${DEV}p2 $MOUNT_DIR/root
mount ${DEV}p1 $MOUNT_DIR/root/boot


cp $MOUNT_DIR/root/boot/cmdline.txt $MOUNT_DIR/root/boot/cmdline.txt-backup
sed s/rw/ro/g $MOUNT_DIR/root/boot/cmdline.txt-backup > $MOUNT_DIR/root/boot/cmdline.txt

cp $MOUNT_DIR/root/etc/fstab $MOUNT_DIR/root/etc/fstab-backup
cat $MOUNT_DIR/root/etc/fstab-backup > $MOUNT_DIR/root/etc/fstab
echo 'tmpfs   /var/log    tmpfs   nodev,nosuid    0   0' >> $MOUNT_DIR/root/etc/fstab
echo 'tmpfs   /var/tmp    tmpfs   nodev,nosuid    0   0' >> $MOUNT_DIR/root/etc/fstab


cp $MOUNT_DIR/root/etc/systemd/journald.conf $MOUNT_DIR/root/etc/systemd/journald.conf-backup
cat $MOUNT_DIR/root/etc/systemd/journald.conf-backup > $MOUNT_DIR/root/etc/systemd/journald.conf
#echo Storage="volatile" >> $MOUNT_DIR/root/etc/systemd/journald.conf
echo Storage="none" >> $MOUNT_DIR/root/etc/systemd/journald.conf


systemd-nspawn  --timezone=off  --directory ${MOUNT_DIR}/root/

```
pacman -Sc --noconfirm
systemctl  mask systemd-random-seed
systemctl  disable systemd-hostnamed
systemctl  disable systemd-timesyncd

history -c -w
# extreme:
#systemctl  mask systemd-homed
#systemctl  mask systemd-logind
#systemctl  mask systemd-userdbd
exit
```



umount ${DEV}p1
umount ${DEV}p2
losetup -d $DEV