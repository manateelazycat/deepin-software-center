#!/bin/sh
# Convert jpg to png

for img in `ls ../pkgData/AppIcon/ | grep .jpg`
do
    convert ../pkgData/AppIcon/$img ../pkgData/AppIcon/${img%.*}.png
    rm ../pkgData/AppIcon/$img
done    
