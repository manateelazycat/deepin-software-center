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

class RecommendItem(DownloadItem):
    '''Application item.'''
    
    MAX_CHARS = 50
    VERSION_MAX_CHARS = 30
    APP_LEFT_PADDING_X = 5
    STAR_PADDING_X = 2
    NORMAL_PADDING_X = 2
    VOTE_PADDING_X = 3
    VOTE_PADDING_Y = 1
    
    NAME_WIDTH = 100
    SUMMARY_WIDTH = 280
    ACTION_WIDTH = 70
    PROGRESS_WIDTH = 165
        
    def __init__(self, appInfo, switchStatus, downloadQueue, entryDetailCallback, index, getSelectIndex, setSelectIndex):
        '''Init for application item.'''
        DownloadItem.__init__(self, appInfo, switchStatus, downloadQueue)
        
        self.appInfo = appInfo
        self.entryDetailCallback = entryDetailCallback
        self.index = index
        self.setSelectIndex = setSelectIndex
        
        # Widget that status will change.
        self.installingProgressbar = None
        self.installingFeedbackLabel = None

        self.upgradingProgressbar = None
        self.upgradingFeedbackLabel = None

        # Init.
        itemPaddingX = 3
        self.itemBox = gtk.HBox()
        self.itemAlign = gtk.Alignment()
        self.itemAlign.set(0.5, 0.5, 0.0, 0.0)
        self.itemAlign.set_padding(0, 0, itemPaddingX, itemPaddingX)
        self.itemAlign.add(self.itemBox)
        self.itemEventBox = gtk.EventBox()
        self.itemEventBox.connect("button-press-event", lambda w, e: clickItem(w, e, entryDetailCallback, appInfo))
        drawListItem(self.itemEventBox, index, getSelectIndex, False)
        self.itemFrame = gtk.Alignment()
        self.itemFrame.set(0.0, 0.5, 0.0, 0.0)
        
        self.appLeftBox = gtk.VBox()
        self.appLeftAlign = gtk.Alignment()
        self.appLeftAlign.set(0.0, 0.5, 0.0, 0.0)
        self.appLeftAlign.add(self.appLeftBox)
        self.itemBox.pack_start(self.appLeftAlign)
        
        self.appBasicBox = gtk.HBox()
        self.appLeftBox.pack_start(self.appBasicBox, False, False)
        
        self.appIconBox = gtk.VBox()
        self.appBasicBox.pack_start(self.appIconBox, False, False)
        
        self.appAdditionBox = gtk.VBox()
        self.appAdditionAlign = gtk.Alignment()
        self.appAdditionAlign.set(0.5, 0.5, 0.0, 0.0)
        self.appAdditionAlign.add(self.appAdditionBox)
        self.appBasicBox.pack_start(self.appAdditionAlign, False, False)
        
        self.appTopBox = gtk.HBox()
        self.appAdditionBox.pack_start(self.appTopBox, False, False)
        
        self.appNameBox = gtk.VBox()
        self.appTopBox.pack_start(self.appNameBox, False, False)
        
        self.appFeedbackBox = gtk.VBox()
        self.appTopBox.pack_start(self.appFeedbackBox, False, False)
        
        self.appSummaryBox = gtk.VBox()
        self.appAdditionBox.pack_start(self.appSummaryBox, False, False)
        
        self.appActionBox = gtk.VBox()
        self.appActionBox.set_size_request(self.ACTION_WIDTH, -1)
        self.appActionAlign = gtk.Alignment()
        self.appActionAlign.set(0.5, 0.5, 0.0, 0.0)
        self.appActionAlign.add(self.appActionBox)
        self.itemBox.pack_start(self.appActionAlign, False, False)
        
        self.initBasicBox()
        
        self.initAdditionStatus()
        
        self.itemEventBox.add(self.itemAlign)
        self.itemFrame.add(self.itemEventBox)
        self.itemFrame.show_all()
        
    def initAdditionStatus(self):
        '''Add addition status.'''
        status = self.appInfo.status
        if status in [APP_STATE_NORMAL, APP_STATE_UPGRADE, APP_STATE_INSTALLED]:
            self.initNormalStatus()
        elif status == APP_STATE_DOWNLOADING:
            self.initDownloadingStatus()
        elif status == APP_STATE_DOWNLOAD_PAUSE:
            self.initDownloadPauseStatus()
        elif status == APP_STATE_INSTALLING:
            self.initInstallingStatus()
        elif status == APP_STATE_UPGRADING:
            self.initUpgradingStatus()
            
        self.itemFrame.show_all()
        
    def initNormalStatus(self):
        '''Init normal status.'''
        pkg = self.appInfo.pkg
        
        # Clean feedback box.
        utils.containerRemoveAll(self.appFeedbackBox)
        utils.containerRemoveAll(self.appActionBox)
        
        # Add action button.
        appButtonBox = gtk.VBox()
        self.appActionBox.pack_start(appButtonBox, False, False, self.APP_RIGHT_PADDING_X)
        if self.appInfo.status == APP_STATE_NORMAL:
            (appButton, appButtonAlign) = newActionButton(
                "install", 0.5, 0.5, 
                "cell", False, "安装", BUTTON_FONT_SIZE_SMALL
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            appButtonBox.pack_start(appButtonAlign)
        elif self.appInfo.status == APP_STATE_UPGRADE:
            (appButton, appButtonAlign) = newActionButton(
                "update", 0.5, 0.5, 
                "cell", False, "升级", BUTTON_FONT_SIZE_SMALL
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            appButtonBox.pack_start(appButtonAlign)
        else:
            appInstalledLabel = gtk.Label()
            appInstalledLabel.set_markup("<span foreground='#1A3E88' size='%s'>%s</span>" % (LABEL_FONT_SIZE, "已安装"))
            buttonImage = gtk.gdk.pixbuf_new_from_file("./icons/cell/update_hover.png")
            appInstalledLabel.set_size_request(buttonImage.get_width(), buttonImage.get_height())
            appButtonBox.pack_start(appInstalledLabel)
            
    def initDownloadingStatus(self):
        '''Init downloading status.'''
        # Clean right box first.
        utils.containerRemoveAll(self.appFeedbackBox)
        
        # Add progress.
        progress = self.appInfo.downloadingProgress
        progressbar = drawProgressbar(self.PROGRESS_WIDTH)
        progressbar.setProgress(progress)
        self.downloadingProgressbar = progressbar
        self.appFeedbackBox.pack_start(progressbar.box)
        
        # Alignment box.
        utils.containerRemoveAll(self.appActionBox)
        
        actionBox = gtk.VBox()
        actionAlign = gtk.Alignment()
        actionAlign.set(0.5, 0.5, 0.0, 0.0)
        actionAlign.add(actionBox)
        self.appActionBox.pack_start(actionAlign)
        
        # Add pause icon.
        buttonPaddingY = 5
        buttonBox = gtk.HBox()
        buttonAlign = gtk.Alignment()
        buttonAlign.set_padding(0, buttonPaddingY, 0, 0)
        buttonAlign.add(buttonBox)
        actionBox.pack_start(buttonAlign, False, False)
        
        pauseIcon = gtk.Button()
        drawSimpleButton(pauseIcon, "pause")
        pauseIcon.connect("button-release-event", lambda widget, event: self.switchToDownloadPause())
        buttonBox.pack_start(pauseIcon, False, False, self.BUTTON_PADDING_X)
        
        # Add stop icon.
        stopIcon = gtk.Button()
        drawSimpleButton(stopIcon, "stop")
        stopIcon.connect("button-release-event", lambda widget, event: self.switchToNormal())
        buttonBox.pack_start(stopIcon, False, False, self.BUTTON_PADDING_X)
        
        # Add feedback label.
        feedbackLabel = gtk.Label()
        feedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, self.appInfo.downloadingFeedback))
        feedbackLabel.set_alignment(0.0, 0.5)
        self.downloadingFeedbackLabel = feedbackLabel
        actionBox.pack_start(feedbackLabel)
        
    def initDownloadPauseStatus(self):
        '''Init download pause status.'''
        # Clean right box first.
        utils.containerRemoveAll(self.appFeedbackBox)
        
        # Add progress.
        progress = self.appInfo.downloadingProgress
        progressbar = drawProgressbar(self.PROGRESS_WIDTH)
        progressbar.setProgress(progress)
        self.downloadingProgressbar = progressbar
        self.appFeedbackBox.pack_start(progressbar.box)
        
        # Alignment box.
        utils.containerRemoveAll(self.appActionBox)
        
        actionBox = gtk.VBox()
        actionAlign = gtk.Alignment()
        actionAlign.set(0.5, 0.5, 0.0, 0.0)
        actionAlign.add(actionBox)
        self.appActionBox.pack_start(actionAlign)
        
        # Add continue icon.
        buttonPaddingY = 5
        buttonBox = gtk.HBox()
        buttonAlign = gtk.Alignment()
        buttonAlign.set_padding(0, buttonPaddingY, 0, 0)
        buttonAlign.add(buttonBox)
        actionBox.pack_start(buttonAlign, False, False)
        
        continueIcon = gtk.Button()
        drawSimpleButton(continueIcon, "continue")
        continueIcon.connect("button-release-event", lambda widget, event: self.switchToDownloading())
        buttonBox.pack_start(continueIcon, False, False, self.BUTTON_PADDING_X)
        
        # Add stop icon.
        stopIcon = gtk.Button()
        drawSimpleButton(stopIcon, "stop")
        stopIcon.connect("button-release-event", lambda widget, event: self.switchToNormal())
        buttonBox.pack_start(stopIcon, False, False, self.BUTTON_PADDING_X)
        
        # Add feedback label.
        feedbackLabel = gtk.Label()
        feedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, self.appInfo.downloadingFeedback))
        feedbackLabel.set_alignment(0.0, 0.5)
        self.downloadingFeedbackLabel = feedbackLabel
        actionBox.pack_start(feedbackLabel)
        
    def initInstallingStatus(self):
        '''Init installing status.'''
        # Clean right box first.
        utils.containerRemoveAll(self.appFeedbackBox)
        
        # Add progress.
        progress = self.appInfo.installingProgress
        progressbar = drawProgressbar(self.PROGRESS_WIDTH)
        progressbar.setProgress(progress)
        self.installingProgressbar = progressbar
        self.appFeedbackBox.pack_start(progressbar.box)
        
        # Alignment box.
        utils.containerRemoveAll(self.appActionBox)
        
        actionBox = gtk.VBox()
        actionAlign = gtk.Alignment()
        actionAlign.set(0.5, 0.5, 0.0, 0.0)
        actionAlign.add(actionBox)
        self.appActionBox.pack_start(actionAlign)
        
        # Add feedback label.
        feedbackLabel = gtk.Label()
        feedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, self.appInfo.installingFeedback))
        feedbackLabel.set_alignment(0.0, 0.5)
        self.installingFeedbackLabel = feedbackLabel
        actionBox.pack_start(feedbackLabel)
        
    def initUpgradingStatus(self):
        '''Init upgrading status.'''
        # Clean right box first.
        utils.containerRemoveAll(self.appFeedbackBox)
        
        # Add progress.
        progress = self.appInfo.upgradingProgress
        progressbar = drawProgressbar(self.PROGRESS_WIDTH)
        progressbar.setProgress(progress)
        self.upgradingProgressbar = progressbar
        self.appFeedbackBox.pack_start(progressbar.box)
        
        # Alignment box.
        utils.containerRemoveAll(self.appActionBox)
        
        actionBox = gtk.VBox()
        actionAlign = gtk.Alignment()
        actionAlign.set(0.5, 0.5, 0.0, 0.0)
        actionAlign.add(actionBox)
        self.appActionBox.pack_start(actionAlign)
        
        # Add feedback label.
        feedbackLabel = gtk.Label()
        feedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, self.appInfo.upgradingFeedback))
        feedbackLabel.set_alignment(0.0, 0.5)
        self.upgradingFeedbackLabel = feedbackLabel
        actionBox.pack_start(feedbackLabel)
        
    def updateDownloadingStatus(self, progress, feedback):
        '''Update downloading status.'''
        if self.appInfo.status in [APP_STATE_DOWNLOAD_PAUSE, APP_STATE_DOWNLOADING]:
            if self.downloadingProgressbar != None and self.downloadingFeedbackLabel != None:
                self.downloadingProgressbar.setProgress(progress)
                if self.appInfo.status == APP_STATE_DOWNLOAD_PAUSE:
                    self.downloadingFeedbackLabel.set_markup("<span size='%s'>暂停</span>" % (LABEL_FONT_SIZE))
                else:
                    self.downloadingFeedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, feedback))
                
                self.itemFrame.show_all()
                
    def initBasicBox(self):
        '''Create item information.'''
        # Init.
        pkg = self.appInfo.pkg
        
        # Add application icon.
        appIcon = createAppIcon(pkg)
        self.appIconBox.pack_start(appIcon, False, False)
        
        # Add application name.
        pkgName = utils.getPkgName(pkg)
        appName = gtk.Label()
        nameMarkup = "<span foreground='#1A3E88' size='%s'>%s</span>" % (LABEL_FONT_SIZE, pkgName)
        nameActiveMarkup = "<span foreground='#0084FF' size='%s'>%s</span>" % (LABEL_FONT_SIZE, pkgName)
        appName.set_markup(nameMarkup)
        appName.set_size_request(self.NAME_WIDTH, -1)
        appName.set_single_line_mode(True)
        appName.set_ellipsize(pango.ELLIPSIZE_END)
        appName.set_alignment(0.0, 0.5)
        appNameEventBox = gtk.EventBox()
        appNameEventBox.add(appName)
        appNameEventBox.set_visible_window(False)
        appNameEventBox.connect(
            "button-press-event",
            lambda w, e: self.entryDetailView())
        
        utils.setHelpTooltip(appNameEventBox, "点击查看详细信息")
        
        utils.setClickableLabel(
            appNameEventBox,
            appName,
            nameMarkup,
            nameActiveMarkup,
            )
        
        self.appNameBox.pack_start(appNameEventBox, False, False)
        
        # Add application summary.
        summary = utils.getPkgShortDesc(pkg)
        appSummaryBox = gtk.HBox()
        appSummary = gtk.Label()
        appSummary.set_markup("<span foreground='#000000' size='%s'>%s</span>" % (LABEL_FONT_SIZE, summary))
        appSummary.set_size_request(self.SUMMARY_WIDTH, -1)
        appSummary.set_single_line_mode(True)
        appSummary.set_ellipsize(pango.ELLIPSIZE_END)
        appSummary.set_alignment(0.0, 0.5)
        appSummaryBox.pack_start(appSummary, False, False)
        self.appSummaryBox.pack_start(appSummaryBox, False, False)
        
    def entryDetailView(self):
        '''Entry detail view.'''
        self.entryDetailCallback(PAGE_RECOMMEND, self.appInfo)
        
def clickItem(widget, event, entryDetailCallback, appInfo):
    '''Click item.'''
    if utils.isDoubleClick(event):
        entryDetailCallback(PAGE_RECOMMEND, appInfo)
        
class RecommendView:
    '''Recommend view.'''
	
    def __init__(self, repoCache, switchStatus, downloadQueue, entryDetailCallback, selectCategoryCallback):
        '''Init for recommend view.'''
        # Init.
        self.repoCache = repoCache
        self.switchStatus = switchStatus
        self.downloadQueue = downloadQueue
        self.entryDetailCallback = entryDetailCallback
        self.selectCategoryCallback = selectCategoryCallback
        
        self.box = gtk.VBox()
        self.itemDict = {}
        
        self.index = -1
        self.ticker = 0
        
        # Create container box.
        listLen = len(RECOMMEND_LIST)
        boxlist = map (lambda n: gtk.HBox(), range(0, listLen / 2 + listLen % 2))
        for box in boxlist:
            self.box.pack_start(box, False, False)
        
        # Add recommend list.
        for (index, (itemName, showMore, appList)) in enumerate(RECOMMEND_LIST):
            recommendList = self.createRecommendList(itemName, showMore, appList)
            box = boxlist[index / 2]
            box.pack_start(recommendList, False, False)
            
        self.box.show_all()
        
    def getSelectIndex(self):
        '''Get select index.'''
        return self.index
    
    def setSelectIndex(self, index):
        '''Set select index.'''
        self.index = index    
        self.box.queue_draw()

    def createRecommendList(self, itemName, showMore, appList):
        '''Create recommend list.'''
        # Init.
        alignX = 4
        alignY = 10
        box = gtk.VBox()
        boxAlign = gtk.Alignment()
        boxAlign.set_padding(0, alignY, alignX, alignX)
        boxAlign.add(box)
        
        # Add category name.
        nameBox = gtk.EventBox()
        nameBox.set_visible_window(False)
        drawTitlebar(nameBox)
        box.pack_start(nameBox, False, False)
        
        nameLabelBox = gtk.HBox()
        nameBox.add(nameLabelBox)
        
        nameLabelPaddingLeft = 20
        nameLabel = gtk.Label()
        nameLabel.set_markup("<span foreground='#000000' size='%s'>%s</span>" % (LABEL_FONT_LARGE_SIZE, itemName))
        nameLabelAlign = gtk.Alignment()
        nameLabelAlign.set(0.0, 0.5, 0.0, 0.0)
        nameLabelAlign.set_padding(0, 0, nameLabelPaddingLeft, 0)
        nameLabelAlign.add(nameLabel)
        nameLabelBox.pack_start(nameLabelAlign)
        
        # Show more label.
        if showMore:
            moreLabelPaddingRight = 15
            moreLabel = gtk.Label()
            moreLabel.set_markup(
                "<span foreground='#000000' size='%s'>%s</span>" % (LABEL_FONT_MEDIUM_SIZE, "更多 >>"))
            moreLabelEventBox = gtk.EventBox()
            moreLabelEventBox.add(moreLabel)
            moreLabelEventBox.set_visible_window(False)
            moreLabelAlign = gtk.Alignment()
            moreLabelAlign.set(1.0, 0.5, 0.0, 0.0)
            moreLabelAlign.set_padding(0, 0, 0, moreLabelPaddingRight)
            moreLabelAlign.add(moreLabelEventBox)
            nameLabelBox.pack_start(moreLabelAlign)
            
            # Switch to repo page and select category.
            categoryIndex = (map (lambda (k, _): k, CLASSIFY_LIST)).index(itemName)
            moreLabelEventBox.connect(
                "button-press-event", 
                lambda w, e: self.selectCategoryCallback(itemName, categoryIndex))
            
            # Make it clickable.
            utils.setClickableLabel(
                moreLabelEventBox,
                moreLabel,
                "<span foreground='#000000' size='%s'>更多 >></span>" % (LABEL_FONT_MEDIUM_SIZE),
                "<span foreground='#0084FF' size='%s'>更多 >></span>" % (LABEL_FONT_MEDIUM_SIZE))
        
        # Content box.
        contentBox = gtk.HBox()
        box.pack_start(contentBox, False, False)
        
        leftLine = gtk.Image()
        drawLine(leftLine, "#BBE0F6", 2, True, LINE_LEFT)
        contentBox.pack_start(leftLine, False, False)
        
        middleBox = gtk.VBox()
        contentBox.pack_start(middleBox, False, False)
        
        rightLine = gtk.Image()
        drawLine(rightLine, "#BBE0F6", 2, True, LINE_RIGHT)
        contentBox.pack_start(rightLine, False, False)
        
        # Add application information's.
        for appName in appList:
            if self.repoCache.cache.has_key(appName):
                appInfo = self.repoCache.cache[appName]
                recommendItem = RecommendItem(appInfo, self.switchStatus, self.downloadQueue, self.entryDetailCallback,
                                              self.ticker, self.getSelectIndex, self.setSelectIndex)
                self.ticker = self.ticker + 1
                middleBox.pack_start(recommendItem.itemFrame)
                self.itemDict[appName] = recommendItem
            else:
                print "%s not in repoCache, skip it." % (appName)
                
        # Bottom line.
        bottomLine = gtk.Image()
        drawLine(bottomLine, "#BBE0F6", 2, False, LINE_BOTTOM)
        box.pack_start(bottomLine, False, False)
    
        return boxAlign
    
    def switchToStatus(self, pkgName, appStatus):
        '''Switch to downloading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.appInfo.status = appStatus
            appItem.initAdditionStatus()

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
            
    def initNormalStatus(self, pkgName, isMarkDeleted):
        '''Init normal status.'''
        if isMarkDeleted:
            self.switchToStatus(pkgName, APP_STATE_NORMAL)
        else:
            self.switchToStatus(pkgName, APP_STATE_INSTALLED)
