#!/bin/bash
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')

gpio -g mode ${SPI_FLASH_GPIO} out
file=$(mktemp).jpg


pkill wpa_supplicant

for i in $(seq 10)
do
  #detected, we blink/flash slowly every time we try to take a picture
  gpio -g write ${SPI_FLASH_GPIO} 1
  sleep 0.1
  gpio -g write ${SPI_FLASH_GPIO} 0
  /opt/vc/bin/raspistill -o ${file} -w 1296 -h 972 -vf -t 1
  decoded=$(zbarimg ${file} -q)
  if echo ${decoded} | grep "QR-Code:.*,.*" -q
  then
    #detected, we blink 5 times, quickly
    for i in $(seq 5)
    do
      gpio -g write ${SPI_FLASH_GPIO} 1
      sleep 0.05
      gpio -g write ${SPI_FLASH_GPIO} 0
      sleep 0.05
    done

    code_str=$(echo ${decoded} | sed s/"QR-Code:"//g)
    ssid=$(echo ${code_str} | cut -f 1 -d ,)
    pass=$(echo ${code_str} | cut -f 2 -d ,)

    wpa_supplicant -B -i wlan0 -c <(wpa_passphrase ${ssid} ${pass})
    sleep 2
    dhclient -x
    dhclient wlan0 -nw
    for i in $(seq 10)
    do
      # internet has worked
      # we make update the configuration file, through copy and move, since it is more atomic
      ip a show dev wlan0 | grep 'inet ' && (
      cp ${SPI_IMAGE_DIR}/'wpa_supplicant.conf' ${SPI_IMAGE_DIR}/'wpa_supplicant.conf.tmp'
      wpa_passphrase ${ssid} ${pass} >> ${SPI_IMAGE_DIR}/'wpa_supplicant.conf.tmp'
      mv ${SPI_IMAGE_DIR}/'wpa_supplicant.conf.tmp' ${SPI_IMAGE_DIR}/'wpa_supplicant.conf'
      return 0
      )
      sleep 1
    done
    # found qr code, but could NOT connect
    return 2
  else
    # No qr code in image
    sleep 1
  fi
done
# never found any qr code
return 1