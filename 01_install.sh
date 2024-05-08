#!/bin/sh

# Download and install required files, this can be done before airgapping the system
setup-xorg-base
apk add xf86-video-fbdev openbox font-terminus
#apk add vulkan-loader mesa-gles
#apk add --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing surf
apk add git cmake make gd-dev libusb-dev gettext-dev
apk add py3-pillow py3-django py3-boto3 py3-qrcode
git clone https://git.familie-radermacher.ch/linux/ptouch-print.git /build/ptouch-print
git clone https://github.com/jethrobear/questhost-poe.git /build/questhost-poe

# Prepare XINITRC
tee ~questhost/.xinitrc << EOF
#!/bin/sh
python3 /build/questhost_poe/tui.py &
exec openbox-session
EOF

# Build ptouch-print
cd /build/ptouch-print/
./build.sh
ln -s udev/90-usb-ptouch-permissions.rules /lib/udev/rules.d
ln -s /build/ptouch-print/build/ptouch-print /usr/local/bin

# Prepare QHPOE
cd /build/questhost-poe
python3 manage.py makemigrations
python3 manage.py migrate
DJANGO_SUPERUSER_USERNAME=questhost DJANGO_SUPERUSER_PASSWORD=questhost DJANGO_SUPERUSER_EMAIL=questhost@furrybrigade.net python3 manage.py createsuperuser --noinput
chmod a+rw -R /build/questhost-poe
tee /etc/init.d/questhostpoe << EOF
#!/sbin/openrc-run

depend() {
    need net
}

directory="/build/questhost-poe"
command="/usr/bin/python3"
command_background="true"
command_args="manage.py runserver"
command_user="questhost:questhost"
pidfile="/build/questhost-poe/pid"
EOF
chmod a+x /etc/init.d/questhostpoe
rc-update add questhostpoe default


# TODO: Only update DB after setting up AWS CLI
#python3 manage.py user_tickets