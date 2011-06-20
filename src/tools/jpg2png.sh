#!/bin/sh
# Convert jpg to png

for img in `ls ../AppIcon/ | grep .jpg`
do
    convert ../AppIcon/$img ../AppIcon/${img%.*}.png
    rm ../AppIcon/$img
done    
