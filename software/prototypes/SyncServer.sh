rfkill unblock all
ip link set wlan0 up
wpa_supplicant -iwlan0  -B -Dnl80211 -c /sticky_pi_data/wpa_supplicant.conf
sleep 2
dhclient -x
dhclient wlan0 -nw
bash


# ~~entropy store~~
# ~~wext~~

# disabble wps?!

# wait for interface to be up?



