set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')

rm /etc/localtime -f
ln -s /usr/share/zoneinfo/UTC /etc/localtime

pacman-key --init
pacman-key --populate
pacman -Syy
pacman -Syu --noconfirm
pacman -S python-pip rng-tools dosfstools devtools libjpeg uboot-tools base-devel parted dhclient git cmake   --needed --noconfirm
pacman -S wiringpi   --needed --noconfirm
pacman -Scc --noconfirm

pip install --upgrade pip --no-cache-dir
pip install wheel --no-cache-dir
pip install requests --no-cache-dir
#pip install faster_than_requests --no-cache-dir
pip install gpiozero --no-cache-dir
pip install Adafruit_DHT --install-option="${ADAFRUIT_DHT_OPTION}" --no-cache-dir
export READTHEDOCS=True; pip install picamera  --no-cache-dir # hack to circumvent virtual pi issue

pip install /opt/sticky_pi/sticky_pi_device.tar.gz --no-cache-dir

cd  /opt/sticky_pi/take_picture && sh build.sh

mkdir ${SPI_IMAGE_DIR}
date
history -c -w
