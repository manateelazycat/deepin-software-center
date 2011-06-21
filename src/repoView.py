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

from appItem import *
from constant import *
from draw import *
import appView
import gtk
import pango
import pygtk
import utils
pygtk.require('2.0')

import urllib2

class RepoItem(DownloadItem):
    '''Application item.'''
    
    MAX_CHARS = 50
    VERSION_MAX_CHARS = 30
    APP_LEFT_PADDING_X = 5
    STAR_PADDING_X = 2
    NORMAL_PADDING_X = 2
    VOTE_PADDING_X = 3
    VOTE_PADDING_Y = 1
    LIKE_PADDING_X = 10
    RATE_PADDING_X = 3
        
    def __init__(self, appInfo, switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback, index, getSelectIndex, setSelectIndex):
        '''Init for application item.'''
        DownloadItem.__init__(self, appInfo, switchStatus, downloadQueue)
        
        self.appInfo = appInfo
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.index = index
        self.setSelectIndex = setSelectIndex
        
        # Init.
        self.itemBox = gtk.HBox()
        self.itemEventBox = gtk.EventBox()
        self.itemEventBox.connect("button-press-event", self.clickItem)
        drawListItem(self.itemEventBox, index, getSelectIndex)
        self.itemFrame = gtk.Alignment()
        self.itemFrame.set(0.0, 0.5, 1.0, 1.0)
        
        self.appBasicBox = createItemBasicBox(self.appInfo, 200, self.itemBox)
        
        # Widget that status will change.
        self.installingProgressbar = None
        self.installingFeedbackLabel = None

        self.upgradingProgressbar = None
        self.upgradingFeedbackLabel = None

        # Connect components.
        self.itemBox.pack_start(self.appBasicBox, True, True, self.APP_LEFT_PADDING_X)
        
        self.appAdditionBox = gtk.HBox()
        self.appAdditionAlign = gtk.Alignment()
        self.appAdditionAlign.set(1.0, 0.5, 0.0, 0.0)
        self.appAdditionAlign.add(self.appAdditionBox)
        self.itemBox.pack_start(self.appAdditionAlign, False, False)
        
        self.initAdditionStatus()
        
        self.itemEventBox.add(self.itemBox)
        self.itemFrame.add(self.itemEventBox)
        self.itemFrame.show_all()
        
    def clickItem(self, widget, event):
        '''Click item.'''
        if utils.isDoubleClick(event):
            self.entryDetailCallback(PAGE_REPO, self.appInfo)
        else:
            self.setSelectIndex(self.index)
        
    def initAdditionStatus(self):
        '''Add addition status.'''
        status = self.appInfo.status
        if status in [APP_STATE_NORMAL, APP_STATE_UPGRADE, APP_STATE_INSTALLED]:
            self.initNormalStatus()
        elif status == APP_STATE_DOWNLOADING:
            self.initDownloadingStatus(self.appAdditionBox)
        elif status == APP_STATE_DOWNLOAD_PAUSE:
            self.initDownloadPauseStatus(self.appAdditionBox)
        elif status == APP_STATE_INSTALLING:
            self.initInstallingStatus()
        elif status == APP_STATE_UPGRADING:
            self.initUpgradingStatus()
            
        self.itemFrame.show_all()
        
    def initNormalStatus(self):
        '''Init normal status.'''
        pkg = self.appInfo.pkg
            
        # Clean right box first.
        utils.containerRemoveAll(self.appAdditionBox)
        
        # Add application size.
        size = utils.getPkgSize(pkg)
        appSize = gtk.Label()
        appSize.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, utils.formatFileSize(size)))
        appSize.set_alignment(1.0, 0.5)
        self.appAdditionBox.pack_start(appSize, False, False, self.LIKE_PADDING_X)
        
        # Add application vote information.
        self.appVoteView = VoteView(
            self.appInfo, PAGE_REPO, 
            self.entryDetailCallback,
            self.sendVoteCallback)
        self.appAdditionBox.pack_start(self.appVoteView.eventbox, False, False)
        
        # Add action button.
        (actionButtonBox, actionButtonAlign) = createActionButton()
        self.appAdditionBox.pack_start(actionButtonAlign, False, False)
        if self.appInfo.status == APP_STATE_NORMAL:
            (appButton, appButtonAlign) = newActionButton(
                "install", 0.5, 0.5, 
                "cell", False, "安装", BUTTON_FONT_SIZE_SMALL
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            actionButtonBox.pack_start(appButtonAlign)
        elif self.appInfo.status == APP_STATE_UPGRADE:
            (appButton, appButtonAlign) = newActionButton(
                "update", 0.5, 0.5, 
                "cell", False, "升级", BUTTON_FONT_SIZE_SMALL
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            actionButtonBox.pack_start(appButtonAlign)
        else:
            appInstalledLabel = gtk.Label()
            appInstalledLabel.set_markup("<span foreground='#1A3E88' size='%s'>%s</span>" % (LABEL_FONT_SIZE, "已安装"))
            buttonImage = gtk.gdk.pixbuf_new_from_file("./icons/cell/update_hover.png")
            appInstalledLabel.set_size_request(buttonImage.get_width(), buttonImage.get_height())
            actionButtonBox.pack_start(appInstalledLabel)
    
    def updateVoteView(self, starLevel, voteNum):
        '''Update vote view.'''
        if self.appInfo.status in [APP_STATE_NORMAL, APP_STATE_UPGRADE, APP_STATE_INSTALLED] and self.appVoteView != None:
            self.appVoteView.updateVote(starLevel, voteNum)
                
class RepoView(appView.AppView):
    '''Application view.'''
	
    def __init__(self, category, appNum, getListFunc, switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback):
        '''Init for application view.'''
        appView.AppView.__init__(self, appNum, PAGE_REPO)
        
        # Init.
        self.category = category
        self.getListFunc = getListFunc
        self.switchStatus = switchStatus
        self.downloadQueue = downloadQueue
        self.itemDict = {}
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.fetchVoteCallback = fetchVoteCallback
        
        self.show()
        
    def update(self, category, appNum):
        '''Update view.'''
        self.category = category
        self.appNum = appNum
        self.pageIndex = 1
        self.calculateMaxPageIndex()
        
        self.show()

    def show(self):
        '''Show application view.'''
        # Remove child widgets first.
        utils.containerRemoveAll(self.box)
        self.itemDict.clear()
        
        if self.appNum != 0:
            # Get application list.
            appList = self.getListFunc(self.category, 
                                       (self.pageIndex - 1) * self.defaultRows,
                                       min(self.pageIndex * self.defaultRows, self.appNum)
                                       )
            
            # Create application view.
            self.box.pack_start(self.createAppList(appList))
            
            
            # Create index view.
            indexbar = self.createIndexbar()
            if not indexbar == None:
                self.box.pack_start(indexbar)
            
            # Show all.
            self.box.show_all()
            
            # Request vote data.
            self.fetchVoteCallback(
                PAGE_REPO, 
                map (lambda appInfo: utils.getPkgName(appInfo.pkg), appList))
            
        # Scroll ScrolledWindow to top after render.
        utils.scrollToTop(self.scrolledwindow)

    def createAppList(self, appList):
        '''Create application list.'''
        # Init.
        itemPaddingY = 5
        
        box = gtk.VBox()
        for (index, appInfo) in enumerate(appList):
            appItem = RepoItem(appInfo, self.switchStatus, self.downloadQueue, 
                               self.entryDetailCallback,
                               self.sendVoteCallback,
                               index, self.getSelectItemIndex, self.setSelectItemIndex)
            box.pack_start(appItem.itemFrame, False, False)
            self.itemDict[utils.getPkgName(appItem.appInfo.pkg)] = appItem
            
        return box

