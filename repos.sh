#!/bin/sh

case "$1" in
    "record" )
        git commit -a
        ;;
    "pull" )
        darcs pull http://patch-tag.com/r/AndyStewart/deepin-software-center
        ;;
    "push" )
        darcs push -a AndyStewart@patch-tag.com:/r/AndyStewart/deepin-software-center --set-default
        ;;
    * ) 
        echo "Help"
        echo "./repos.sh record         => record patch"
        echo "./repos.sh pull           => pull patch"
        echo "./repos.sh push           => push patch"
        ;;
    esac
