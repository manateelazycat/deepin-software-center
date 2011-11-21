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

from lang import __
from theme import *
from constant import *
from draw import *
import cairo
import gtk
import pygtk
import utils
pygtk.require('2.0')

class Statusbar(object):
    '''Status bar.'''
	
    def __init__(self):
        '''Init for status bar.'''
        # Init.
        self.paddingX = 10
        self.paddingY = 5
        
        self.eventbox = gtk.EventBox()
        drawStatusbarBackground(
            self.eventbox,
            appTheme.getDynamicPixbuf("statusbar/background.png"),
            appTheme.getDynamicDrawType("statusbar"),
            appTheme.getDynamicAlphaColor("frameLigtht"),
            appTheme.getDynamicAlphaColor("statusbarTop"),
            )
        
        self.box = gtk.HBox()
        
        self.name = gtk.Label()
        self.initStatus()
        self.nameAlignment = gtk.Alignment()
        self.nameAlignment.set_padding(self.paddingY, self.paddingY, self.paddingX, self.paddingX)
        self.nameAlignment.set(0.0, 0.0, 0.0, 1.0)
        self.nameAlignment.add(self.name)
        self.box.pack_start(self.nameAlignment)
        
        # Connect components.
        self.eventbox.add(self.box)
        self.eventbox.show_all()
        
    def initStatus(self):
        '''Init status.'''
        self.name.set_markup("<span foreground='#FFFFFF' size='%s'>%s %s</span>" % (LABEL_FONT_SIZE, __("Deepin Software Center"), VERSION))

    def setStatus(self, status):
        '''Set status.'''
        self.name.set_markup("<span foreground='#FFFFFF' size='%s'>%s</span>" % (LABEL_FONT_SIZE, status))
