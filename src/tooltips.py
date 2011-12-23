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
import glib
import gtk

class Tooltips(object):
    '''Tooltips.'''
    
    def __init__(self, window, widget):
        '''Init for tooltips.'''
        # Init.
        self.width = 300
        self.height = 24
        self.paddingX = 10
        self.startTimes = 10
        self.endTimes = 60
        self.times = 70
        self.interval = 80     # in milliseconds
        self.ticker = self.times
        
        # Create tooltips window.
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(True)
        self.window.set_transient_for(window.get_toplevel())
        self.window.set_opacity(0.9)
        self.window.set_property("accept-focus", False)
        self.window.set_size_request(-1, self.height)
        
        # Create tooltips label.
        self.label = gtk.Label()
        self.label.set_single_line_mode(True) # just one line
        self.align = gtk.Alignment()
        self.align.set(0.5, 0.5, 0.0, 0.0)
        self.align.set_padding(0, 0, self.paddingX, self.paddingX)
        self.align.add(self.label)
        self.window.add(self.align)
        
        # Update position.
        self.updatePosition(widget)
        
        # Add signal handler.
        window.connect("size-allocate", lambda w, e: self.updatePosition(widget))
        window.connect("configure-event", lambda w, e: self.updatePosition(widget))
        self.window.connect("expose-event", self.show)
        
    def start(self, message):
        '''Start.'''
        if self.ticker >= self.times:
            glib.timeout_add(self.interval, self.redraw)
            
        self.ticker = 0
        self.label.set_markup("<span foreground='%s' size='%s'>%s</span>" % (
                appTheme.getDynamicColor("tooltipForeground").getColor(),
                LABEL_FONT_MEDIUM_SIZE, 
                message))
        
    def redraw(self):
        '''Redraw.'''
        # Hide tooltips when ticker reach times.
        if self.ticker >= self.times:
            self.window.hide_all()
            
            return False
        # Or show animation.
        else:
            self.ticker += 1
            self.window.queue_draw()
            self.window.show_all()
            
            return True
        
    def show(self, widget, event):
        '''Show'''
        # Draw background.
        rect = widget.allocation
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*colorHexToCairo(appTheme.getDynamicColor("tooltipBackground").getColor()))
        cr.rectangle(0, 0, rect.width, rect.height)
        cr.fill()
        
        # Change opacity with ticker.
        if self.ticker <= self.startTimes:
            self.window.set_opacity(self.ticker * 0.1)
        elif self.ticker <= self.endTimes:
            self.window.set_opacity(1)
        else:
            self.window.set_opacity((self.times - self.ticker) * 0.1)
            
        # Update window position.
        (width, _) = self.label.get_layout().get_pixel_size()
        self.window.move(self.x - width / 2 - self.paddingX, self.y)
        
        # Expose recursively.
        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)
            
        return True
        
    def updatePosition(self, widget):
        '''Update position.'''
        # Get coordinate.
        (wx, wy) = widget.window.get_origin()
        rect = widget.get_allocation()
        (ww, wh) = (rect.width, rect.height)
        
        # Update coordinate.
        self.x = wx + ww / 2
        self.y = wy - self.height
        
        # Redraw.
        self.window.queue_draw()
            
