#!/bin/sh

for pkgfile in `ls ../pkgInfo/`
do
    if [ ! -f ../AppIcon/$pkgfile.png ]
    then
        echo $pkgfile
    fi
done

# You can find icon through "http://ubuntu.allmyapps.com/apps/install-" + pkgfile
