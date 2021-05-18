include ./.env
export

OS_IMG_NAME:=$(shell date "+%Y-%m-%d")_sticky_pi_${SPI_ARCH}.img
PYTHON_RESOURCES := $(shell find src -name \*.py -print)
BASE_OS_IMG_NAME:= base-${OS_IMG_NAME}
DT_BLOB := ./os_stub/boot/dt-blob.bin
PYTHON_PACKAGE :=./os_stub/opt/sticky_pi/sticky_pi_device.tar.gz
NET_CONF :=./os_stub/etc/netctl/${SPI_NET_INTERFACE}

.PHONY: base_os custom_os device_tree all
all: custom_os

base_os: ${BASE_OS_IMG_NAME}
custom_os: ${OS_IMG_NAME}.gz
device_tree: ${DT_BLOB}
net_conf: ${NET_CONF}
python_package: ${PYTHON_PACKAGE}




${BASE_OS_IMG_NAME}: utils/make_base_os.sh
	@set +a
	@bash $< || (rm -f tmp-${OS_IMG_NAME}; echo "Failed to make base image!"; exit 1)
	@echo "Made base image $@ !"
	@set -a


${DT_BLOB}: utils/dt-blob.dts
	@dtc -I dts -O dtb $< -o $@ 2> /dev/null
	@echo Made $@

${PYTHON_PACKAGE}: ${PYTHON_RESOURCES} .env
	@echo "# Do not modify manually. Built automatically from ../../.env" > src/sticky_pi_device/_version.py
	@echo "__version__ = '${SPI_VERSION}'" >> src/sticky_pi_device/_version.py
	@cd src && rm -r dist && python setup.py sdist
	@cp src/dist/*.tar.gz $@ -v
	@echo Made $@

${NET_CONF}: .env
	@mkdir -p $(shell dirname $@)
	@echo "Interface=wlan0" > $@
	@echo "Connection=wireless" >>  $@
	@echo "Security=wpa"  >> $@
	@echo "IP=dhcp"  >> $@
	@echo "ESSID='${SPI_WIFI_SSID}'"  >> $@
	@echo "Key='${SPI_WIFI_PASSWORD}'" >> $@
	@echo Made $@

${OS_IMG_NAME}.gz: utils/emulate_arm.sh  base-${OS_IMG_NAME} ${PYTHON_PACKAGE} ${NET_CONF}  ${DT_BLOB}
	@set +a
#fixme disable rm close
	@bash $<  || (rm -f tmp-${OS_IMG_NAME};  echo "Failed to make final image!"; exit 1)
	@echo "Made final image ${OS_IMG_NAME}! Compressing to $@"
	@gzip ${OS_IMG_NAME} -f
	@set -a



clean:
	rm tmp-*.img -f ${NET_CONF} ${DT_BLOB} ${PYTHON_PACKAGE}
	losetup --detach-all

cleanall: clean
	rm base-*.img spi-*.img  -f


# export $(grep -v '^#' /etc/environment | xargs -d '\r\n');
# pip install  --no-dependencies--force-reinstall --upgrade /opt/sticky_pi/sticky_pi_device.tar.gz
