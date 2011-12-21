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
import gtk
import utils

class Titlebar(object):
    '''Title bar.'''
	
    def __init__(self, selectThemeCallback, showMoreWindowCallback, minCallback, maxCallback, closeCallback):
        '''Init for title bar.'''
        self.box = gtk.VBox()
        
        self.controlBox = gtk.HBox()
        self.controlAlign = gtk.Alignment()
        self.controlAlign.set(1.0, 0.0, 0.0, 0.0)
        self.controlAlign.add(self.controlBox)
        self.box.add(self.controlAlign)
        
        self.themeButton = gtk.Button()
        self.themeButton.connect("button-release-event", lambda w, e: selectThemeCallback(w, e))
        drawButton(self.themeButton, "theme", "navigate")
        self.controlBox.pack_start(self.themeButton, False, False)

        self.moreButton = gtk.Button()
        self.moreButton.connect("button-release-event", lambda w, e: showMoreWindowCallback(w, e))
        drawButton(self.moreButton, "more", "navigate")
        self.controlBox.pack_start(self.moreButton, False, False)
        
        self.minButton = gtk.Button()
        self.minButton.connect("button-release-event", lambda w, e: minCallback())
        drawButton(self.minButton, "min", "navigate")
        self.controlBox.pack_start(self.minButton, False, False)
        
        self.maxButton = gtk.Button()
        self.maxButton.connect("button-release-event", lambda w, e: maxCallback())
        drawButton(self.maxButton, "max", "navigate")
        self.controlBox.pack_start(self.maxButton, False, False)

        self.closeButton = gtk.Button()
        self.closeButton.connect("button-release-event", lambda w, e: closeCallback())
        drawButton(self.closeButton, "close", "navigate")
        self.controlBox.pack_start(self.closeButton, False, False)
        
        self.box.show_all()
