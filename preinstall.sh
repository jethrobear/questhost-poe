sudo apt update
sudo apt --no-install-recommends install -y python3-pillow python3-django python3-boto3 awscli ninja libgtk-3-dev libwebkit2gtk-4.0-dev gettext libsoup2.4-dev cmake libgd-dev libusb-1.0-0-dev wmctl
mkdir -p ~/workspace

git clone https://hacktivis.me/git/badwolf.git ~/workspace/badwolf
cd ~/workspace/badwolf/
./configure && ninja

git clone https://git.familie-radermacher.ch/linux/ptouch-print.git ~/workspace/ptouch-print
cd ~/workspace/ptouch-print/
./build.sh
sudo cp udev/90-usb-ptouch-permissions.rules /lib/udev/rules.d

# TODO: Add our own setup here