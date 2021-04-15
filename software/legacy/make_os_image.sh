#!/usr/bin/env bash

if [[ -v LAB_PI ]];
then
    echo "LAB_PI already set"
else

  LAB_PI=false
  while getopts ":l" o; do
      case "${o}" in
          l)
              LAB_PI=true
              ;;
          *)
              usage
              ;;
      esac
  done
fi

echo LAB_PI is $LAB_PI
sleep 1


if [ ${LAB_PI} = 'true' ]
then
  TARGET_SERVICE=take_picture.timer
  ZIP_IMG=ArchLinuxARM-rpi-2-latest.tar.gz
  ARCH=rpi2
  ADAFRUIT_DHT_OPTION=--force-pi3 #untested
else
  ZIP_IMG=ArchLinuxARM-rpi-latest.tar.gz
  TARGET_SERVICE=take_picture.service
  ARCH=rpi
  ADAFRUIT_DHT_OPTION=--force-pi2
fi

OS_IMG_NAME=$(date "+%Y-%m-%d")_sticky_pi_${ARCH}.img
ALARM_URL=http://os.archlinuxarm.org/os/$ZIP_IMG
MOUNT_DIR=/mnt/sticky_pi_root
MIRROR=de.mirror.archlinuxarm.org
SPI_DRIVE_LABEL=SPI_DRIVE


# if not in chroot
if [ $(systemd-detect-virt) = 'none' ]
then
    set -e
    wget $ALARM_URL  -nc
    dd bs=1M count=5000 if=/dev/zero of=$OS_IMG_NAME
    DEV="$(losetup --show -f -P "$OS_IMG_NAME")"

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
    cp make_os_image.sh ${MOUNT_DIR}/root/root/
    set +e

    # fixme this seems to be the point of --bind-root=/etc/resolv.conf
    # as in `systemd-nspawn -D /mnt/sdcard -M myARMMachine --bind-root=/etc/resolv.conf`
    # from https://wiki.archlinux.org/index.php/QEMU#Starting_QEMU_virtual_machines_on_boot
    rm ${MOUNT_DIR}/root/etc/resolv.conf
    cat /etc/resolv.conf > ${MOUNT_DIR}/root/etc/resolv.conf

    dtc -I dts -O dtb dt-blob.dts -o ./os_stub/boot/dt-blob.bin
    rsync -rvP --copy-links ./os_stub/ ${MOUNT_DIR}/root/root/os_stub
    chmod 700 ${MOUNT_DIR}/root/root/make_os_image.sh
    systemd-nspawn  --timezone=off --directory ${MOUNT_DIR}/root/  -E LAB_PI=${LAB_PI}  /root/make_os_image.sh

    umount ${DEV}p1
    umount ${DEV}p2
    losetup -d $DEV

else
    set -e
#    cannot work without buss
#    timedatectl set-timezone UTC
#    timedatectl set-ntp 0
    rm /etc/localtime -f
    ln -s /usr/share/zoneinfo/UTC /etc/localtime

    # a dir to mount the USB drives
    mkdir -p /mnt/${SPI_DRIVE_LABEL}

    #echo Server = http://$MIRROR'/$arch/$repo ' > /etc/pacman.d/mirrorlist
    pacman-key --init
    pacman-key --populate
    pacman -Syy
    #pacman -S pacman --needed --noconfirm
    pacman -Syu --noconfirm

    pacman -S python python-pip devtools uboot-tools base-devel libjpeg --needed --noconfirm

    pip install --upgrade pip
    pip install rpi_ws281x
#    pip install RPi.GPIO pytz netifaces pillow adafruit-circuitpython-dht
    pip install RPi.GPIO pytz netifaces pillow
    pip install piexif
    pip install Adafruit_DHT --install-option="${ADAFRUIT_DHT_OPTION}"
    pip install keyboard
    pip install pyserial

    #fixme alternative camera installation
    #    git clone https://github.com/pieelab/picamera
    # see https://github.com/waveform80/picamera/issues/604
#    curl  https://codeload.github.com/pieelab/picamera/tar.gz/1.3.1  --output picamera.tar.gz
#    tar -xvzf picamera.tar.gz
#    rm picamera.tar.gz
#    cd picamera*/
#    python setup.py sdist
#    pip install dist/picamera-*.tar.gz
#    cd -


    export READTHEDOCS=True; pip install picamera # hack to circumvent virtual pi issue

     cd /root/os_stub/
    rsync -rvP ./ /
    mkdir /sticky_pi_images

    systemctl enable ${TARGET_SERVICE}
    if [ ${LAB_PI} != 'true' ]
    then
        systemctl enable rtc-i2c.service
        systemctl disable sshd.service
        systemctl disable systemd-networkd.service
        systemctl disable systemd-resolved.service
    fi
    date
    history -c -w
fi

