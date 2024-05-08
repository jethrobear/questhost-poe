#!/bin/sh

# Alpine customization
ln -s /build/questhost-poe/terminal/static/splash.png /etc/X11/xdm/
cp /etc/X11/xdm/xdm-config /etc/X11/xdm/xdm-config.old
sed -i '/^DisplayManager\*resources\:/d' /etc/X11/xdm/xdm-config
sed -i '/^DisplayManager\*setup\:/d' /etc/X11/xdm/xdm-config
sed -i '/^DisplayManager\*startup\:/d' /etc/X11/xdm/xdm-config
tee -a /etc/X11/xdm/xdm-config << EOF
DisplayManager*resources: /etc/X11/xdm/Xresources_custom
DisplayManager*setup: /etc/X11/xdm/Xsetup_custom
DisplayManager*startup: /etc/X11/xdm/Xstartup_custom
EOF 

tee /etc/X11/xdm/Xresources_custom << EOF
# cp -f /etc/X11/xdm/Xresources /etc/X11/xdm/Xresources_custom
# echo "

Xmessage*geometry:              170x27+20+20
Xmessage*background:            black
Xmessage*foreground:            red
Xmessage*Font:                  -xos4-terminus-*-r-normal-*-*-180-*-*-*-*-*-*
Xmessage*borderWidth:           0

Xmessage*message.scrollVertical:        Never
Xmessage*message.scrollHorizontal:      Never
Xmessage*message*background:            black

Xmessage*Text*background:       white
Xmessage*Text*foreground:       red
Xmessage*Text.borderColor:      black
Xmessage*Text.borderWidth:      0
Xmessage*Text*font:             -xos4-terminus-*-r-normal-*-*-180-*-*-*-*-*-*" >> /etc/X11/xdm/Xresources_custom
EOF

tee /etc/X11/xdm/Xsetup_custom << EOF
#!/bin/sh
#
# This script is run as root before showing login widget.

#--- set a fullscreen image in background
xloadimage -onroot -quiet -fullscreen /etc/X11/xdm/splash.png

#--- set Shutdown/Reboot buttons
(
xmessage -buttons Shutdown:20,Reboot:21 "" ;
case \$? in
    20)
	TERM=linux openvt -c 1 -f /usr/bin/clear
        exec openvt -c 1 -f -s -- /sbin/shutdown -hP now
        ;;
    21)
	TERM=linux openvt -c 1 -f /usr/bin/clear
        exec openvt -c 1 -f -s /sbin/reboot
        ;;
    *)
        echo "Xmessage closed on $(date)"
        ;;
esac
) &
EOF

tee /etc/X11/xdm/Xstartup_custom << EOF
#!/bin/sh
#
# This script is run as root after the user logs in.  If this script exits with
# a return code other than 0, the user's session will not be started.

# terminate xmessage
killall xmessage

# set the X background to plain black
xsetroot -solid black

if [ -x /etc/X11/xdm/Xstartup ]; then
  /etc/X11/xdm/Xstartup
fi

# vim:set ai et sts=2 sw=2 tw=0:
EOF