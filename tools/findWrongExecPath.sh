#!/bin/bash

for pathFile in `ls ../pkgData/pkgPath/`
do
    lines=`cat ../pkgData/pkgPath/$pathFile | wc -l`
    if [ $lines -ne 1 ]
    then
        echo $pathFile
    fi
done
