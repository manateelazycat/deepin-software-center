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
import gtk
import pygtk
import utils
pygtk.require('2.0')

class NavigateBar:
    '''Interface for navigate bar.'''
	
    def __init__(self):
        '''Init for navigate bar.'''
        # Init.
        self.iconPadding = 8
        
        self.pageId = PAGE_RECOMMEND
        
        self.box = gtk.HBox()
        
        self.logoIcon = self.createLogoIcon()
        self.logoAlign = gtk.Alignment()
        self.logoAlign.set_padding(0, 0, 30, 10)
        self.logoAlign.add(self.logoIcon)
        self.box.pack_start(self.logoAlign, False, False)

        self.navBox = gtk.HBox()
        self.navAlign = gtk.Alignment()
        self.navAlign.set(0.5, 0.5, 0.0, 0.0)
        self.navAlign.set_padding(0, 0, 0, 60)
        self.navAlign.add(self.navBox)
        self.box.pack_start(self.navAlign, True, True)
        
        self.recommendIcon      = self.createNavIcon("精选推荐", "./icons/navigate/nav_recommend.png", PAGE_RECOMMEND)
        self.navBox.pack_start(self.recommendIcon, False, False, self.iconPadding)
        
        self.repositoryIcon     = self.createNavIcon("软件仓库", "./icons/navigate/nav_repo.png", PAGE_REPO)
        self.navBox.pack_start(self.repositoryIcon, False, False, self.iconPadding)
        
        self.updateIcon         = self.createNavIcon("软件更新", "./icons/navigate/nav_update.png", PAGE_UPGRADE)
        self.navBox.pack_start(self.updateIcon, False, False, self.iconPadding)
        
        self.uninstallIcon      = self.createNavIcon("软件卸载", "./icons/navigate/nav_uninstall.png", PAGE_UNINSTALL)
        self.navBox.pack_start(self.uninstallIcon, False, False, self.iconPadding)
        
        self.communityIcon      = self.createNavIcon("社区分享", "./icons/navigate/nav_hi.png", PAGE_COMMUNITY)
        self.navBox.pack_start(self.communityIcon, False, False, self.iconPadding)
        
        # self.moreIcon           = self.createNavIcon("更多精彩", "./icons/navigate/nav_more.png", PAGE_MORE)
        # self.navBox.pack_start(self.moreIcon, False, False, self.iconPadding)
        
        self.box.show_all()

    def createLogoIcon(self):
        '''Create navigate icon.'''
        eventBox = gtk.EventBox()
        eventBox.set_visible_window(False)
        navBox = gtk.VBox()
        navImage = gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file("./icons/navigate/logo.png"))
        navBox.pack_start(navImage, False)
        eventBox.add(navBox)
        eventBox.show_all()
        
        return eventBox
    
    def createNavIcon(self, iconName, iconPath, pageId):
        '''Create navigate icon.'''
        eventButton = gtk.Button()
        navButtonSetBackground(
            eventButton,
            iconName, iconPath,
            "./icons/navigate/menu_hover.png",
            "./icons/navigate/menu_press.png",
            pageId,
            self.getPageId
            )
        
        return eventButton
    
    def getPageId(self):
        '''Get page id.'''
        return self.pageId
    
