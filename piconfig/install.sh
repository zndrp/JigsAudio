echo "Starting JigsAudio installer..."
sudo apt-get update
sudo apt-get install -y dnsmasq hostapd nginx
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
echo "Copying config files into place..."
sudo cp dhcpcd.conf /etc/dhcpcd.conf
sudo service dhcpcd restart
sudo cp dnsmasq.conf /etc/dnsmasq.conf
sudo cp hostapd.conf.orig /etc/hostapd/hostapd.conf.orig
sudo cp hostapd /etc/default/hostapd
sudo cp sysctl.conf /etc/sysctl.conf
sudo cp 10-wpa_supplicant /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
sudo chmod ugo+x rc.local
sudo cp rc.local /etc/rc.local
echo "Setting up nginx..."
sudo cp default /etc/nginx/sites-available/default
sudo chmod ugo+r ../.
echo "Setting up JigsAudio service..."
sudo chmod ugo+x jigsaudio.service
sudo cp jigsaudio.service /etc/systemd/system/jigsaudio.service
sudo systemctl daemon-reload
sudo systemctl enable jigsaudio.service
echo "COMPLETE!! Reboot device to start hotspot."
