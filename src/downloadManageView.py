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

from appItem import *
from constant import *
from draw import *
from lang import __, getDefaultLanguage
from theme import *
from utils import *
import appView
import glib
import gtk
import pango
import urllib2
import utils

class DownloadManageItem(DownloadItem):
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
        
        self.appBasicView = AppBasicView(self.appInfo, 200 + APP_BASIC_WIDTH_ADJUST, self.itemBox, self.entryDetailView)
        
        # Widget that status will change.
        self.installingProgressbar = None
        self.installingFeedbackLabel = None

        self.upgradingProgressbar = None
        self.upgradingFeedbackLabel = None

        # Connect components.
        self.itemBox.pack_start(self.appBasicView.align, True, True, self.APP_LEFT_PADDING_X)
        
        self.appAdditionBox = gtk.HBox()
        self.appAdditionAlign = gtk.Alignment()
        self.appAdditionAlign.set(1.0, 0.5, 0.0, 0.0)
        self.appAdditionAlign.add(self.appAdditionBox)
        self.itemBox.pack_start(self.appAdditionAlign, False, False)
        
        self.initAdditionStatus()
        
        self.itemEventBox.add(self.itemBox)
        self.itemFrame.add(self.itemEventBox)
        self.itemFrame.show_all()
        
    def entryDetailView(self):
        '''Entry detail view.'''
        self.entryDetailCallback(PAGE_DOWNLOAD_MANAGE, self.appInfo)
        
    def clickItem(self, widget, event):
        '''Click item.'''
        if utils.isDoubleClick(event):
            self.entryDetailView()
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
        
        # Add application vote information.
        self.appVoteView = VoteView(
            self.appInfo, PAGE_DOWNLOAD_MANAGE, 
            self.sendVoteCallback)
        self.appAdditionBox.pack_start(self.appVoteView.eventbox, False, False)
        
        # Add application size.
        size = utils.getPkgSize(pkg)
        appSize = gtk.Label()
        appSize.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, utils.formatFileSize(size)))
        appSize.set_alignment(1.0, 0.5)
        self.appAdditionBox.pack_start(appSize, False, False, self.LIKE_PADDING_X)
        
        # Add action button.
        (actionButtonBox, actionButtonAlign) = createActionButton()
        self.appAdditionBox.pack_start(actionButtonAlign, False, False)
        if self.appInfo.status == APP_STATE_NORMAL:
            (appButton, appButtonAlign) = newActionButton(
                "install", 0.5, 0.5, 
                "cell", False, __("Action Install"), BUTTON_FONT_SIZE_SMALL, "buttonFont"
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            actionButtonBox.pack_start(appButtonAlign)
        elif self.appInfo.status == APP_STATE_UPGRADE:
            (appButton, appButtonAlign) = newActionButton(
                "update", 0.5, 0.5, 
                "cell", False, __("Action Update"), BUTTON_FONT_SIZE_SMALL, "buttonFont"
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            actionButtonBox.pack_start(appButtonAlign)
        else:
            appInstalledDynamicLabel = DynamicSimpleLabel(
                actionButtonBox,
                __("Action Installed"),
                appTheme.getDynamicColor("installed"),
                LABEL_FONT_SIZE,
                )
            appInstalledLabel = appInstalledDynamicLabel.getLabel()
            buttonImage = appTheme.getDynamicPixbuf("cell/update_hover.png").getPixbuf()
            appInstalledLabel.set_size_request(buttonImage.get_width(), buttonImage.get_height())
            actionButtonBox.pack_start(appInstalledLabel)
    
    def updateVoteView(self, starLevel, commentNum):
        '''Update vote view.'''
        if self.appInfo.status in [APP_STATE_NORMAL, APP_STATE_UPGRADE, APP_STATE_INSTALLED] and self.appVoteView != None:
            self.appVoteView.updateVote(starLevel, commentNum)
            self.appBasicView.updateCommentNum(commentNum)
                
class DownloadManageView(appView.AppView):
    '''Application view.'''
	
    def __init__(self, repoCache, getRunningNum, getListFunc, switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback):
        '''Init for application view.'''
        appNum = getRunningNum()
        appView.AppView.__init__(self, appNum, PAGE_DOWNLOAD_MANAGE)
        
        # Init.
        self.repoCache = repoCache
        self.getRunningNum = getRunningNum
        self.getListFunc = getListFunc
        self.switchStatus = switchStatus
        self.downloadQueue = downloadQueue
        self.itemDict = {}
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.fetchVoteCallback = fetchVoteCallback
        
        self.show()
        
    def update(self, appNum):
        '''Update view.'''
        self.appNum = appNum
        self.pageIndex = 1
        self.calculateMaxPageIndex()
        self.show()

    def show(self):
        '''Show application view.'''
        # Remove child widgets first.
        utils.containerRemoveAll(self.box)
        self.itemDict.clear()
        
        if self.appNum == 0:
            if (getDefaultLanguage() == "default"):
                paddingX = 10
            else:
                paddingX = 45
            
            notifyBox = gtk.VBox()
            notifyAlign = gtk.Alignment()
            notifyAlign.set(0.5, 0.5, 0.0, 0.0)
            notifyAlign.add(notifyBox)
            self.box.pack_start(notifyAlign)
            
            tipImage = gtk.image_new_from_pixbuf(
                gtk.gdk.pixbuf_new_from_file("../icon/tips/%s/downloadTip.png" % (getDefaultLanguage())))
            tipAlign = gtk.Alignment()
            tipAlign.set_padding(0, 0, paddingX, 0)
            tipAlign.add(tipImage)
            notifyBox.pack_start(tipAlign)
            
            penguinImage = gtk.image_new_from_pixbuf(
                gtk.gdk.pixbuf_new_from_file("../icon/tips/penguin.png"))
            penguinAlign = gtk.Alignment()
            penguinAlign.set_padding(0, 0, 0, paddingX)
            penguinAlign.add(penguinImage)
            notifyBox.pack_start(penguinAlign)
            
            self.box.show_all()
        else:
            # Get application list.
            appList = self.getListFunc(
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
                PAGE_DOWNLOAD_MANAGE, 
                map (lambda appInfo: utils.getPkgName(appInfo.pkg), appList))
            
        # Scroll ScrolledWindow to top after render.
        utils.scrollToTop(self.scrolledwindow)

    def createAppList(self, appList):
        '''Create application list.'''
        itemPaddingY = 5
        
        box = gtk.VBox()
        for (index, appInfo) in enumerate(appList):
            appItem = DownloadManageItem(appInfo, self.switchStatus, self.downloadQueue, 
                                         self.entryDetailCallback,
                                         self.sendVoteCallback,
                                         index, self.getSelectItemIndex, self.setSelectItemIndex)
            self.box.pack_start(appItem.itemFrame, False, False)
            self.itemDict[utils.getPkgName(appItem.appInfo.pkg)] = appItem
        
        return box
    
#  LocalWords:  ScrolledWindow
