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
from theme import *
import gtk
import pango
import utils

class AppView(object):
    '''Application view.'''
	
    def __init__(self, appNum, pageId, isSearchPage=False):
        '''Init for application view.'''
        # Init.
        self.appNum = appNum
        self.pageIndex = 1      # default display first page
        self.defaultRows = 50
        self.maxPageIndex = None
        self.jumpButton = None
        self.itemIndex = -1
        self.pageSize = 5
        self.calculateMaxPageIndex()
        self.pageId = pageId
        self.isSearchPage = isSearchPage
        
        # Connect widget.
        self.box = gtk.VBox()
        self.eventbox = gtk.EventBox()
        self.eventbox.add(self.box)
        self.eventbox.connect("expose-event", lambda w, e: drawBackground(w, e, appTheme.getDynamicColor("background")))
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        drawVScrollbar(self.scrolledwindow)
        utils.addInScrolledWindow(self.scrolledwindow, self.eventbox)
        
        # Avoid eventbox wider than scroll view.
        self.eventbox.set_size_request(DEFAULT_WINDOW_WIDTH / 2, -1) 
        
    def calculateMaxPageIndex(self):
        '''Calculate max page index.'''
        if self.appNum % self.defaultRows == 0:
            self.maxPageIndex = self.appNum / self.defaultRows
        else:
            self.maxPageIndex = self.appNum / self.defaultRows + 1
        
    def getSelectItemIndex(self):
        '''Get select item index.'''
        return self.itemIndex
    
    def setSelectItemIndex(self, index):
        '''Set select index.'''
        self.itemIndex = index    
        self.box.queue_draw()

    def jumpPage(self, index):
        '''Jump to page'''
        if self.pageIndex != index:
            self.pageIndex = index
            self.itemIndex = -1
            self.show()
        
    def show(self, scrollToTop=True):
        '''Show application view.'''
        # Remove child widgets first.
        utils.containerRemoveAll(self.box)
        self.itemDict.clear()
        
        # If i don't re-connect self.eventbox and self.box,
        # update view will show nothing.
        # I still can't understand why?
        # Maybe this is bug of GtkEventBox?
        utils.containerRemoveAll(self.eventbox)
        self.eventbox.add(self.box)
        
        if self.appNum != 0:
            # Get application list.
            appList = self.getListFunc((self.pageIndex - 1) * self.defaultRows,
                                       min(self.pageIndex * self.defaultRows, self.appNum)
                                       )
            
            # Create application view.
            self.box.pack_start(self.createAppList(appList))
            
            # Create index view.
            indexbar = self.createIndexbar()
            if not indexbar == None:
                self.box.pack_start(indexbar)
                
            self.box.show_all()
            
            # Request vote data.
            self.fetchVoteCallback(
                self.pageId, 
                map (lambda appInfo: utils.getPkgName(appInfo.pkg), appList),
                self.isSearchPage)
            
        # Scroll ScrolledWindow to top after render.
        if scrollToTop:
            utils.scrollToTop(self.scrolledwindow)
        
    def createIndexbar(self):
        '''Create bottom bar.'''
        # Init.
        paddingX = 5
        paddingY = 10
            
        # Just render when application more than one page.
        if self.appNum > self.defaultRows * self.pageSize:
            # Create index box.
            box = gtk.HBox()
            align = gtk.Alignment()
            align.set(0.5, 1.0, 0.0, 0.0)
            align.set_padding(paddingY, paddingY, paddingX, paddingX)
            align.add(box)
            
            # Get start/end index.
            if self.pageIndex % self.pageSize == 0:
                (startIndex, endIndex) = (max(1, (self.pageIndex - 1) / self.pageSize * self.pageSize + 1),
                                          min(self.pageIndex + 1,
                                              self.maxPageIndex + 1))
            else:
                (startIndex, endIndex) = (int(self.pageIndex / self.pageSize) * self.pageSize + 1, 
                                          min((int(self.pageIndex / self.pageSize) + 1) * self.pageSize + 1,
                                              self.maxPageIndex + 1))
            
            # Don't add first icon if at first *page*.
            if startIndex != 1:
                # Add previous icon.
                prevButton = setHoverButton(
                    appTheme.getDynamicPixbuf("index/backward_normal.png"),
                    appTheme.getDynamicPixbuf("index/backward_hover.png"),
                    )
                prevButton.connect("button-press-event", 
                                lambda widget, event: self.jumpPage(max(1, (self.pageIndex - 1) / self.pageSize * self.pageSize)))
                prevAlign = gtk.Alignment()
                prevAlign.set(0.5, 0.5, 0.0, 0.0)
                prevAlign.add(prevButton)
                box.pack_start(prevAlign, False, False, paddingX)
                
                firstBox = self.createNumIcon(1)
                firstLabel = gtk.Label()
                firstLabel.set_markup("<span foreground='%s' size='%s'> ... </span>" % (
                        appTheme.getDynamicColor("index").getColor(),
                        LABEL_FONT_MEDIUM_SIZE))
                box.pack_start(firstBox)
                box.pack_start(firstLabel)
            
            # Add index number icon.
            for i in range(startIndex, endIndex):
                box.pack_start(self.createNumIcon(i), False, False, paddingX)
            
            # Don't add last icon if at last *page*.
            if endIndex - 1 != self.maxPageIndex:
                lastBox = self.createNumIcon(self.maxPageIndex)
                lastLabel = gtk.Label()
                lastLabel.set_markup("<span foreground='%s' size='%s'> ... </span>" % (
                        appTheme.getDynamicColor("index").getColor(),
                        LABEL_FONT_MEDIUM_SIZE))
                box.pack_start(lastLabel)
                box.pack_start(lastBox)
                
                # Add next icon.
                nextButton = setHoverButton(
                    appTheme.getDynamicPixbuf("index/forward_normal.png"),
                    appTheme.getDynamicPixbuf("index/forward_hover.png"),
                    )
                nextButton.connect("button-press-event", 
                                   lambda widget, event: self.jumpPage(min(self.maxPageIndex, ((self.pageIndex - 1) / self.pageSize + 1) * self.pageSize + 1)))
                nextAlign = gtk.Alignment()
                nextAlign.set(0.5, 0.5, 0.0, 0.0)
                nextAlign.add(nextButton)
                box.pack_start(nextAlign, False, False, paddingX)
            
            # Add jump button.
            spinButton = gtk.SpinButton()
            spinButton.set_digits(0)
            spinButton.set_increments(1, self.defaultRows)
            spinButton.set_range(1, self.maxPageIndex)
            spinButton.set_value(self.pageIndex)
            self.jumpButton = spinButton
            
            # Add jump label.
            jumpBeforeLabel = gtk.Label()
            jumpBeforeLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_MEDIUM_SIZE, __("Jump To")))
            jumpAfterLabel = gtk.Label()
            jumpAfterLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_MEDIUM_SIZE, __("Page")))
            jumpButton = utils.newButtonWithoutPadding()
            jumpButton.connect("button-release-event", lambda widget, event: self.jumpPage(int(self.jumpButton.get_text())))
            drawButton(jumpButton, "confirm", "index", False, __("Jump"), BUTTON_FONT_SIZE_SMALL, "buttonFont")
            
            # Connect widget.
            box.pack_start(jumpBeforeLabel, False, False, paddingX)
            box.pack_start(spinButton, False, False, paddingX)
            box.pack_start(jumpAfterLabel, False, False, paddingX)
            box.pack_start(jumpButton, False, False, paddingX)
            
            return align
        elif self.appNum > self.defaultRows:
            # Init.
            box = gtk.HBox()
            align = gtk.Alignment()
            align.set(0.5, 1.0, 0.0, 0.0)
            align.set_padding(paddingY, paddingY, paddingX, paddingX)
            align.add(box)
            
            # Add index number icon.
            for i in range(1, self.maxPageIndex + 1):
                box.pack_start(self.createNumIcon(i), False, False, paddingX)
            
            return align
        else:
            return None
        
    def createNumIcon(self, index):
        '''Create number icon.'''
        numBox = setNumButton(
            self.pageIndex,
            index, 
            appTheme.getDynamicPixbuf("index/hover.png"),
            appTheme.getDynamicPixbuf("index/press.png")
            )
        numBox.connect("button-press-event", lambda widget, event: self.jumpPage(index))
        
        return numBox

    def switchToStatus(self, pkgName, appStatus, updateVote=False):
        '''Switch to downloading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.appInfo.status = appStatus
            appItem.initAdditionStatus()
            
        if updateVote:
            self.fetchVoteCallback(self.pageId, [pkgName], self.isSearchPage)

    def initNormalStatus(self, pkgName, isMarkDeleted, updateVote=False):
        '''Init normal status.'''
        if isMarkDeleted:
            self.switchToStatus(pkgName, APP_STATE_NORMAL, updateVote)
        else:
            self.switchToStatus(pkgName, APP_STATE_INSTALLED, updateVote)
            
    def updateDownloadingStatus(self, pkgName, progress, feedback):
        '''Update downloading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateDownloadingStatus(progress, feedback)
            
    def updateInstallingStatus(self, pkgName, progress, feedback):
        '''Update installing status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateInstallingStatus(progress, feedback)
            
    def updateUpgradingStatus(self, pkgName, progress, feedback):
        '''Update upgrading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateUpgradingStatus(progress, feedback)
            
    def updateUninstallingStatus(self, pkgName, progress, feedback):
        '''Update upgrading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateUninstallingStatus(progress, feedback)
            
    def updateVoteView(self, pkgName, starLevel, commentNum):
        '''Update vote view.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateVoteView(starLevel, commentNum)

#  LocalWords:  FFFFFF eventbox GtkEventBox ScrolledWindow numBox EventBox
#  LocalWords:  numLabel pageIndex numColor
