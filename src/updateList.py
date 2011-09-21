#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Yong Wang
#
# Author:     Yong Wang <lazycat.manatee@gmail.com>
# Maintainer: Yong Wang <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from utils import *
import apt
import apt.progress
import sys
import os
import glib
import stat
import time
import threading as td

class UpdateList(td.Thread):
    '''Update package list.'''
	
    def __init__(self, cache, statusbar, refreshUpdateViewCallback):
        '''Init for UpdateList.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit
        
        self.cache = cache
        self.statusbar = statusbar
        self.refreshUpdateViewCallback = refreshUpdateViewCallback
        self.progress = UpdateListProgress(
            self.updateCallback,
            self.finishCallback
            )
        
    def run(self):
        '''Update package list.'''
        # Get last update hours.
        agoHours = self.getLastUpdateHours()

        # Just update one day after.
        if agoHours != None and agoHours >= UPDATE_INTERVAL:
        # if True:
            self.cache.update(self.progress)
        else:
            print "Just update system %s hours ago" % (agoHours)
        
    @postGUI
    def updateCallback(self, percent):
        '''Update callback for progress.'''
        self.statusbar.setStatus("正在更新软件列表%s%%." % percent)
        
    @postGUI
    def finishCallback(self):
        '''Finish callback for progress.'''
        # Refresh update view.
        self.refreshUpdateViewCallback()

        # Update status.
        self.statusbar.setStatus("更新软件列表完毕。")
        
        # Reset statusbar after 2 seconds.
        glib.timeout_add_seconds(2, self.resetStatus)
        
    def resetStatus(self):
        '''Reseet status.'''
        self.statusbar.initStatus()
    
        return False
        
    def getLastUpdateHours(self):
        """
        Return the number of hours since the last successful apt-get update
        
        If the date is unknown, return "None"
        """
        if not os.path.exists("/var/lib/apt/periodic/update-success-stamp"):
            return None
        # calculate when the last apt-get update (or similar operation) was performed.
        mtime = os.stat("/var/lib/apt/periodic/update-success-stamp")[stat.ST_MTIME]
        agoHours = int((time.time() - mtime) / (60 * 60))
        return agoHours

class UpdateListProgress(apt.progress.FetchProgress):
    """ Ready to use progress object for terminal windows """

    def __init__(self, updateCallback, finishCallback):
        apt.progress.FetchProgress.__init__(self)
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback

    def pulse(self):
        """Called periodically to update the user interface.

        Return True to continue or False to cancel.
        """
        apt.progress.FetchProgress.pulse(self)
        
        self.updateCallback("%2.f" % (self.percent))
        
        return True

    def stop(self):
        """Called when all files have been fetched."""
        self.finishCallback()
