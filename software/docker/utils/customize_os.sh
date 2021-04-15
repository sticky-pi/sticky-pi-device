
set -e
#    cannot work without bus
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
