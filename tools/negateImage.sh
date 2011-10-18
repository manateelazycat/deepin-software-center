#!/bin/sh
# Negate image, useful for theme test.

for file in `find ../theme/test/ -type f`
do 
    echo "Negate $file"
    convert -negate $file $file
done
