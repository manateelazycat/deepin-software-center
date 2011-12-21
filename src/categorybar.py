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

class CategoryBar(object):
    '''Category bar to list software.'''
	
    def __init__(self, categoryList, getCategoryNumCallback, func):
        '''Init for category bar.'''
        # Init.
        self.getCategoryNumCallback = getCategoryNumCallback
        self.box = gtk.VBox()
        self.callback = func
        self.paddingTop = 5
        self.paddingBottom = 5
        self.paddingLeft = 20
        self.paddingX = 10
        (self.categoryName, _) = categoryList[0]
        self.categoryId = 0
        
        # Create category icon.
        for (index, (categoryName, categoryIcon)) in enumerate(categoryList):
            icon = self.createCategoryIcon(categoryName, "category/" + categoryIcon, index)
            self.box.pack_start(icon)
        
        # Show.
        self.box.show_all()
        
    def createCategoryIcon(self, categoryName, iconPath, categoryId):
        '''Create category icon.'''
        # Create icon.
        eventButton = gtk.Button()
        eventButton.connect("button-press-event", lambda widget, event: self.callback(categoryName, categoryId))
        sideButtonSetBackground(
            eventButton,
            categoryName, 
            iconPath,
            "category/sidebar_normal.png",
            "category/sidebar_hover.png",
            "category/sidebar_press.png",
            self.getCategoryNumCallback,
            categoryId,
            self.getCategoryId
            )
        
        return eventButton

    def getCategoryId(self):
        '''Get page id.'''
        return self.categoryId
    
