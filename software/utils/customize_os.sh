set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')

rm /etc/localtime -f
ln -s /usr/share/zoneinfo/UTC /etc/localtime

pacman-key --init
pacman-key --populate
pacman -Syy
pacman -Syu --noconfirm
pacman -S python-pip python-requests python-wheel rng-tools dosfstools devtools libjpeg uboot-tools base-devel parted dhclient git cmake  libtommath --needed --noconfirm
pacman -S wiringpi zbar uvicorn python-fastapi python-pytz python-pydantic python-aiofiles  --needed --noconfirm

pacman -Scc --noconfirm

pip install --upgrade pip --no-cache-dir
pip install zeroconf --no-cache-dir
# pip install gpiozero --no-cache-dir

export CFLAGS=-fcommon; pip install RPi.GPIO --no-cache-dir
pip install Adafruit_DHT --install-option="${ADAFRUIT_DHT_OPTION}" --no-cache-dir
# hack to circumvent virtual pi issue (when building on emulated platform)
export READTHEDOCS=True; pip install picamera  --no-cache-dir

pip install /opt/sticky_pi/sticky_pi_device.tar.gz --no-cache-dir

cd  /opt/sticky_pi/take_picture && sh build.sh

mkdir ${SPI_IMAGE_DIR}


echo Now compiling our own WPA supplicant
cd /tmp/
curl  https://w1.fi/releases/wpa_supplicant-2.10.tar.gz > wpa_supplicant-2.10.tar.gz
tar -xvf wpa_supplicant-2.10.tar.gz

cat > wpa_supplicant/.config << "EOF"
CONFIG_BACKEND=file
CONFIG_CTRL_IFACE=y
CONFIG_DEBUG_FILE=y
CONFIG_DEBUG_SYSLOG=y
CONFIG_DEBUG_SYSLOG_FACILITY=LOG_DAEMON
CONFIG_DRIVER_NL80211=y
CONFIG_DRIVER_WIRED=y
CONFIG_EAP_GTC=y
CONFIG_EAP_LEAP=y
CONFIG_EAP_MD5=y
CONFIG_EAP_MSCHAPV2=y
CONFIG_EAP_OTP=y
CONFIG_EAP_PEAP=y
CONFIG_IEEE8021X_EAPOL=y
CONFIG_IPV6=y
CONFIG_LIBNL32=y
CONFIG_PEERKEY=y
CONFIG_PKCS12=y
CONFIG_READLINE=y
CONFIG_SMARTCARD=y
CONFIG_TLS=internal
CONFIG_INTERNAL_LIBTOMMATH_FAST=y
CFLAGS += -I/usr/include/libnl3
EOF

cd wpa_supplicant && make BINDIR=/usr/sbin LIBDIR=/usr/lib
install -v -m755 wpa_{cli,passphrase,supplicant} /usr/sbin/

date
history -c -w