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

from draw import *
import gobject
import gtk
import pygtk
pygtk.require('2.0')

class Progressbar():
    '''Progress bar.'''
	
    def __init__(self, width,
                 bgLeftImg, bgMiddleImg, bgRightImg,
                 fgLeftImg, fgMiddleImg, fgRightImg):
        '''Init for progress bar.'''
        self.box = gtk.HBox()
        
        self.bgLeftPixbuf = gtk.gdk.pixbuf_new_from_file(bgLeftImg)
        self.bgMiddlePixbuf = gtk.gdk.pixbuf_new_from_file(bgMiddleImg)
        self.bgRightPixbuf = gtk.gdk.pixbuf_new_from_file(bgRightImg)
        self.fgLeftPixbuf = gtk.gdk.pixbuf_new_from_file(fgLeftImg)
        self.fgMiddlePixbuf = gtk.gdk.pixbuf_new_from_file(fgMiddleImg)
        self.fgRightPixbuf = gtk.gdk.pixbuf_new_from_file(fgRightImg)
        
        self.width = width
        self.fgBorderWidth = self.fgLeftPixbuf.get_width()
        self.bgBorderWidth = self.bgLeftPixbuf.get_width()
        self.fgHeight = self.fgLeftPixbuf.get_height()
        self.bgHeight = self.bgLeftPixbuf.get_height()
        self.progressWidth = self.width - self.bgBorderWidth * 2
        
        self.leftImage = gtk.Image()
        self.box.pack_start(self.leftImage, False, False)
        
        self.middleImage = gtk.Image()
        self.middleImage.set_size_request(self.progressWidth, self.bgHeight)
        self.box.pack_start(self.middleImage, False, False)
        
        self.rightImage = gtk.Image()
        self.box.pack_start(self.rightImage, False, False)
        
        self.progress = 0
        self.setProgress(self.progress)
        
        self.box.show_all()
        
    def setLeftImage(self, progress):
        '''Get left image.'''
        if progress == 0:
            self.leftImage.set_from_pixbuf(self.bgLeftPixbuf)
        else:
            bgLeftPixbuf = self.bgLeftPixbuf.copy()
            self.fgLeftPixbuf.copy_area(
                0, 0, self.fgBorderWidth, self.fgHeight,
                bgLeftPixbuf, 
                (self.bgBorderWidth - self.fgBorderWidth),
                (self.bgHeight - self.fgHeight) / 2)
            
            self.leftImage.set_from_pixbuf(bgLeftPixbuf)
    
    def setRightImage(self, progress):
        '''Get right image.'''
        if progress == 100:
            bgRightPixbuf = self.bgRightPixbuf.copy()
            self.fgRightPixbuf.copy_area(
                0, 0, self.fgBorderWidth, self.fgHeight,
                bgRightPixbuf, 
                0,
                (self.bgHeight - self.fgHeight) / 2)
            
            self.rightImage.set_from_pixbuf(bgRightPixbuf)
        else:
            self.rightImage.set_from_pixbuf(self.bgRightPixbuf)
        
    def setProgress(self, progress):
        '''Set progress.'''
        # Init.
        self.setLeftImage(progress)
        self.setRightImage(progress)
        
        fgWidth = int(self.progressWidth * progress / 100)        
        middlePixbuf = self.bgMiddlePixbuf.scale_simple(self.progressWidth, self.bgHeight, gtk.gdk.INTERP_BILINEAR)
        
        if fgWidth != 0:
            fgMiddlePixbuf = self.fgMiddlePixbuf.scale_simple(fgWidth, self.fgHeight, gtk.gdk.INTERP_BILINEAR)
            fgMiddlePixbuf.copy_area(0, 0, fgWidth, self.fgHeight, middlePixbuf, 0, (self.bgHeight - self.fgHeight) / 2)
            
            fgRightPixbuf = self.fgRightPixbuf.scale_simple(self.fgBorderWidth, self.fgHeight, gtk.gdk.INTERP_BILINEAR)
            if fgWidth + self.fgBorderWidth <= self.progressWidth:
                fgRightPixbuf.copy_area(0, 0, self.fgBorderWidth, self.fgHeight, 
                                        middlePixbuf, fgWidth, (self.bgHeight - self.fgHeight) / 2)
        
        self.middleImage.set_from_pixbuf(middlePixbuf)
        
        self.box.show_all()
