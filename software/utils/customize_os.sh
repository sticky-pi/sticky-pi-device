set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')

rm /etc/localtime -f
ln -s /usr/share/zoneinfo/UTC /etc/localtime

pacman-key --init
pacman-key --populate
pacman -Syy
pacman -Syu --noconfirm
pacman -S python-pip rng-tools dosfstools devtools libjpeg uboot-tools base-devel parted dhclient git cmake   --needed --noconfirm
pacman -Scc --noconfirm

pip install --upgrade pip --no-cache-dir
pip install requests --no-cache-dir
export READTHEDOCS=True; pip install picamera  --no-cache-dir # hack to circumvent virtual pi issue

pip install /tmp/sticky_pi/sticky_pi_device.tar.gz --no-cache-dir

cd  /tmp/sticky_pi/take_picture && sh build.sh


date
history -c -w
