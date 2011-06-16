#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
# 
# Copyright (C) 2011 Andy Stewart, all rights reserved.
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
import glib
import gtk
import pygtk
import recommendView
import utils
pygtk.require('2.0')

class RecommendPage:
    '''Interface for recommend page.'''
	
    def __init__(self, repoCache, switchStatus, downloadQueue, entryDetailCallback, selectCategoryCallback):
        '''Init for recommend page.'''
        # Init.
        self.box = gtk.VBox()
        
        # Add slide bar.
        self.slidebar = SlideBar()
        
        # Add recommend view.
        self.recommendView = recommendView.RecommendView(
            repoCache, 
            switchStatus, 
            downloadQueue, 
            entryDetailCallback,
            selectCategoryCallback)
        self.appBox = gtk.VBox()
        self.appBox.pack_start(self.recommendView.box, False, False)

        self.bodyBox = gtk.HBox()
        self.bodyBox.pack_start(self.appBox, False, False)
        self.bodyAlign = gtk.Alignment()
        self.bodyAlign.set(0.5, 0.0, 0.0, 0.0)
        self.bodyAlign.add(self.bodyBox)
        
        self.contentBox = gtk.VBox()
        self.contentBox.pack_start(self.slidebar.align, False, False)
        self.contentBox.pack_start(self.bodyAlign, False, False)
        self.box.pack_start(self.contentBox)
        
        self.eventbox = gtk.EventBox()
        self.eventbox.add(self.box)
        self.eventbox.connect("expose-event", lambda w, e: drawBackground(w, e, "#FFFFFF"))
        
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        utils.addInScrolledWindow(self.scrolledwindow, self.eventbox)
        
        self.scrolledwindow.show_all()
        
class SlideBar:
    '''Slide bar'''
	
    def __init__(self):
        '''Init for slide bar.'''
        # Init.
        self.images = ["chrome.png",
                       "birds.png",
                       "twitter.png"]
        self.names = ["谷歌浏览器",
                      "愤怒的小鸟",
                      "推特"]
        self.padding = 10
        self.imageWidth = 600
        self.imageHeight = 300
        self.times = 20
        self.interval = 400 / self.times
        self.smallImagePaddingY = 10

        self.imageDir = "./images/"
        firstPath = self.images[0]
        
        self.sourcePath = ""
        self.targetPath = self.imageDir + self.images[0]
        self.targetName = self.names[0]
        self.sourceImage = gtk.gdk.pixbuf_new_from_file_at_size(
            self.imageDir + firstPath, 
            self.imageWidth, 
            self.imageHeight)
        secondPath = self.images[1]
        self.targetImage = gtk.gdk.pixbuf_new_from_file_at_size(
            self.imageDir + secondPath,
            self.imageWidth,
            self.imageHeight)
        self.stop = True
        self.moveUp = True
        self.ticker = self.times
        self.index = 0
        self.alphaInterval = 1
        
        self.align = gtk.Alignment()
        self.align.set(0.5, 0.5, 0.0, 0.0)
        self.align.set_padding(self.padding, self.padding, self.padding, self.padding)
        
        # Add slide label.
        self.labelBox = gtk.VBox()
        for (index, _) in enumerate(self.images):
            self.createSlideLabel(index)
        
        # Add slide area.
        self.drawingArea = gtk.DrawingArea()
        self.drawingArea.set_size_request(self.imageWidth, self.imageHeight)
        self.drawingArea.connect("expose_event", self.exposeBigArea)
        self.drawingArea.queue_draw()
        
        # Connect widgets.
        self.imageBox = gtk.VBox()
        self.imageBox.pack_start(self.drawingArea, False, False)
        
        self.box = gtk.HBox()
        self.box.pack_start(self.imageBox, False, False)
        self.box.pack_start(self.labelBox)
        
        self.alignBox = gtk.VBox()
        self.alignBox.pack_start(self.box, False, False)
        
        self.align.add(self.alignBox)
        
    def createSlideLabel(self, index):
        '''Create slide label.'''
        imagePath = self.imageDir + self.images[index]
        image = gtk.DrawingArea()
        image.set_size_request(self.imageWidth / 3, 
                               (self.imageHeight - self.smallImagePaddingY * 2) / 3)
        image.connect("expose_event", lambda w, e: self.exposeSmallArea(w, e, imagePath))
        image.queue_draw()
        
        imageAlign = gtk.Alignment()
        if index == 1:
            imagePaddingY = self.smallImagePaddingY
        else:
            imagePaddingY = 0
        imagePaddingLeft = 10
        imageAlign.set_padding(imagePaddingY, imagePaddingY, imagePaddingLeft, 0)
        imageAlign.add(image)
        labelBox = gtk.EventBox()
        labelBox.add(imageAlign)
        labelBox.connect("enter-notify-event", lambda widget, event: self.start(index))
        labelBox.connect("expose-event", lambda w, e: drawBackground(w, e, "#FFFFFF"))
        self.labelBox.pack_start(labelBox, True, True)
        
    def exposeSmallArea(self, drawArea, event, imgPath):
        '''Expose small area.'''
        # Draw image.
        width, height = drawArea.allocation.width, drawArea.allocation.height
        pixbuf = gtk.gdk.pixbuf_new_from_file(imgPath).scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
        cr = drawArea.window.cairo_create()
        cr.set_source_pixbuf(pixbuf, 0, 0)
        
        interval = 0.5 / self.times
        if self.targetPath == imgPath:
            cr.paint_with_alpha(0.5 + self.ticker * interval)
        elif self.sourcePath == imgPath:
            cr.paint_with_alpha(1.0 - self.ticker * interval)
        else:
            cr.paint_with_alpha(0.5)
        
    def exposeBigArea(self, drawArea, event):
        '''Expose callback for the drawing area.'''
        bottomHeight = 50
        width, height = self.targetImage.get_width(), self.targetImage.get_height()

        # Draw background.
        cr = self.drawingArea.window.cairo_create()
        if self.ticker < self.times / 2:
            maskPixbuf = self.sourceImage.copy()
            
            targetPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height - bottomHeight)
            self.targetImage.copy_area(0, 0, width, height - bottomHeight, targetPixbuf, 0, 0)
            cr.set_source_pixbuf(targetPixbuf, 0, 0)
            cr.paint_with_alpha(self.ticker * self.alphaInterval)
            
            sourcePixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height - bottomHeight)
            self.sourceImage.copy_area(0, 0, width, height - bottomHeight, sourcePixbuf, 0, 0)
            cr.set_source_pixbuf(sourcePixbuf, 0, 0)
            cr.paint_with_alpha((self.times - self.ticker) * self.alphaInterval)
        elif self.ticker == self.times:
            maskPixbuf = self.targetImage.copy()
            
            targetPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height - bottomHeight)
            self.targetImage.copy_area(0, 0, width, height - bottomHeight, targetPixbuf, 0, 0)
            cr.set_source_pixbuf(targetPixbuf, 0, 0)
            cr.paint_with_alpha(1)
        else:
            maskPixbuf = self.targetImage.copy()
            
            sourcePixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height - bottomHeight)
            self.sourceImage.copy_area(0, 0, width, height - bottomHeight, sourcePixbuf, 0, 0)
            cr.set_source_pixbuf(sourcePixbuf, 0, 0)
            cr.paint_with_alpha((self.times - self.ticker) * self.alphaInterval)
            
            targetPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height - bottomHeight)
            self.targetImage.copy_area(0, 0, width, height - bottomHeight, targetPixbuf, 0, 0)
            cr.set_source_pixbuf(targetPixbuf, 0, 0)
            cr.paint_with_alpha(self.ticker * self.alphaInterval)

        # Draw mask.
        bottomPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, bottomHeight)
        maskPixbuf.copy_area(0, height - bottomHeight, width, bottomHeight, bottomPixbuf, 0, 0)
        
        cr.set_source_pixbuf(bottomPixbuf, 0, height - bottomHeight)
        cr.paint_with_alpha(0.5)
        
        # Draw information.
        fontSize = 24
        fontWidth = 4
        nameAlignX = 20
        cr.set_line_width(fontWidth)
        drawFont(cr, self.targetName, fontSize, "#FFFFFF", nameAlignX, height - fontSize / 2- fontWidth)
        
        # Draw star.
        starLevel = 10
        starAlignX = 150
        starSize = 24
        for i in range(0, 5):
            starPixbuf = utils.getStarPixbuf(i + 1, starLevel, starSize)
            cr.set_source_pixbuf(starPixbuf, 
                                 starAlignX + i * starSize,
                                 height - (bottomHeight - starSize) / 2 - starSize)
            cr.paint()
            
        # Draw button.
        buttonAlignX = width - 100
        buttonPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/cell/search_normal.png")
        buttonHeight = buttonPixbuf.get_height()
        buttonWidth = buttonPixbuf.get_width()
        cr.set_source_pixbuf(buttonPixbuf, 
                             buttonAlignX, 
                             height - (bottomHeight - buttonHeight) / 2 - buttonHeight)
        cr.paint()

        # Draw button label.
        buttonFontSize = 16
        drawFont(cr, "安装", buttonFontSize, "#FFFFFF", 
                 buttonAlignX + buttonFontSize,
                 utils.getFontYCoordinate(height - (bottomHeight - buttonHeight) / 2 - buttonHeight - 1,
                                          buttonHeight,
                                          buttonFontSize))

    def start(self, index):
        '''Start show slide.'''
        # Stop if index same as current one.
        if self.index == index:
            return
        # Just start slide when stop.
        elif self.stop:
            # Get path.
            self.sourcePath = self.imageDir + self.images[self.index]
            self.targetPath = self.imageDir + self.images[index]
            
            # Set name.
            self.targetName = self.names[index]
            
            # Get new image.
            self.sourceImage = gtk.gdk.pixbuf_new_from_file_at_size(
                self.sourcePath,
                self.imageWidth,
                self.imageHeight)
            self.targetImage = gtk.gdk.pixbuf_new_from_file_at_size(
                self.targetPath,
                self.imageWidth,
                self.imageHeight)
            
            # Get move direction with given index.
            if self.index < index:
                self.moveUp = True
            else:
                self.moveUp = False
                
            # Reset.
            self.stop = False
            self.index = index
            self.ticker = 0
            self.alphaInterval = 1.0 / self.times
            
            # Start slide.
            glib.timeout_add(self.interval, self.slide)

    def slide(self):
        '''Slide.'''
        # Update ticker.
        self.ticker = self.ticker + 1
        
        # Redraw.
        self.drawingArea.queue_draw() # redraw big logo
        self.labelBox.queue_draw()    # redraw small logo
        
        # Stop slide if ticker reach times.
        if self.ticker == self.times:
            self.stop = True
            return False
        else:
            return True

