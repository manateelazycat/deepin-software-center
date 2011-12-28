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

from constant import *
from draw import *
from lang import __, getDefaultLanguage
from theme import *
import cairo
import gtk
import utils

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
        
        self.joinUs = gtk.Label()
        self.joinUs.set_markup("<span foreground='%s' size='%s'>%s</span>" % (
                appTheme.getDynamicColor("statusText").getColor(),
                LABEL_FONT_SIZE, __("Join Us")))
        self.joinUsEventBox = gtk.EventBox()
        self.joinUsEventBox.set_visible_window(False)
        self.joinUsEventBox.add(self.joinUs)
        self.joinUsEventBox.connect("button-press-event", lambda w, e: sendCommand("xdg-open http://www.linuxdeepin.com/recruitment"))
        setClickableCursor(self.joinUsEventBox)
        self.joinUsAlign = gtk.Alignment()
        self.joinUsAlign.set_padding(0, 0, 0, self.paddingX)
        self.joinUsAlign.set(1.0, 0.5, 0.0, 0.0)
        self.joinUsAlign.add(self.joinUsEventBox)
        self.box.pack_start(self.joinUsAlign)
        
        # Connect components.
        self.eventbox.add(self.box)
        self.eventbox.show_all()
        
    def initStatus(self):
        '''Init status.'''
        self.name.set_markup("<span foreground='%s' size='%s'>%s %s</span>" % (
                appTheme.getDynamicColor("statusText").getColor(),
                LABEL_FONT_SIZE,
                __("Deepin Software Center"), 
                VERSION))

    def setStatus(self, status):
        '''Set status.'''
        self.name.set_markup("<span foreground='%s' size='%s'>%s</span>" % (
                appTheme.getDynamicColor("statusText").getColor(),
                LABEL_FONT_SIZE, 
                status))
