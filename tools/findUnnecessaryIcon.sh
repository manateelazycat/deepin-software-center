#!/bin/sh

for pkgfile in `ls ../pkgData/AppIcon/`
do
    if [ ! -f ../pkgData/pkgInfo/${pkgfile%.*} ]
    then
        echo $pkgfile
    fi
done
