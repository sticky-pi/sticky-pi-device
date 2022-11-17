include ./.env
export

OS_IMG_NAME:=$(shell date "+%Y-%m-%d")_sticky_pi_${SPI_ARCH}.img
PYTHON_RESOURCES := $(shell find src -name \*.py -print)
BASE_OS_IMG_NAME:= base-${OS_IMG_NAME}
CUSTOM_OS_IMG_NAME:= custom-${OS_IMG_NAME}
DT_BLOB := ./os_stub/boot/dt-blob.bin
PYTHON_PACKAGE :=./os_stub/opt/sticky_pi/sticky_pi_device.tar.gz
NET_CONF :=./os_stub/etc/wpa_supplicant/wpa_supplicant.conf
PACMAN_MIRROR_CONF :=./os_stub/etc/pacman.d/mirrorlist

.PHONY: base_os custom_os device_tree all
all: custom_os

base_os: ${BASE_OS_IMG_NAME}.gz
custom_os: ${CUSTOM_OS_IMG_NAME}.gz
#final_os: ${OS_IMG_NAME}.gz
device_tree: ${DT_BLOB}
net_conf: ${NET_CONF}
python_package: ${PYTHON_PACKAGE}
pacman_mirror_conf : ${PACMAN_MIRROR_CONF}



${BASE_OS_IMG_NAME}.gz: utils/make_base_os.sh
	@set +a
	@bash $< || (rm -f tmp-${OS_IMG_NAME}; echo "Failed to make base image!"; exit 1)
	@echo "Made base image. Now compressing..."
	@gzip ${BASE_OS_IMG_NAME} -f
	@echo "Done with $@.gz"
	@set -a


${DT_BLOB}: utils/dt-blob.dts
	@sed  "s/<SPI_FLASH_GPIO>/${SPI_FLASH_GPIO}/g" $< > $<.parsed.dts
	@#echo $<.parsed.dts
	@dtc -I dts -O dtb $<.parsed.dts -o $@ 2> /dev/null
	@echo Made $@

${PYTHON_PACKAGE}: ${PYTHON_RESOURCES} .env
	@echo "# Do not modify manually. Built automatically from ../../.env" > src/sticky_pi_device/_version.py
	@echo "__version__ = '${SPI_VERSION}'" >> src/sticky_pi_device/_version.py
	@cd src && rm -rf dist && python setup.py sdist
	@mkdir  ./os_stub/opt/sticky_pi -p # fixme, should be dynamically defined
	@cp src/dist/*.tar.gz $@ -v
	@echo Made $@

${NET_CONF}: .env
	@mkdir -p $(shell dirname $@)
	@echo "ctrl_interface=DIR=/var/run/wpa_supplicant" > $@
	@echo "network={" >> $@
	@echo "ssid=\"${SPI_WIFI_SSID}\"" >>  $@
	@echo "scan_ssid=0" >> $@
	@echo "key_mgmt=WPA-PSK" >> $@
	@echo "psk=\"${SPI_WIFI_PASSWORD}\"" >> $@
#	@echo "proto=RSN" >> $@
#	@echo "pairwise=CCMP" >> $@
#	@echo "auth_alg=OPEN" >> $@
	@echo "}" >> $@
	@echo Made $@

${PACMAN_MIRROR_CONF}: .env
	@mkdir -p $(shell dirname $@)
	@echo -n "Server = " > $@
	@echo ${MIRROR_URL} >> $@
	@echo Made $@


${CUSTOM_OS_IMG_NAME}.gz: utils/emulate_arm.sh  base-${OS_IMG_NAME}.gz ${PYTHON_PACKAGE} ${NET_CONF}  ${DT_BLOB} ${PACMAN_MIRROR_CONF}
	@set +a
	@bash $<  || (rm -f tmp-${OS_IMG_NAME};  echo "Failed to make final image!"; exit 1)
	@echo "Made final image ${CUSTOM_OS_IMG_NAME}! Compressing to $@"
	@gzip ${CUSTOM_OS_IMG_NAME} -f
	@set -a

#${OS_IMG_NAME}.gz: utils/compile_take_picture.sh custom-${OS_IMG_NAME}.gz
#	@set +a
#	@bash $<  || (rm -f tmp-${OS_IMG_NAME};  echo "Failed to make final image!"; exit 1)
#	@echo "Made final image ${OS_IMG_NAME}! Compressing to $@"
#	@gzip ${OS_IMG_NAME} -f
#	@set -a

clean:
	rm tmp-*.img -f ${NET_CONF} ${DT_BLOB} ${PYTHON_PACKAGE}
	losetup --detach-all

cleanall: clean
	rm base-*.img.gz custom-*.img.gz   -f


# export $(grep -v '^#' /etc/environment | xargs -d '\r\n');
# pip install  --no-dependencies--force-reinstall --upgrade /opt/sticky_pi/sticky_pi_device.tar.gz
