#!/bin/sh

for pkgfile in `ls ../AppIcon/`
do
    if [ ! -f ../pkgInfo/${pkgfile%.*} ]
    then
        echo $pkgfile
    fi
done
