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
from utils import *
import gtk
import utils

class NavigateBar(object):
    '''Interface for navigate bar.'''
	
    def __init__(self):
        '''Init for navigate bar.'''
        # Init.
        self.getUpgradableNumCallback = None
        self.selectPageCallback = None
        self.getRunningNumCallback = None
        self.iconPadding = 8
        self.animationFrames = 8
        self.updateAnimationCount = 0
        self.downloadAnimationCount = 0
        
        self.pageId = PAGE_RECOMMEND
        
        self.box = gtk.HBox()
        
        self.logoIcon = self.createLogoIcon()
        self.logoAlign = gtk.Alignment()
        self.logoAlign.set_padding(10, 0, 40, 0)
        self.logoAlign.add(self.logoIcon)
        self.box.pack_start(self.logoAlign, False, False)

        self.navBox = gtk.HBox()
        self.navAlign = gtk.Alignment()
        self.navAlign.set(0.3, 0.5, 0.0, 0.0)
        self.navAlign.set_padding(0, 0, 0, 120)
        self.navAlign.add(self.navBox)
        self.box.pack_start(self.navAlign, True, True)
        
        self.recommendIcon = self.createNavIcon(
            __("Nav Recommend"),
            "navigate/nav_recommend.png", 
            PAGE_RECOMMEND)
        self.navBox.pack_start(self.recommendIcon, False, False, self.iconPadding)
        
        self.repositoryIcon = self.createNavIcon(
            __("Nav Repository"),
            "navigate/nav_repo.png", 
            PAGE_REPO)
        self.navBox.pack_start(self.repositoryIcon, False, False, self.iconPadding)
        
        self.updateIcon = self.createUpdateIcon(
            __("Nav Update"),
            "navigate/nav_update.png", 
            PAGE_UPGRADE,
            self.getUpgradableNum)
        self.navBox.pack_start(self.updateIcon, False, False, self.iconPadding)
        
        self.uninstallIcon = self.createNavIcon(
            __("Nav Uninstall"),
            "navigate/nav_uninstall.png", 
            PAGE_UNINSTALL)
        self.navBox.pack_start(self.uninstallIcon, False, False, self.iconPadding)

        self.downloadIcon = self.createUpdateIcon(
            __("Nav Download Manage"),
            "navigate/nav_download.png", 
            PAGE_DOWNLOAD_MANAGE, 
            self.getRunningNum)
        self.navBox.pack_start(self.downloadIcon, False, False, self.iconPadding)
        
        self.box.show_all()

    def createLogoIcon(self):
        '''Create navigate icon.'''
        eventBox = gtk.EventBox()
        eventBox.set_visible_window(False)
        navBox = gtk.VBox()
        navImage = gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file(
                "../icon/logo/%s/logo.png" % (getDefaultLanguage())))
        navBox.pack_start(navImage, False)
        eventBox.add(navBox)
        eventBox.show_all()
        
        return eventBox
    
    def createUpdateIcon(self, iconName, iconPath, pageId, callback):
        '''Create navigate icon.'''
        eventButton = gtk.Button()
        eventButton.connect(
            "button-press-event", 
            lambda w, e: self.selectPage(pageId))
        updateButtonSetBackground(
            eventButton,
            iconName, iconPath,
            "navigate/menu_hover.png",
            "navigate/menu_press.png",
            pageId,
            self.getPageId,
            callback
            )
        
        box = gtk.VBox()
        
        label = gtk.Label()
        label.set_markup("<span foreground='%s'>%s</span>" % (
                appTheme.getDynamicColor("navigateText").getColor(),
                iconName))
        labelAlign = gtk.Alignment()
        labelAlign.set(0.5, 1.0, 0.0, 0.0)
        labelAlign.add(label)
        box.pack_start(labelAlign)
        
        eventButton.add(box)
        
        return eventButton
    
    def createNavIcon(self, iconName, iconPath, pageId):
        '''Create navigate icon.'''
        eventButton = gtk.Button()
        eventButton.connect(
            "button-press-event", 
            lambda w, e: self.selectPage(pageId))
        navButtonSetBackground(
            eventButton,
            iconName, 
            iconPath,
            "navigate/menu_hover.png",
            "navigate/menu_press.png",
            pageId,
            self.getPageId
            )
        
        box = gtk.VBox()
        
        label = gtk.Label()
        label.set_markup("<span foreground='%s'>%s</span>" % (
                appTheme.getDynamicColor("navigateText").getColor(),
                iconName))
        labelAlign = gtk.Alignment()
        labelAlign.set(0.5, 1.0, 0.0, 0.0)
        labelAlign.add(label)
        box.pack_start(labelAlign)
        
        eventButton.add(box)
        
        return eventButton
    
    def getPageId(self):
        '''Get page id.'''
        return self.pageId
    
    def selectPage(self, pageId):
        '''Select page.'''
        if self.selectPageCallback != None:
            self.selectPageCallback(pageId)
    
    def getUpgradableNum(self):
        '''Get upgradable number.'''
        if self.getUpgradableNumCallback == None:
            return 0
        else:
            return self.getUpgradableNumCallback()
        
    def getRunningNum(self):
        '''Get running number.'''
        if self.getRunningNumCallback == None:
            return 0
        else:
            return self.getRunningNumCallback()
        
    def setSelectPageCallback(self, callback):
        '''Set select page callback.'''
        self.selectPageCallback = callback    
    
    def setUpgradableNumCallback(self, callback):
        '''Set upgradable number callback.'''
        self.getUpgradableNumCallback = callback
        
    def setRunningNumCallback(self, callback):
        '''Set running number callback.'''
        self.getRunningNumCallback = callback
    
    
#  LocalWords: createNavIcon iconPadding
