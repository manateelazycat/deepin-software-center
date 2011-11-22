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

from lang import __
from theme import *
from draw import *
import gtk
import pygtk
import utils
pygtk.require('2.0')

class SubCategorybar(object):
    '''Sub category bar.'''
	
    def __init__(self, category, categoryList, func):
        '''Init for sub category bar.'''
        # Init.
        self.frame = gtk.EventBox()
        eventBoxSetBackground(
            self.frame,
            True, False,
            appTheme.getDynamicPixbuf("subcategory/background.png")
            )
        self.box = gtk.VBox()
        self.paddingX = 10
        self.paddingY = 5
        self.defaultColumns = 11
        (labelWidth, _) = gtk.Label("标准宽度").get_layout().get_pixel_size()
        self.labelWidth = labelWidth
        self.categoryList = categoryList
        self.callback = func
        self.category = category
        self.cacheWidth = 0
        self.redrawCount = 0
        
        # Show.
        self.frame.add(self.box)
        self.showSubCategorybar()
        self.box.connect_after("size-allocate", lambda widget, rect: self.onSizeAllocate(rect.width))
        
    def onSizeAllocate(self, width):
        '''Call when signal 'size-allocate' emit.'''
        # When first time redraw, remove child and reset width. 
        if self.redrawCount == 0:
            self.redrawCount = self.redrawCount + 1
            utils.containerRemoveAll(self.box)
            self.box.set_size_request(1, -1)
        # When second time redraw, redraw with new width allocated.
        elif self.redrawCount == 1:
            self.redrawCount = self.redrawCount + 1
            self.showSubCategorybar(width)
        # When third time, reset redraw count, stop redraw.
        else:
            self.redrawCount = 0
        
    def showSubCategorybar(self, boxWidth=0):
        '''Show sub category bar.'''
        # Use default columns if boxWidth is equal 0.
        if boxWidth == 0:
            columns = self.defaultColumns
        # Otherwise calculate columns.
        elif boxWidth > 0:
            columns = int (boxWidth / (self.labelWidth + self.paddingX * 2))
        
        # Add sub-category label.
        vboxs = []
        for index, subCategory in enumerate(self.categoryList):
            boxIndex = index / columns
            if len(vboxs) < boxIndex + 1:
                hbox = gtk.HBox()
                self.box.pack_start(hbox, False, False, self.paddingY)
                vboxs.append(hbox)

            categoryBox = self.createSubCategoryLabel(subCategory)
            vboxs[boxIndex].pack_start(categoryBox, False, False, self.paddingX)
            
        # Show.
        self.box.show_all()

    def updateSubCategorybar(self, category, categoryList):
        '''Update sub category bar.'''
        # Update value.
        self.category = category
        self.categoryList = categoryList
        
        # Remove child widgets first.
        utils.containerRemoveAll(self.box)
        
        # Show sub-category bar.
        rect = self.box.get_allocation()
        self.showSubCategorybar(rect.width)
    
    def createSubCategoryLabel(self, subCategory):
        '''Create sub category label.'''
        # Create sub-category label.
        categoryBox = gtk.Button()
        fontButtonSetBackground(
            categoryBox,
            self.labelWidth, -1,
            subCategory, "#BBBB00", "#BB00BB", "#00BBBB",
            )
        
        # Register button-press-event to callback.
        categoryBox.connect("button-press-event", 
                            lambda widget, event: self.callback(self.category, subCategory))

        return categoryBox

#  LocalWords:  boxWidth BBBB
