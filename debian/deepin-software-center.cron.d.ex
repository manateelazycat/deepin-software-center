#
# Regular cron jobs for the deepin-software-center package
#
0 4	* * *	root	[ -x /usr/bin/deepin-software-center_maintenance ] && /usr/bin/deepin-software-center_maintenance
