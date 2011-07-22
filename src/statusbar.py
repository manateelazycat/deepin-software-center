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

from constant import *
from draw import *
import cairo
import gtk
import pygtk
import utils
pygtk.require('2.0')

class Statusbar:
    '''Status bar.'''
	
    def __init__(self):
        '''Init for status bar.'''
        # Init.
        self.paddingX = 10
        self.paddingY = 5
        self.eventbox = gtk.EventBox()
        
        eventBoxSetBackground(
            self.eventbox,
            True, False,
            "./icons/statusbar/background.png")
        self.box = gtk.HBox()
        
        self.name = gtk.Label()
        self.initStatus()
        self.nameAlignment = gtk.Alignment()
        self.nameAlignment.set_padding(self.paddingY, self.paddingY, self.paddingX, self.paddingX)
        self.nameAlignment.set(0.0, 0.0, 0.0, 1.0)
        self.nameAlignment.add(self.name)
        self.box.pack_start(self.nameAlignment)
        
        self.join = gtk.Label()
        self.join.set_markup("<span foreground='#FFFFFF' size='%s' underline='single'>加入我们</span>" % (LABEL_FONT_SIZE))
        self.joinAlignment = gtk.Alignment()
        self.joinAlignment.set_padding(self.paddingY, self.paddingY, self.paddingX, self.paddingX)
        self.joinAlignment.set(1.0, 0.0, 0.0, 1.0)
        self.joinAlignment.add(self.join)
        self.joinBox = gtk.EventBox()
        self.joinBox.set_visible_window(False)
        self.joinBox.add(self.joinAlignment)
        self.joinBox.connect("button-press-event", lambda w, e: utils.runCommand("xdg-open http://www.linuxdeepin.com/job-offers"))
        self.box.pack_start(self.joinBox)
        utils.setClickableCursor(self.joinBox)
        
        # Connect components.
        self.eventbox.add(self.box)
        self.eventbox.show_all()
        
    def initStatus(self):
        '''Init status.'''
        self.name.set_markup("<span foreground='#FFFFFF' size='%s'>深度Linux软件中心 %s</span>" % (LABEL_FONT_SIZE, VERSION))

    def setStatus(self, status):
        '''Set status.'''
        self.name.set_markup("<span foreground='#FFFFFF' size='%s'>%s</span>" % (LABEL_FONT_SIZE, status))
