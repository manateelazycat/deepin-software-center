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

from lang import __, getDefaultLanguage
from theme import *
import gobject
import gtk
import pango

class SearchEntry(gtk.Entry):
    '''Search entry.'''
	
    def __init__(self, parent, helpString, hintDColor, backgroundDColor, foregroundDColor, noHint=False):
        '''Init for search entry.'''
        # Init.
        gtk.Entry.__init__(self)
        self.helpString = helpString
        self.hintDColor = hintDColor
        self.backgroundDColor = backgroundDColor
        self.foregroundDColor = foregroundDColor
        self.ticker = 0
        
        # Set default font.
        self.modify_font(pango.FontDescription(DEFAULT_FONT + " 10"))
        
        # Clean input when first time focus in entry.
        if noHint:
            self.focusIn = True
            self.set_text(self.helpString)
        else:
            self.focusIn = False
            self.focusInHandler = self.connect("focus-in-event", lambda w, e: self.firstFocusIn())
            self.connect("expose-event", self.exposeCallback)
        
        # Show help string.
        self.updateColor()
        
        parent.connect("size-allocate", lambda w, e: self.realize())
        
    def exposeCallback(self, widget, event):
        '''Expose callback.'''
        if self.ticker != appTheme.ticker:
            self.ticker = appTheme.ticker
            self.updateColor()
        
    def updateColor(self):
        '''Update color.'''
        self.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.backgroundDColor.getColor()))
        if self.focusIn:
            self.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.foregroundDColor.getColor()))
        else:
            self.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.hintDColor.getColor()))
            self.set_text(self.helpString)
        
    def firstFocusIn(self):
        '''First touch callback.'''
        self.focusIn = True
        
        # Empty entry when first time focus in.
        self.set_text("")
        
        # Adjust input text color.
        self.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.backgroundDColor.getColor()))
        self.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.foregroundDColor.getColor()))
        
        # And disconnect signal itself.
        self.disconnect(self.focusInHandler)
        
        return False
    
gobject.type_register(SearchEntry)
