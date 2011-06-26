#!/usr/bin/env python
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

from checkUpdate import *
import dbus
from dbus.mainloop.glib import DBusGMainLoop

class NetworkWatcher:
    '''Watch network status.'''
	
    # Network state.
    NM_STATE_UNKNOWN = 0
    NM_STATE_ASLEEP = 1
    NM_STATE_CONNECTING = 2
    NM_STATE_CONNECTED = 3
    NM_STATE_DISCONNECTED = 4
    
    def __init__(self):
        '''Init for NetworkWatcher.'''
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.Bus(dbus.Bus.TYPE_SYSTEM)
        self.networkState = self.NM_STATE_CONNECTED # make it always connected if NM isn't available
        
    def run(self):
        '''Run.'''
        # Get DBus object.
        obj = self.bus.get_object(
            "org.freedesktop.NetworkManager", 
            "/org/freedesktop/NetworkManager")
        
        # Register callback to StateChanged signal.
        obj.connect_to_signal(
            "StateChanged",
            self.updateNotify,
            dbus_interface="org.freedesktop.NetworkManager")
        
        # Run first time.
        interface = dbus.Interface(obj, "org.freedesktop.DBus.Properties")
        self.networkState = interface.Get("org.freedesktop.NetworkManager", "State")
        self.updateNotify(self.networkState)

    def updateNotify(self, state):
        '''Notify update.'''
        if state == self.NM_STATE_CONNECTED:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
            try:
                s.bind(SOCKET_UPDATEMANAGER_ADDRESS)
                s.close()
                
                runCommand("./checkUpdate.py")
            except Exception, e:
                s.close()
                
                print "Has one update manager running..."
        
if __name__ == "__main__":
    # Init loop.
    loop = gobject.MainLoop()

    # Start network watcher.
    networkWatcher = NetworkWatcher()
    networkWatcher.run()
    
    # Run loop.
    loop.run()
