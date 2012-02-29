#!/usr/bin/env python
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

from checkUpdate import *
from dbus.mainloop.glib import DBusGMainLoop
from lang import __, getDefaultLanguage
import dbus
import glib
import sys

class UpdateMonitor(object):
    '''Update monitor.'''
	
    def run(self):
        '''Run.'''
        # Run first time.
        self.update()
        
        # Update package list every 24 hours.
        glib.timeout_add_seconds(60 * 60 * 24, self.update)
        
    def update(self):
        '''Update.'''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        try:
            s.bind(SOCKET_UPDATEMANAGER_ADDRESS)
            s.close()
            
            runCommand("./checkUpdate.py")
        except Exception, e:
            print "Has one update manager running..."
            s.close()
            
        return True    
        
if __name__ == "__main__":
    # Init loop.
    loop = gobject.MainLoop()

    # Start network watcher.
    networkWatcher = UpdateMonitor()
    networkWatcher.run()
    
    # Run loop.
    loop.run()
