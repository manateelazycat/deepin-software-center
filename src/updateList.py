#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Wang Yong
#
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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

from apt.progress.old import FetchProgress
from lang import __, getDefaultLanguage
from utils import *
import downloadUpdateData
import glib
import os
import stat
import sys
import threading as td
import time

class UpdateList(td.Thread):
    '''Update package list.'''
	
    def __init__(self, cache, statusbar):
        '''Init for UpdateList.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit
        
        self.cache = cache
        self.statusbar = statusbar
        self.progress = UpdateListProgress(
            self.updateCallback,
            self.finishCallback
            )
        
    def run(self):
        '''Update package list.'''
        # Get last update hours.
        agoHours = getLastUpdateHours("/var/lib/apt/periodic/update-success-stamp")

        # Just update one day after.
        if agoHours != None and agoHours >= UPDATE_INTERVAL:
        # if True:
            try:
                self.cache.update(self.progress)
            except Exception, e:
                print "UpdateList.run(): %s" % (e)
        else:
            print "Just update system %s hours ago" % (agoHours)
        
    @postGUI
    def updateCallback(self, percent):
        '''Update callback for progress.'''
        self.statusbar.setStatus(__("Updating souces list ..."))
        
    @postGUI
    def finishCallback(self):
        '''Finish callback for progress.'''
        # Update status.
        self.statusbar.setStatus(__("Update sources list completed."))
        
        # Reset statusbar after 2 seconds.
        glib.timeout_add_seconds(2, self.resetStatus)
        
        # Download update data from server, this must execute after list update complete.
        downloadUpdateData.DownloadUpdateData().start()
        
    def resetStatus(self):
        '''Reseet status.'''
        self.statusbar.initStatus()
    
        return False
        
class UpdateListProgress(FetchProgress):
    """ Ready to use progress object for terminal windows """

    def __init__(self, updateCallback, finishCallback):
        super(UpdateListProgress, self).__init__()
        
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback

    def pulse(self):
        """Called periodically to update the user interface.

        Return True to continue or False to cancel.
        """
        try:
            self.percent = (((self.currentBytes + self.currentItems) * 100.0) /
                            float(self.totalBytes + self.totalItems))
            if self.currentCPS > 0:
                self.eta = ((self.totalBytes - self.currentBytes) /
                            float(self.currentCPS))
                
            self.updateCallback("%2.f" % (self.percent))
        except Exception, e:
            print "UpdateListProgress.pulse(): %s" % (e)
        
        return True

    def stop(self):
        """Called when all files have been fetched."""
        self.finishCallback()
