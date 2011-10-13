#!/bin/sh
# pickPathFromDesktopFile.sh desktopDirectory pathDirectory

for pkgName in `ls $1`
do 
    echo "Convert $1$pkgName to $2${pkgName%.*}" 
    cat $1$pkgName | grep "^Exec" | sed 's/Exec=//' > $2${pkgName%.*}
done
