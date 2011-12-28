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
import appView
import glib
import gtk
import pango
import utils

class UpdateItem(DownloadItem):
    '''Application item.'''
    
    MAX_CHARS = 50
    VERSION_MAX_CHARS = 30
    APP_LEFT_PADDING_X = 5
    STAR_PADDING_X = 2
    NORMAL_PADDING_X = 2
    VOTE_PADDING_X = 3
    VOTE_PADDING_Y = 1
    VERSION_LABEL_WIDTH = 120
    SIZE_LABEL_WIDTH = 60
	
    def __init__(self, appInfo, switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback,
                 index, getSelectIndex, setSelectIndex,
                 selectPkgCallback, unselectPkgCallback, 
                 getSelectStatusCallback, addIgnorePkgCallback):
        '''Init for application item.'''
        DownloadItem.__init__(self, appInfo, switchStatus, downloadQueue)
        
        self.appInfo = appInfo
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.selectPkgCallback = selectPkgCallback
        self.unselectPkgCallback = unselectPkgCallback
        self.getSelectStatusCallback = getSelectStatusCallback
        self.addIgnorePkgCallback = addIgnorePkgCallback
        self.checkButton = None
        self.index = index
        self.setSelectIndex = setSelectIndex
        
        # Widget that status will change.
        self.upgradingProgressbar = None
        self.upgradingFeedbackLabel = None

        # Init.
        self.itemBox = gtk.HBox()
        self.itemEventBox = gtk.EventBox()
        self.itemEventBox.connect("button-press-event", self.clickItem)
        self.itemEventBox.add(self.itemBox)
        drawListItem(self.itemEventBox, index, getSelectIndex)
        
        self.itemFrame = gtk.Alignment()
        self.itemFrame.set(0.0, 0.5, 1.0, 1.0)
        self.itemFrame.add(self.itemEventBox)
        
        # Add check box.
        checkPaddingLeft = 20
        checkPaddingRight = 15
        checkPaddingY = 10
        self.checkButton = gtk.CheckButton()
        self.checkButton.set_active(self.getSelectStatusCallback(utils.getPkgName(self.appInfo.pkg)))
        self.checkButton.connect("toggled", lambda w: self.toggleSelectStatus())
        checkButtonSetBackground(
            self.checkButton,
            False, False, 
            "cell/select.png",
            "cell/selected.png",
            )
        self.checkAlign = gtk.Alignment()
        self.checkAlign.set(0.5, 0.5, 0.0, 0.0)
        self.checkAlign.set_padding(checkPaddingY, checkPaddingY, checkPaddingLeft, checkPaddingRight)
        self.checkAlign.add(self.checkButton)
        self.itemBox.pack_start(self.checkAlign, False, False)
        
        self.appBasicView = AppBasicView(self.appInfo, 300 + APP_BASIC_WIDTH_ADJUST, self.itemBox, self.entryDetailView) 
        self.itemBox.pack_start(self.appBasicView.align, True, True)
        
        self.appAdditionBox = gtk.HBox()
        self.appAdditionAlign = gtk.Alignment()
        self.appAdditionAlign.set(1.0, 0.5, 0.0, 0.0)
        self.appAdditionAlign.add(self.appAdditionBox)
        self.itemBox.pack_start(self.appAdditionAlign, False, False)
        
        self.initAdditionStatus()
       
        self.itemFrame.show_all()
        
    def toggleSelectStatus(self):
        '''Toggle select status.'''
        selectStatus = self.checkButton.get_active()    
        pkgName = utils.getPkgName(self.appInfo.pkg)
        if selectStatus:
            self.selectPkgCallback(pkgName)
        else:
            self.unselectPkgCallback(pkgName)
        
    def entryDetailView(self):
        '''Entry detail view.'''
        self.entryDetailCallback(PAGE_UPGRADE, self.appInfo)
        
    def clickItem(self, widget, event):
        '''Click item.'''
        if utils.isDoubleClick(event):
            self.entryDetailView()
        else:
            self.setSelectIndex(self.index)
        
    def initAdditionStatus(self):
        '''Add addition status.'''
        status = self.appInfo.status
        
        if status == APP_STATE_UPGRADE:
            self.initNormalStatus()
        elif status == APP_STATE_DOWNLOADING:
            self.initDownloadingStatus(self.appAdditionBox)
        elif status == APP_STATE_DOWNLOAD_PAUSE:
            self.initDownloadPauseStatus(self.appAdditionBox)
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
            self.appInfo, PAGE_UPGRADE, 
            self.sendVoteCallback)
        self.appAdditionBox.pack_start(self.appVoteView.eventbox, False, False)
        
        # Add application size.
        size = utils.getPkgSize(pkg)

        appSizeLabel = DynamicSimpleLabel(
            self.appAdditionBox,
            utils.formatFileSize(size),
            appTheme.getDynamicColor("appSize"),
            LABEL_FONT_SIZE,
            )
        appSize = appSizeLabel.getLabel()
        
        appSize.set_size_request(self.SIZE_LABEL_WIDTH, -1)
        appSize.set_alignment(1.0, 0.5)
        self.appAdditionBox.pack_start(appSize, False, False, self.APP_RIGHT_PADDING_X)
        
        # Add ignore button.
        (ignoreLabel, ignoreEventBox) = setDefaultClickableDynamicLabel(
            __("Don't Notify"),
            "appIgnore",
            )
        self.appAdditionBox.pack_start(ignoreEventBox, False, False)
        ignoreEventBox.connect("button-press-event", 
                               lambda w, e: self.addIgnorePkgCallback(utils.getPkgName(pkg)))
        
        # Add action button.
        (actionButtonBox, actionButtonAlign) = createActionButton()
        self.appAdditionBox.pack_start(actionButtonAlign, False, False)
        
        (appButton, appButtonAlign) = newActionButton(
            "update", 0.5, 0.5, "cell", False, __("Action Update"), BUTTON_FONT_SIZE_SMALL, "buttonFont")
        appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
        actionButtonBox.pack_start(appButtonAlign)
        
    def updateVoteView(self, starLevel, commentNum):
        '''Update vote view.'''
        if self.appInfo.status == APP_STATE_UPGRADE and self.appVoteView != None:
            self.appVoteView.updateVote(starLevel, commentNum)
            self.appBasicView.updateCommentNum(commentNum)
                
class UpdateView(appView.AppView):
    '''Application view.'''
	
    def __init__(self, repoCache, switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback, addIgnorePkgCallback):
        '''Init for application view.'''
        appNum = repoCache.getUpgradableNum()
        appView.AppView.__init__(self, appNum, PAGE_UPGRADE)
        
        # Init.
        self.repoCache = repoCache
        self.getListFunc = self.repoCache.getUpgradableAppList
        self.switchStatus = switchStatus
        self.downloadQueue = downloadQueue
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.fetchVoteCallback = fetchVoteCallback
        self.addIgnorePkgCallback = addIgnorePkgCallback
        self.itemDict = {}
        
        # Init select list.
        self.selectList = []
        for pkgName in self.repoCache.upgradablePkgs:
            self.selectList.append(pkgName)
        
        self.show()
        
    def update(self, appNum):
        '''Update view'''
        self.appNum = appNum
        self.calculateMaxPageIndex()
        self.pageIndex = min(self.pageIndex, self.maxPageIndex)
        self.show(False)
        
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
        
        if self.appNum == 0:
            if (getDefaultLanguage() == "default"):
                paddingX = 10
            else:
                paddingX = 0
            
            notifyBox = gtk.VBox()
            notifyAlign = gtk.Alignment()
            notifyAlign.set(0.5, 0.5, 0.0, 0.0)
            notifyAlign.add(notifyBox)
            self.box.pack_start(notifyAlign)
            
            tipImage = gtk.image_new_from_pixbuf(
                gtk.gdk.pixbuf_new_from_file("../icon/tips/%s/updateTip.png" % (getDefaultLanguage())))
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
                
            self.box.show_all()
            
            # Request vote data.
            self.fetchVoteCallback(
                PAGE_UPGRADE, 
                map (lambda appInfo: utils.getPkgName(appInfo.pkg), appList))
            
        # Scroll ScrolledWindow to top after render.
        if scrollToTop:
            utils.scrollToTop(self.scrolledwindow)

    def createAppList(self, appList):
        '''Create application list.'''
        # Init.
        itemPaddingY = 5
        
        box = gtk.VBox()
        for (index, appInfo) in enumerate(appList):
            appItem = UpdateItem(appInfo, self.switchStatus, self.downloadQueue, 
                                 self.entryDetailCallback, 
                                 self.sendVoteCallback,
                                 index, self.getSelectItemIndex, self.setSelectItemIndex,
                                 self.selectPkg, self.unselectPkg, self.getSelectStatus,
                                 self.addIgnorePkgCallback)
            box.pack_start(appItem.itemFrame, False, False)
            self.itemDict[utils.getPkgName(appItem.appInfo.pkg)] = appItem
            
        return box
        
    def selectPkg(self, pkgName):
        '''Select package.'''
        utils.addInList(self.selectList, pkgName)
            
    def unselectPkg(self, pkgName):
        '''Un-select package.'''
        utils.removeFromList(self.selectList, pkgName)
            
    def getSelectStatus(self, pkgName):
        '''Get select status of package.'''
        return pkgName in self.selectList    
    
    def selectAllPkg(self):
        '''Select all packages.'''
        for pkgName in self.repoCache.upgradablePkgs:
            self.selectPkg(pkgName)
            if self.itemDict.has_key(pkgName):
                self.itemDict[pkgName].checkButton.set_active(True)
                
    def unselectAllPkg(self):
        '''Unselect all packages.'''
        for pkgName in self.repoCache.upgradablePkgs:
            self.unselectPkg(pkgName)
            if self.itemDict.has_key(pkgName):
                self.itemDict[pkgName].checkButton.set_active(False)
                
    def getSelectList(self):
        '''Get select package list.'''
        return self.selectList
        

#  LocalWords:  efe pkgName selectList getSelectStatus selectAllPkg selectPkg
#  LocalWords:  unselectAllPkg Unselect unselectPkg getSelectList appNum EE
#  LocalWords:  calculateMaxPageIndex pageIndex maxPageIndex scrollToTop
#  LocalWords:  GtkEventBox ScrolledWindow
