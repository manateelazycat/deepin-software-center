#!/bin/sh
# Update translation.

for poFile in `find ../locale/ -name *.po`
do
    base=${poFile%.*}
    msgfmt $poFile -o $base.mo
    echo "Update translation: $poFile"
done    
