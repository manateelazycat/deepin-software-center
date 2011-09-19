#!/bin/sh

for pkgfile in `ls ../pkgData/pkgInfo/`
do
    if [ ! -f ../pkgData/AppIcon/$pkgfile.png ]
    then
        echo $pkgfile
    fi
done

# You can find icon through:
# "http://ubuntu.allmyapps.com/apps/install-" + pkgfile
# "https://admin.fedoraproject.org/pkgdb/apps/search/" + pkgfile
# "http://images.google.com/search?hl=zh-CN&gbv=2&biw=1366&bih=609&tbs=isz%3Aex%2Ciszw%3A48%2Ciszh%3A48&tbm=isch&sa=1&oq=grdesktop&aq=f&aqi=&aql=&gs_sm=e&gs_upl=23750l23750l0l1l1l0l0l0l0l0l0ll0&q=" + pkgfile

