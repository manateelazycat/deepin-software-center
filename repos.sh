#!/bin/sh

case "$1" in
    "record" )
        git commit -a
        ;;
    "pull" )
        git pull origin master
        ;;
    "push" )
        git push git@github.com:manateelazycat/deepin-software-center.git
        ;;
    "changelog" )
        git log --oneline
        ;;
    "checkout" )
        git checkout -- .
        ;;
    "revert" )
        git revert $2
        ;;
    * ) 
        echo "Help"
        echo "./repos.sh record         => record patch"
        echo "./repos.sh pull           => pull patch"
        echo "./repos.sh push           => push patch"
        echo "./repos.sh changelog      => show changelog"
        echo "./repos.sh checkout       => revert change code"
        echo "./repos.sh revert         => revert patch by id"
        ;;
    esac
