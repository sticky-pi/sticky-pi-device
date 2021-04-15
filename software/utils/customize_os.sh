set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')

rm /etc/localtime -f
ln -s /usr/share/zoneinfo/UTC /etc/localtime

pacman-key --init
pacman-key --populate
pacman -Syy
pacman -Syu --noconfirm
pacman -S python-pip dosfstools devtools libjpeg uboot-tools base-devel parted --needed --noconfirm
pacman -Scc --noconfirm

pip install --upgrade pip --no-cache-dir
pip install rpi_ws281x --no-cache-dir
pip install pytz netifaces pillow --no-cache-dir
pip install piexif --no-cache-dir
pip install keyboard --no-cache-dir
pip install pyserial --no-cache-dir
pip install Adafruit_DHT --install-option="${ADAFRUIT_DHT_OPTION}" --no-cache-dir
export CFLAGS=-fcommon; pip install RPi.GPIO --no-cache-dir
export READTHEDOCS=True; pip install picamera  --no-cache-dir # hack to circumvent virtual pi issue

pip install /opt/sticky_pi/sticky_pi_device.tar.gz --no-cache-dir

systemctl enable first_boot.service
systemctl disable sshd.service
systemctl disable systemd-resolved.service

date
history -c -w
