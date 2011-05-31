#!/bin/sh

case "$1" in
    "record" )
        git commit -a
        ;;
    "pull" )
        git pull git://github.com/manateelazycat/deepin-software-center.git
        ;;
    "push" )
        git push git@github.com:manateelazycat/deepin-software-center.git
        ;;
    * ) 
        echo "Help"
        echo "./repos.sh record         => record patch"
        echo "./repos.sh pull           => pull patch"
        echo "./repos.sh push           => push patch"
        ;;
    esac
