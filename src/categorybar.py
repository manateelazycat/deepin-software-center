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
import gtk
import pygtk
import utils
pygtk.require('2.0')

class CategoryBar:
    '''Category bar to list software.'''
	
    def __init__(self, categoryList, func):
        '''Init for category bar.'''
        # Init.
        self.box = gtk.VBox()
        self.callback = func
        self.paddingTop = 5
        self.paddingBottom = 5
        self.paddingLeft = 20
        self.paddingX = 10
        self.categoryId = 0
        
        # Create category icon.
        for (index, (categoryName, categoryIcon)) in enumerate(categoryList):
            icon = self.createCategoryIcon(categoryName, "./icons/category/" + categoryIcon, index)
            self.box.pack_start(icon)
        
        # Show.
        self.box.show_all()
        
    def createCategoryIcon(self, iconName, iconPath, categoryId):
        '''Create category icon.'''
        # Create icon.
        eventButton = gtk.Button()
        eventButton.connect("button-press-event", lambda widget, event: self.callback(iconName, categoryId))
        sideButtonSetBackground(
            eventButton,
            iconName, iconPath,
            "./icons/category/sidebar_normal.png",
            "./icons/category/sidebar_hover.png",
            "./icons/category/sidebar_press.png",
            categoryId,
            self.getCategoryId
            )
        
        return eventButton

    def getCategoryId(self):
        '''Get page id.'''
        return self.categoryId
    
