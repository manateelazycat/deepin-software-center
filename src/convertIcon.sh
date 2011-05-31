#!/bin/sh
# convertIcon.sh ImageDirectory TargetDirectory

for img in `ls $1`
do 
    echo "Convert $1$img to $2${img%.*}.png" 
    convert -resize $3x$3 $1$img $2${img%.*}.png
done
