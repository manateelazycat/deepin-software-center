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
                 selectPkgCallback, unselectPkgCallback, getSelectStatusCallback):
        '''Init for application item.'''
        DownloadItem.__init__(self, appInfo, switchStatus, downloadQueue)
        
        self.appInfo = appInfo
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.selectPkgCallback = selectPkgCallback
        self.unselectPkgCallback = unselectPkgCallback
        self.getSelectStatusCallback = getSelectStatusCallback
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
        checkPadding = 10
        self.checkButton = gtk.CheckButton()
        self.checkButton.set_active(self.getSelectStatusCallback(utils.getPkgName(self.appInfo.pkg)))
        self.checkButton.connect("toggled", lambda w: self.toggleSelectStatus())
        checkButtonSetBackground(
            self.checkButton,
            False, False, 
            "./icons/cell/select.png",
            "./icons/cell/selected.png",
            )
        self.checkAlign = gtk.Alignment()
        self.checkAlign.set(0.5, 0.5, 0.0, 0.0)
        self.checkAlign.set_padding(checkPadding, checkPadding, checkPadding, checkPadding)
        self.checkAlign.add(self.checkButton)
        self.itemBox.pack_start(self.checkAlign, False, False)
        
        self.appBasicBox = createItemBasicBox(self.appInfo, 560, self.itemBox, self.entryDetailView, False) 
        self.itemBox.pack_start(self.appBasicBox, True, True)
        
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
        
        # Add application version.
        currentVersion = pkg.installed.version
        if len(pkg.versions) == 0:
            upgradeVersion = "错误的版本, 请报告错误！"
        else:
            upgradeVersion = pkg.versions[0].version
            
        versionBox = gtk.VBox()
        versionAlign = gtk.Alignment()        
        versionAlign.set(0.0, 0.5, 0.0, 0.0)
        versionAlign.add(versionBox)
        self.appAdditionBox.pack_start(versionAlign, True, True, self.APP_RIGHT_PADDING_X)
        
        currentVersionBox = gtk.HBox()
        versionBox.pack_start(currentVersionBox, False, False)
        
        currentVersionName = gtk.Label()
        currentVersionName.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "当前版本: "))
        currentVersionBox.pack_start(currentVersionName, False, False)
        
        currentVersionNum = gtk.Label()
        currentVersionNum.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        currentVersionNum.set_markup("<span foreground='#7d8087' size='%s'>%s</span>" % (LABEL_FONT_SIZE, currentVersion))
        currentVersionNum.set_size_request(self.VERSION_LABEL_WIDTH, -1)
        currentVersionNum.set_alignment(0.0, 0.5)
        currentVersionBox.pack_start(currentVersionNum, False, False)
        
        upgradeVersionBox = gtk.HBox()
        versionBox.pack_start(upgradeVersionBox, False, False)
        
        upgradeVersionName = gtk.Label()
        upgradeVersionName.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "升级版本: "))
        upgradeVersionBox.pack_start(upgradeVersionName, False, False)
        
        upgradeVersionNum = gtk.Label()
        upgradeVersionNum.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        upgradeVersionNum.set_markup("<span foreground='#006efe' size='%s'>%s</span>" % (LABEL_FONT_SIZE, upgradeVersion))
        upgradeVersionNum.set_size_request(self.VERSION_LABEL_WIDTH, -1)
        upgradeVersionNum.set_alignment(0.0, 0.5)
        upgradeVersionBox.pack_start(upgradeVersionNum, False, False)
            
        # Add application size.
        size = utils.getPkgSize(pkg)
        appSize = gtk.Label()
        appSize.set_size_request(self.SIZE_LABEL_WIDTH, -1)
        appSize.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, utils.formatFileSize(size)))
        appSize.set_alignment(1.0, 0.5)
        self.appAdditionBox.pack_start(appSize, False, False, self.APP_RIGHT_PADDING_X)
        
        # Add application vote information.
        self.appVoteView = VoteView(
            self.appInfo, PAGE_UPGRADE, 
            self.entryDetailCallback,
            self.sendVoteCallback)
        self.appAdditionBox.pack_start(self.appVoteView.eventbox, False, False)
        
        # Add action button.
        (actionButtonBox, actionButtonAlign) = createActionButton()
        self.appAdditionBox.pack_start(actionButtonAlign, False, False)
        
        (appButton, appButtonAlign) = newActionButton(
            "update", 0.5, 0.5, "cell", False, "升级", BUTTON_FONT_SIZE_SMALL)
        appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
        actionButtonBox.pack_start(appButtonAlign)
        
    def updateVoteView(self, starLevel, voteNum):
        '''Update vote view.'''
        if self.appInfo.status == APP_STATE_UPGRADE and self.appVoteView != None:
            self.appVoteView.updateVote(starLevel, voteNum)
                
class UpdateView(appView.AppView):
    '''Application view.'''
	
    def __init__(self, repoCache, appNum, getListFunc, switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback):
        '''Init for application view.'''
        appView.AppView.__init__(self, appNum, PAGE_UPGRADE)
        
        # Init.
        self.repoCache = repoCache
        self.getListFunc = getListFunc
        self.switchStatus = switchStatus
        self.downloadQueue = downloadQueue
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.fetchVoteCallback = fetchVoteCallback
        self.itemDict = {}
        
        # Init select list.
        self.selectList = []
        for pkgName in self.repoCache.upgradablePkgs:
            self.selectList.append(pkgName)
        
        self.show()
        
    def selectPkg(self, pkgName):
        '''Select package.'''
        if not pkgName in self.selectList:
            self.selectList.append(pkgName)
            
    def unselectPkg(self, pkgName):
        '''Unselect package.'''
        if pkgName in self.selectList:
            self.selectList.remove(pkgName)
            
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
            notifyBox = gtk.HBox()
            notifyAlign = gtk.Alignment()
            notifyAlign.set(0.5, 0.5, 0.0, 0.0)
            notifyAlign.add(notifyBox)
            self.box.pack_start(notifyAlign)
            
            notifyIconAlignX = 5
            notifyIcon = gtk.image_new_from_file("./icons/update/smile.gif")
            notifyIconAlign = gtk.Alignment()
            notifyIconAlign.set(0.5, 1.0, 0.0, 0.0)
            notifyIconAlign.set_padding(0, 0, notifyIconAlignX, notifyIconAlignX)
            notifyIconAlign.add(notifyIcon)
            notifyBox.pack_start(notifyIconAlign)
            
            notifyLabel = gtk.Label()
            notifyLabel.set_markup(
                "<span foreground='#1A38EE' size='%s'>%s</span>"
                % (LABEL_FONT_XXX_LARGE_SIZE, "你的系统已经是最新的. :)"))
            notifyBox.pack_start(notifyLabel, False, False)
            
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
                                 self.selectPkg, self.unselectPkg, self.getSelectStatus)
            box.pack_start(appItem.itemFrame, False, False)
            self.itemDict[utils.getPkgName(appItem.appInfo.pkg)] = appItem
            
        return box
        
