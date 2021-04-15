include ./.env
export
OS_IMG_NAME:=$(shell date "+%Y-%m-%d")_sticky_pi_${SPI_ARCH}.img
PYTHON_RESOURCES := $(shell find src -name \*.py -print)
.PHONY: base_os custom_os device_tree
BASE_OS_IMG_NAME:= base-${OS_IMG_NAME}
DT_BLOB := ./os_stub/boot/dt-blob.bin
PYTHON_PACKAGE :=./os_stub/opt/sticky_pi/sticky_pi_device.tar.gz
NET_CONF :=./os_stub/etc/netctl/${SPI_NET_INTERFACE}

base_os: ${BASE_OS_IMG_NAME}
custom_os: spi-${OS_IMG_NAME}
device_tree: ${DT_BLOB}
net_conf: ${NET_CONF}
python_package: ${PYTHON_PACKAGE}


${BASE_OS_IMG_NAME}: utils/make_base_os.sh  utils/customize_os.sh os_stub ${DT_BLOB}
	set +a
	bash $< || rm -f tmp-${OS_IMG_NAME}
	set -a
	echo Made base image $@

${DT_BLOB}: utils/dt-blob.dts
	dtc -I dts -O dtb $< -o $@

${PYTHON_PACKAGE}: ${PYTHON_RESOURCES}
	cd src && rm -r dist && python setup.py sdist
	cp src/dist/*.tar.gz $@ -v

${NET_CONF}: .env
	mkdir -p $(shell dirname $@)
	echo "Interface=wlan0" > $@
	echo "Connection=wireless" >>  $@
	echo "Security=wpa"  >> $@
	echo "IP=dhcp"  >> $@
	echo "ESSID='$SPI_WIFI_SSID'"  >> $@
	echo "Key='$SPI_WIFI_PASSWORD'" >> $@

spi-${OS_IMG_NAME}: utils/emulate_arm.sh  base-${OS_IMG_NAME} ${PYTHON_PACKAGE} ${NET_CONF}
	set +a
	bash $< || rm -f tmp-${OS_IMG_NAME}
	echo Made final image $@ !
	set -a


clean:
	rm tmp-*.img -f
	losetup --detach-all

cleanall: clean
	rm base-*.img custom-*.img custom-*.ro -f
