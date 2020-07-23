cp ./config/wpa_supplicant.conf /etc/

ifdown wlan0
rm -f /var/lib/dhcp/*
ifup wlan0

