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
from theme import *
import gtk
import pygtk
import utils
import os
pygtk.require('2.0')

class ThemeSelect:
    '''Theme select.'''
    def __init__(self, widget, changeThemeCallback):
        '''Init theme select.'''
        # Init.
        self.index = 0
        self.dirnames = []
        self.changeThemeCallback = changeThemeCallback
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(False)
        self.window.set_transient_for(widget.get_toplevel())
        self.window.set_opacity(0.95)
        
        self.mainBox = gtk.VBox()
        self.window.add(self.mainBox)
        
        self.titleEventBox = gtk.EventBox()
        self.titleEventBox.set_visible_window(False)
        self.mainBox.pack_start(self.titleEventBox, False, False)
        
        self.titleAlign = gtk.Alignment()
        dLabel = DynamicSimpleLabel(
            self.titleAlign,
            "更换皮肤",
            appTheme.getDynamicColor("themeSelectTitleText"),
            LABEL_FONT_LARGE_SIZE,
            )
        self.titleLabel = dLabel.getLabel()
        alignY = 10
        self.titleAlign.set(0.0, 0.0, 1.0, 1.0)
        self.titleAlign.set_padding(alignY, alignY, 0, 0)
        self.titleAlign.add(self.titleLabel)
        self.titleEventBox.add(self.titleAlign)
        
        self.themeIconBox = gtk.VBox()
        self.themeIconAlign = gtk.Alignment()
        self.themeIconAlign.set(0.5, 0.5, 0.0, 0.0)
        self.themeIconAlign.add(self.themeIconBox)
        self.mainBox.pack_start(self.themeIconAlign)
        
        # Set size request.
        self.window.set_size_request(THEME_WINDOW_WIDTH, THEME_WINDOW_HEIGHT)
        
        # Set shape.
        self.window.connect("size-allocate", lambda w, a: updateShape(w, a, RADIUS))
        
        # Draw.
        drawThemeSelectWindow(
            self.window,
            appTheme.getDynamicPixbuf("skin/background.png"),
            appTheme.getDynamicColor("frame"),
            appTheme.getDynamicAlphaColor("frameLigtht"),
            )
        
        # Hide window if user click on main window.
        widget.connect("button-press-event", lambda w, e: self.hide())
        
    def show(self, x, y):
        '''Show.'''
        # Scan theme directory.
        containerRemoveAll(self.themeIconBox)
        dirs = os.listdir("../theme/")
        self.dirnames = dirs
        boxs = map (lambda n: gtk.HBox(), range(0, len(dirs) / 3 + len(dirs) % 3))
        boxIndex = 0
        for (index, dirname) in enumerate(dirs):
            box = boxs[boxIndex / 3]
            box.pack_start(ThemeSlide(dirname, index, self.setIndex, self.getIndex).align)
            self.themeIconBox.pack_start(box, False, False)
            boxIndex += 1

        # Show.
        self.window.show_all()
        self.window.move(x, y)
        
    def hide(self):
        '''Hide.'''
        self.window.hide_all()
        
    def setIndex(self, index):
        '''Set index.'''
        self.index = index
        self.changeThemeCallback(self.dirnames[index])
    
    def getIndex(self):
        '''Get index.'''
        return index

class ThemeSlide:
    '''Theme slide.'''
    
    PADDING_X = 10
    PADDING_Y = 5
	
    def __init__(self, dirname, index, setIndexCallback, getIndexCallback):
        '''Init theme slide.'''
        # Init.
        self.dirname = dirname
        self.pixbuf = gtk.gdk.pixbuf_new_from_file("../theme/%s/image/skin/icon.png" % (self.dirname))
        self.iconName = evalFile("../theme/%s/name.txt" % dirname)[getDefaultLanguage()]
        
        # Build widget.
        self.box = gtk.VBox()
        self.align = gtk.Alignment()
        self.align.set(0.5, 0.5, 0.0, 0.0)
        self.align.set_padding(self.PADDING_Y, self.PADDING_Y, self.PADDING_X, self.PADDING_X)
        self.iconBox = gtk.EventBox()
        self.iconBox.set_visible_window(False)
        self.iconBox.set_size_request(self.pixbuf.get_width(), self.pixbuf.get_height())
        self.iconBox.connect("button-press-event", lambda w, e: setIndexCallback(index))
        drawThemeIcon(self.iconBox, self.pixbuf, index, getIndexCallback)
        
        self.iconNameBox = gtk.EventBox()
        self.iconNameBox.set_visible_window(False)
        dLabel = DynamicSimpleLabel(
            self.iconNameBox,
            self.iconName,
            appTheme.getDynamicColor("themeIconName"),
            LABEL_FONT_SIZE,
            )
        self.iconNameLabel = dLabel.getLabel()
        self.iconNameBox.add(self.iconNameLabel)
        
        self.box.pack_start(self.iconBox, False, False)
        self.box.pack_start(self.iconNameBox, False, False)
        self.align.add(self.box)
        
