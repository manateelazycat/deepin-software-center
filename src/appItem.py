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
import appView
import gobject
import gtk
import pango
import progressbar as pb
import pygtk
import searchCompletion as sc
import utils
pygtk.require('2.0')

class UninstallItem:
    '''Application item.'''
    
    ITEM_PADDING = 5
    PROGRESS_WIDTH = 170
    PROGRESS_HEIGHT = 3
    MAX_CHARS = 50
    VERSION_MAX_CHARS = 30
    APP_LEFT_PADDING_X = 5
    APP_RIGHT_PADDING_X = 20
    STAR_PADDING_X = 2
    NORMAL_PADDING_X = 2
    BUTTON_PADDING_X = 4
    PROGRESS_LABEL_WIDTH_CHARS = 25
    VOTE_PADDING_X = 3
    VOTE_PADDING_Y = 1
    VERSION_LABEL_WIDTH = 120
    SIZE_LABEL_WIDTH = 60
        
    def __init__(self, appInfo, actionQueue, 
                 entryDetailCallback, sendVoteCallback, 
                 index, getSelectIndex, setSelectIndex):
        '''Init for application item.'''
        # Init.
        self.appInfo = appInfo
        self.entryDetailCallback = entryDetailCallback
        self.sendVoteCallback = sendVoteCallback
        self.index = index
        self.setSelectIndex = setSelectIndex
        self.actionQueue = actionQueue
        self.confirmUninstall = False
        self.appVoteView = None
        
        # Widget that status will change.
        self.uninstallingProgressbar = None
        self.uninstallingFeedbackLabel = None

        self.itemBox = gtk.HBox()
        self.itemEventBox = gtk.EventBox()
        self.itemEventBox.connect("button-press-event", self.clickItem)
        self.itemEventBox.add(self.itemBox)
        drawListItem(self.itemEventBox, index, getSelectIndex)
        
        self.itemFrame = gtk.Alignment()
        self.itemFrame.set(0.0, 0.5, 1.0, 1.0)
        self.itemFrame.add(self.itemEventBox)
        
        self.appBasicBox = createItemBasicBox(self.appInfo, 200, self.itemBox)
        self.itemBox.pack_start(self.appBasicBox, True, True, self.APP_LEFT_PADDING_X)
        
        self.appAdditionBox = gtk.HBox()
        self.appAdditionAlign = gtk.Alignment()
        self.appAdditionAlign.set(1.0, 0.5, 0.0, 0.0)
        self.appAdditionAlign.add(self.appAdditionBox)
        self.itemBox.pack_start(self.appAdditionAlign, False, False)
        
        self.initAdditionStatus()
        
        self.itemFrame.show_all()
        
    def clickItem(self, widget, event):
        '''Click item.'''
        if utils.isDoubleClick(event):
            self.entryDetailCallback(PAGE_UNINSTALL, self.appInfo)
        else:
            self.setSelectIndex(self.index)
        
    def initAdditionStatus(self):
        '''Add addition status.'''
        status = self.appInfo.status
        if status == APP_STATE_UNINSTALLING:
            self.initUninstallingStatus()
        else:
            self.initNormalStatus()
            
        self.itemFrame.show_all()
        
    def initNormalStatus(self):
        '''Init normal status.'''
        pkg = self.appInfo.pkg
            
        # Clean right box first.
        utils.containerRemoveAll(self.appAdditionBox)
        
        # Add application installed size.
        size = utils.getPkgInstalledSize(pkg)
        appSize = gtk.Label()
        appSize.set_size_request(self.SIZE_LABEL_WIDTH, -1)
        appSize.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, utils.formatFileSize(size)))
        appSize.set_alignment(1.0, 0.5)
        self.appAdditionBox.pack_start(appSize, False, False, self.APP_RIGHT_PADDING_X)
        
        # Add application vote information.
        self.appVoteView = VoteView(
            self.appInfo, PAGE_UNINSTALL, 
            self.entryDetailCallback, 
            self.sendVoteCallback)
        self.appAdditionBox.pack_start(self.appVoteView.eventbox, False, False)
        
        # Add action button.
        (actionButtonBox, actionButtonAlign) = createActionButton()
        self.appAdditionBox.pack_start(actionButtonAlign, False, False)
        
        if self.confirmUninstall:
            appUninstallLabel = gtk.Label()
            appUninstallLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "你确定要卸载吗？"))
            actionButtonBox.pack_start(appUninstallLabel, False, False)
            
            appUninstallBox = gtk.HBox()
            appUninstallAlign = gtk.Alignment()
            appUninstallAlign.set(0.5, 0.5, 1.0, 1.0)
            appUninstallAlign.set_padding(ACTION_BUTTON_PADDING_Y, ACTION_BUTTON_PADDING_Y, 0, 0)
            appUninstallAlign.add(appUninstallBox)
            actionButtonBox.pack_start(appUninstallAlign, False, False)
            
            (appConfirmButton, appConfirmAlign) = newActionButton(
                "uninstall_confirm", 0.0, 0.5, 
                "cell", False, "卸载", BUTTON_FONT_SIZE_SMALL
                )
            appConfirmButton.connect("button-release-event", lambda widget, event: self.switchToUninstalling())
            
            (appCancelButton, appCancelAlign) = newActionButton(
                "uninstall_confirm", 1.0, 0.5, 
                "cell", False, "取消", BUTTON_FONT_SIZE_SMALL
                )
            appCancelButton.connect("button-release-event", lambda widget, event: self.switchToNormal(False))
            
            appUninstallBox.pack_start(appConfirmAlign)
            appUninstallBox.pack_start(appCancelAlign)
        else:
            (appUninstallBox, appUninstallAlign) = newActionButton(
                "uninstall", 0.5, 0.5,
                "cell", False, "卸载", BUTTON_FONT_SIZE_SMALL
                )
            appUninstallBox.connect("button-release-event", lambda widget, event: self.switchToNormal(True))
            actionButtonBox.pack_start(appUninstallAlign)
            
    def initUninstallingStatus(self, withoutBorder=False):
        '''Init uninstalling status.'''
        (progressbar, feedbackLabel) = initActionStatus(
            self.appAdditionBox, 
            self.appInfo.uninstallingProgress,
            self.appInfo.uninstallingFeedback,
            withoutBorder)
        
        self.uninstallingProgressbar = progressbar
        self.uninstallingFeedbackLabel = feedbackLabel
        
    def switchToNormal(self, confirmUninstall=False):
        '''Switch to normal.'''
        self.confirmUninstall = confirmUninstall
        self.appInfo.status = APP_STATE_INSTALLED
        self.initAdditionStatus()
        
    def switchToUninstalling(self):
        '''Switch to uninstalling.'''
        self.appInfo.status = APP_STATE_UNINSTALLING
        self.initAdditionStatus()
        self.actionQueue.addAction(utils.getPkgName(self.appInfo.pkg), ACTION_UNINSTALL)

    def updateUninstallingStatus(self, progress, feedback):
        '''Update uninstalling status.'''
        if self.appInfo.status == APP_STATE_UNINSTALLING:
            if self.uninstallingProgressbar != None and self.uninstallingFeedbackLabel != None:
                self.uninstallingProgressbar.setProgress(progress)
                self.uninstallingFeedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "卸载中"))
                
                self.itemFrame.show_all()
                
    def updateVoteView(self, starLevel, voteNum):
        '''Update vote view.'''
        if not self.appInfo.status == APP_STATE_UNINSTALLING and self.appVoteView != None:
            self.appVoteView.updateVote(starLevel, voteNum)
                
def createActionButton(alignX=0.5, alignY=0.5):
    '''Create action button.'''
    appButtonBox = gtk.VBox()
    appButtonBox.set_size_request(ACTION_BUTTON_WIDTH, -1)
    appButtonAlign = gtk.Alignment()
    appButtonAlign.set(alignX, alignY, 1.0, 1.0)
    appButtonAlign.set_padding(0, 0, ACTION_BUTTON_PADDING_X, ACTION_BUTTON_PADDING_X)
    appButtonAlign.add(appButtonBox)
    
    return (appButtonBox, appButtonAlign)
                
class DownloadItem:
    '''Application item.'''
    PROGRESS_WIDTH = 170
    APP_RIGHT_PADDING_X = 20
    PROGRESS_LABEL_WIDTH_CHARS = 25
    BUTTON_PADDING_X = 4

    def __init__(self, appInfo, switchStatus, downloadQueue):
        '''Init for application item.'''
        # Init.
        self.appInfo = appInfo
        self.switchStatus = switchStatus
        self.downloadQueue = downloadQueue
        self.downloadingProgressbar = None
        self.downloadingFeedbackLabel = None
        self.appVoteView = None
        
    def initDownloadingStatus(self, appAdditionBox, withoutBorder=False):
        '''Init downloading status.'''
        # Clean right box first.
        utils.containerRemoveAll(appAdditionBox)
        
        # Add progress.
        progress = self.appInfo.downloadingProgress
        if withoutBorder:
            progressbar = drawProgressbarWithoutBorder(self.PROGRESS_WIDTH)
        else:
            progressbar = drawProgressbar(self.PROGRESS_WIDTH)
        progressbar.setProgress(progress)
        self.downloadingProgressbar = progressbar
        appAdditionBox.pack_start(progressbar.box)
        
        # Alignment box.
        (actionBox, actionAlign) = createActionButton()
        appAdditionBox.pack_start(actionAlign)
        
        # Add pause icon.
        buttonBox = gtk.HBox()
        buttonAlign = gtk.Alignment()
        buttonAlign.set(0.5, 0.5, 0.0, 0.0)
        buttonAlign.set_padding(ACTION_BUTTON_PADDING_Y, ACTION_BUTTON_PADDING_Y, 0, 0)
        buttonAlign.add(buttonBox)
        actionBox.pack_start(buttonAlign)
        
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
        feedbackLabel.set_width_chars(self.PROGRESS_LABEL_WIDTH_CHARS)
        feedbackLabel.set_ellipsize(pango.ELLIPSIZE_END)
        feedbackLabel.set_alignment(0.5, 0.5)
        self.downloadingFeedbackLabel = feedbackLabel
        actionBox.pack_start(feedbackLabel)
        
    def initDownloadPauseStatus(self, appAdditionBox, withoutBorder=False):
        '''Init download pause status.'''
        # Clean right box first.
        utils.containerRemoveAll(appAdditionBox)
        
        # Add progress.
        progress = self.appInfo.downloadingProgress
        if withoutBorder:
            progressbar = drawProgressbarWithoutBorder(self.PROGRESS_WIDTH)
        else:
            progressbar = drawProgressbar(self.PROGRESS_WIDTH)
        progressbar.setProgress(progress)
        appAdditionBox.pack_start(progressbar.box)
        
        # Alignment box.
        (actionBox, actionAlign) = createActionButton()
        appAdditionBox.pack_start(actionAlign)
        
        # Add play icon.
        buttonBox = gtk.HBox()
        buttonAlign = gtk.Alignment()
        buttonAlign.set(0.5, 0.5, 0.0, 0.0)
        buttonAlign.set_padding(ACTION_BUTTON_PADDING_Y, ACTION_BUTTON_PADDING_Y, 0, 0)
        buttonAlign.add(buttonBox)
        actionBox.pack_start(buttonAlign)
        
        continueIcon = gtk.Button()
        drawSimpleButton(continueIcon, "continue")
        continueIcon.connect("button-release-event", lambda widget, event: self.switchToDownloading())
        buttonBox.pack_start(continueIcon, False, False, self.BUTTON_PADDING_X)
        
        # Add stop icon.
        stopIcon = gtk.Button()
        drawSimpleButton(stopIcon, "stop")
        stopIcon.connect("button-release-event", lambda widget, event: self.switchToNormal())
        buttonBox.pack_start(stopIcon, False, False, self.BUTTON_PADDING_X)
        
        # Add pause label.
        pauseLabel = gtk.Label()
        pauseLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "暂停"))
        pauseLabel.set_width_chars(self.PROGRESS_LABEL_WIDTH_CHARS)
        pauseLabel.set_ellipsize(pango.ELLIPSIZE_END)
        pauseLabel.set_alignment(0.5, 0.5)
        actionBox.pack_start(pauseLabel)
        
    def initInstallingStatus(self, withoutBorder=False):
        '''Init installing status.'''
        (progressbar, feedbackLabel) = initActionStatus(
            self.appAdditionBox, 
            self.appInfo.installingProgress,
            self.appInfo.installingFeedback, 
            withoutBorder)
        
        self.installingProgressbar = progressbar
        self.installingFeedbackLabel = feedbackLabel
        
    def initUpgradingStatus(self, withoutBorder=False):
        '''Init upgrading status.'''
        (progressbar, feedbackLabel) = initActionStatus(
            self.appAdditionBox, 
            self.appInfo.upgradingProgress, 
            self.appInfo.upgradingFeedback,
            withoutBorder)
        
        self.upgradingProgressbar = progressbar
        self.upgradingFeedbackLabel = feedbackLabel
        
    def switchToDownloading(self):
        '''Switch to downloading.'''
        pkgName = utils.getPkgName(self.appInfo.pkg)
        self.switchStatus(pkgName, APP_STATE_DOWNLOADING)
        self.downloadQueue.addDownload(pkgName)
        
    def switchToDownloadPause(self):
        '''Switch to pause.'''
        pkgName = utils.getPkgName(self.appInfo.pkg)
        self.switchStatus(pkgName, APP_STATE_DOWNLOAD_PAUSE)
        self.downloadQueue.stopDownload(pkgName)
        
    def switchToNormal(self):
        '''Switch to normal.'''
        pkgName = utils.getPkgName(self.appInfo.pkg)
        if self.appInfo.pkg.is_upgradable:
            self.switchStatus(pkgName, APP_STATE_UPGRADE)
        else:
            self.switchStatus(pkgName, APP_STATE_NORMAL)
        self.downloadQueue.stopDownload(pkgName)

    def updateDownloadingStatus(self, progress, feedback, color="#000000"):
        '''Update downloading status.'''
        if self.appInfo.status == APP_STATE_DOWNLOADING:
            if self.downloadingProgressbar != None and self.downloadingFeedbackLabel != None:
                self.downloadingProgressbar.setProgress(progress)
                self.downloadingFeedbackLabel.set_markup(
                    "<span foreground='%s' size='%s'>%s</span>"
                    % (color, LABEL_FONT_SIZE, feedback))
                
                self.itemFrame.show_all()
                
    def updateInstallingStatus(self, progress, feedback, color="#000000"):
        '''Update installing status.'''
        if self.appInfo.status == APP_STATE_INSTALLING:
            if self.installingProgressbar != None and self.installingFeedbackLabel != None:
                self.installingProgressbar.setProgress(progress)
                self.installingFeedbackLabel.set_markup(
                    "<span foreground='%s' size='%s'>%s</span>"
                    % (color, LABEL_FONT_SIZE, "安装中"))
                
                self.itemFrame.show_all()
                
    def updateUpgradingStatus(self, progress, feedback, color="#000000"):
        '''Update upgrading status.'''
        if self.appInfo.status == APP_STATE_UPGRADING:
            if self.upgradingProgressbar != None and self.upgradingFeedbackLabel != None:
                self.upgradingProgressbar.setProgress(progress)
                self.upgradingFeedbackLabel.set_markup(
                    "<span foreground='%s' size='%s'>%s</span>"
                    % (color, LABEL_FONT_SIZE, "升级中"))
                
                self.itemFrame.show_all()
                
def createItemBasicBox(appInfo, maxWidth, parent, showVersion=True):
    '''Create item information.'''
    # Init.
    appBasicAlign = gtk.Alignment()
    appBasicAlign.set(0.0, 0.5, 1.0, 1.0)
    
    appBasicBox = gtk.HBox()
    appBasicAlign.add(appBasicBox)
    pkg = appInfo.pkg
    
    # Add application icon.
    appIcon = createAppIcon(pkg)
    appBasicBox.pack_start(appIcon, False, False)
    
    # Add application left box.
    appBox = gtk.VBox()
    appAlign = gtk.Alignment()
    appAlign.set(0.0, 0.5, 0.0, 0.0)
    appAlign.add(appBox)
    appBasicBox.pack_start(appAlign)
    
    # Add application name.
    pkgName = utils.getPkgName(pkg)
    appName = gtk.Label()
    parent.connect("size-allocate", 
                   lambda w, e: adjustLabelWidth(parent, 
                                                 appName,
                                                 LABEL_FONT_SIZE / 1000,
                                                 maxWidth))
    
    appName.set_single_line_mode(True)
    appName.set_ellipsize(pango.ELLIPSIZE_END)
    appName.set_alignment(0.0, 0.5)
    appBox.pack_start(appName, False, False)
    
    pkgVersion = utils.getPkgVersion(pkg)
    nameMarkup = "<span foreground='#1A3E88' size='%s'>%s</span>" % (LABEL_FONT_SIZE, pkgName)
    versionMarkup = "<span foreground='#00BB00' size='%s'> (%s)</span>" % (LABEL_FONT_SIZE, pkgVersion)
    if showVersion:
        appName.set_markup(nameMarkup + versionMarkup)
    else:
        appName.set_markup(nameMarkup)
    
    # Add application summary.
    summary = utils.getPkgShortDesc(pkg)
    appSummaryBox = gtk.HBox()
    appSummary = gtk.Label()
    appSummary.set_markup("<span foreground='#000000' size='%s'>%s</span>" % (LABEL_FONT_SIZE, summary))
    parent.connect("size-allocate", 
                   lambda w, e: adjustLabelWidth(parent, 
                                                 appSummary,
                                                 LABEL_FONT_SIZE / 1000,
                                                 maxWidth))
    
    appSummary.set_single_line_mode(True)
    appSummary.set_ellipsize(pango.ELLIPSIZE_END)
    appSummary.set_alignment(0.0, 0.5)
    appSummaryBox.pack_start(appSummary, False, False)
    appBox.pack_start(appSummaryBox, False, False)
    
    return appBasicAlign

def adjustLabelWidth(parent, label, fontWidth, adjustWidth):
    '''Adjust label width.'''
    label.set_width_chars((parent.allocation.width - adjustWidth) / fontWidth)

def createAppIcon(pkg, size=32, alignLeft=5, alignRight=5, alignTop=5, alignBottom=5):
    '''Create application icon.'''
    appIcon = utils.getPkgIcon(pkg, size, size)
    appIcon.set_size_request(size, size)
    appIconAlign = gtk.Alignment()
    appIconAlign.set(0.5, 0.5, 0.0, 0.0)
    appIconAlign.set_padding(alignTop, alignBottom, alignLeft, alignRight)
    appIconAlign.add(appIcon)
    
    return appIconAlign

class VoteView:
    '''Vote view.'''
    
    VOTE_PADDING_X = 16
    VOTE_PADDING_Y = 3    
    
    FOCUS_STAR = 0
    FOCUS_NORMAL = 1
    FOCUS_INIT = 2
	
    def __init__(self, appInfo, pageId,
                 entryDetailCallback, sendVoteCallback):
        '''Init for vote view.'''
        self.appInfo = appInfo
        self.pageId = pageId
        self.starLevel = 0
        self.voteNum   = 0
        self.sendVoteCallback = sendVoteCallback
        self.entryDetailCallback = entryDetailCallback
        
        self.focusStatus = self.FOCUS_INIT
        # self.focusStatus = self.FOCUS_NORMAL
        self.starSize = 16
        self.starView = None
        
        self.box = gtk.VBox()
        self.align = gtk.Alignment()
        self.align.set(0.5, 0.5, 0.0, 0.0)
        self.align.set_padding(0, 0, self.VOTE_PADDING_X, self.VOTE_PADDING_X)
        self.align.add(self.box)
        self.eventbox = gtk.EventBox()
        self.eventbox.set_visible_window(False)
        self.eventbox.add(self.align)
        
        self.starBox = gtk.HBox()
        self.box.pack_start(self.starBox, False, False, self.VOTE_PADDING_Y)
        
        self.voteBox = gtk.HBox()
        self.box.pack_start(self.voteBox)
        
        self.init()
        
    def init(self):
        '''Init.'''
        if self.focusStatus == self.FOCUS_STAR:
            self.drawFocusStar()
        elif self.focusStatus == self.FOCUS_NORMAL:
            self.drawFocusNormal()
        elif self.focusStatus == self.FOCUS_INIT:
            self.drawFocusInit()
        
        self.eventbox.show_all()
        
    def switchFocusStatus(self, status):
        '''Switch focus status.'''
        self.focusStatus = status
        self.init()
        
        return False
    
    def sendVote(self):
        '''Send vote.'''
        if self.starView != None:
            name = utils.getPkgName(self.appInfo.pkg)                
            vote = self.starView.getStarLevel()
            self.sendVoteCallback(name, vote)
        else:
            print "sendVote: starView is None, send vote failed."
            
    def drawFocusStar(self):
        '''Draw focus star status.'''
        # Remove child first.
        utils.containerRemoveAll(self.starBox)
        utils.containerRemoveAll(self.voteBox)
        
        # Add application vote star.
        self.starView = StarView()
        self.starBox.pack_start(self.starView.eventbox)
        self.starView.eventbox.connect("button-press-event", lambda w, e: self.sendVote())
        self.starView.eventbox.connect("button-press-event", lambda w, e: self.switchFocusStatus(self.FOCUS_NORMAL))
        
    def drawFocusNormal(self):
        '''Draw focus normal status.'''
        # Remove child first.
        utils.containerRemoveAll(self.starBox)
        utils.containerRemoveAll(self.voteBox)
        
        # Add application vote star.
        starBox = createStarBox(self.starLevel, self.starSize)
        
        self.starBox.pack_start(starBox)
        
        self.voteLabel = gtk.Label()
        self.voteLabel.set_markup("<span foreground='#1A3E88' size='%s'>评分</span>" % (LABEL_FONT_SIZE))
        self.voteEventBox = gtk.EventBox()
        self.voteEventBox.set_visible_window(False)
        self.voteEventBox.add(self.voteLabel)
        self.voteEventBox.connect("button-press-event", lambda w, e: self.switchFocusStatus(self.FOCUS_STAR))
        self.voteBox.pack_start(self.voteEventBox)
        utils.setClickableLabel(
            self.voteEventBox,
            self.voteLabel,
            "<span foreground='#1A3E88' size='%s'>评分</span>" % (LABEL_FONT_SIZE),
            "<span foreground='#0084FF' size='%s'>评分</span>" % (LABEL_FONT_SIZE))
        
        self.rate = gtk.Label()
        self.rateEventBox = gtk.EventBox()
        self.rateEventBox.set_visible_window(False)
        self.rateEventBox.add(self.rate)
        self.rateEventBox.connect("button-press-event", 
                             lambda w, e: self.entryDetailCallback(self.pageId, self.appInfo))
        rateAlign = gtk.Alignment()
        rateAlign.set(1.0, 0.5, 0.0, 0.0)
        rateAlign.add(self.rateEventBox)
        self.voteBox.pack_start(rateAlign)
        
        if self.voteNum == 0:
            self.rate.set_markup("<span foreground='#1A3E88' size='%s'>抢沙发!</span>" % (LABEL_FONT_SIZE))
            
            utils.setClickableLabel(
                self.rateEventBox,
                self.rate,
                "<span foreground='#1A3E88' size='%s'>抢沙发!</span>" % (LABEL_FONT_SIZE),
                "<span foreground='#0084FF' size='%s'>抢沙发!</span>" % (LABEL_FONT_SIZE))
        else:
            self.rate.set_markup("<span foreground='#1A3E88' size='%s'>%s 评论</span>" % (LABEL_FONT_SIZE, self.voteNum))
            
            utils.setClickableLabel(
                self.rateEventBox,
                self.rate,
                "<span foreground='#1A3E88' size='%s'>%s 评论</span>" % (LABEL_FONT_SIZE, self.voteNum),
                "<span foreground='#0084FF' size='%s'>%s 评论</span>" % (LABEL_FONT_SIZE, self.voteNum))

    def drawFocusInit(self):
        '''Draw focus out.'''
        # Remove child first.
        utils.containerRemoveAll(self.starBox)
        utils.containerRemoveAll(self.voteBox)
        
        # Add waiting label.
        waitingVoteLabel = gtk.Label()
        waitingVoteLabel.set_markup("<span foreground='#1A3E88' size='%s'>读取评论数据...</span>" % (LABEL_FONT_SIZE))
        self.starBox.pack_start(waitingVoteLabel)
        
    def updateVote(self, starLevel, voteNum):
        '''Update vote.'''
        self.starLevel = starLevel
        self.voteNum = voteNum
        
        if not self.focusStatus == self.FOCUS_STAR:
            self.switchFocusStatus(self.FOCUS_NORMAL)
        
class StarView:
    '''Star view.'''
	
    def __init__(self):
        '''Init for star view.'''
        self.starLevel = 10
        self.starSize = 16
        
        self.eventbox = gtk.EventBox()
        self.eventbox.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.eventbox.add_events(gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.eventbox.set_visible_window(False)
        self.eventbox.set_size_request(self.starSize * 5, self.starSize)
        self.eventbox.connect("motion-notify-event", self.updateStarLevel)
        self.eventbox.connect("expose-event", self.draw)
        
        self.eventbox.show_all()
        
    def draw(self, widget, event):
        '''Draw.'''
        cr = widget.window.cairo_create()
        for i in range(0, 5):
            starPath = getStarPath(i + 1, self.starLevel)
            starPixbuf = gtk.gdk.pixbuf_new_from_file_at_size(starPath, self.starSize, self.starSize)
            drawPixbuf(cr, starPixbuf, 
                       widget.allocation.x + i * self.starSize,
                       widget.allocation.y)
            
        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)
        
        return True

    def updateStarLevel(self, widget, event):
        '''Update star level.'''
        (x, _) = event.get_coords()
        self.starLevel = int(min(x / (self.starSize / 2) + 1, 10))
        self.eventbox.queue_draw()
        
        return True
        
    def getStarLevel(self):
        '''Get star level.'''
        return self.starLevel
    
def createStarBox(starLevel=5.0, starSize=16, paddingX=0):
    '''Create star box.'''
    starLevel = int(round(starLevel)) # round star level
    
    appStarBox = gtk.HBox()
    for i in range(0, 5):
        starIcon = utils.getStarImg(i + 1, starLevel, starSize)
        appStarBox.pack_start(starIcon, False, False, paddingX)
        
    return appStarBox

def initActionStatus(appAdditionBox, progress, feedback, withoutBorder=False):
    '''Init action status.'''
    APP_RIGHT_PADDING_X = 20
    PROGRESS_WIDTH = 170
    
    # Clean right box first.
    utils.containerRemoveAll(appAdditionBox)
    
    # Add progress.
    if withoutBorder:
        progressbar = drawProgressbarWithoutBorder(PROGRESS_WIDTH)
    else:
        progressbar = drawProgressbar(PROGRESS_WIDTH)
    progressbar.setProgress(progress)
    appAdditionBox.pack_start(progressbar.box)
    
    # Alignment box.
    alignBox = gtk.HBox()
    alignBox.set_size_request(ACTION_BUTTON_WIDTH, -1)
    appAdditionBox.pack_start(alignBox, False, False, ACTION_BUTTON_PADDING_X)
    
    # Add feedback label.
    feedbackLabel = gtk.Label()
    feedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, feedback))
    feedbackLabel.set_ellipsize(pango.ELLIPSIZE_END)
    feedbackLabel.set_alignment(0.5, 0.5)
    alignBox.pack_start(feedbackLabel)
    
    return (progressbar, feedbackLabel)

def newActionButton(iconPrefix, alignX, alignY,
                    subDir="cell", scaleX=False, 
                    buttonLabel=None, fontSize=None, labelColor=None,
                    paddingY=0, paddingX=0):
    '''New action button.'''
    button = utils.newButtonWithoutPadding()
    drawButton(button, iconPrefix, subDir, scaleX, buttonLabel, fontSize, labelColor)
    align = gtk.Alignment()
    align.set(alignX, alignY, 0.0, 0.0)
    align.set_padding(paddingY, paddingY, paddingX, paddingX)
    align.add(button)
    
    return (button, align)

class SearchEntry(gtk.Entry):
    '''Search entry.'''
	
    def __init__(self, helpString):
        '''Init for search entry.'''
        # Init.
        gtk.Entry.__init__(self)
        
        # Show help string.
        self.set_text(helpString)
        
        # Clean input when first time focus in entry.
        self.focusInHandler = self.connect("focus-in-event", lambda w, e: self.firstFocusIn())
        
    def firstFocusIn(self):
        '''First touch callback.'''
        # Empty entry when first time focus in.
        self.set_text("")
        
        # Adjust input text color.
        self.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
        
        # And disconnect signal itself.
        self.disconnect(self.focusInHandler)
        
        return False
    
gobject.type_register(SearchEntry)

def newSearchUI(helpString, getCandidatesCallback, clickCandidateCallback, searchCallback):
    '''New search box.'''
    entryPaddingX = 5
    SEARCH_ENTRY_WIDTH = 300
    
    searchBox = gtk.HBox()
    searchAlign = gtk.Alignment()
    searchAlign.set(1.0, 0.0, 0.0, 1.0)
    searchAlign.add(searchBox)
    
    # searchEntry = gtk.Entry()
    searchEntry = SearchEntry(helpString)
    searchEntry.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#999999"))
    searchEntry.set_size_request(SEARCH_ENTRY_WIDTH, -1)
    searchEntry.connect("activate", searchCallback)
    searchBox.pack_start(searchEntry, False, False, entryPaddingX)

    searchCompletion = sc.SearchCompletion(
        searchEntry,
        getCandidatesCallback,
        clickCandidateCallback,
        )
    
    (searchButton, searchButtonAlign) = newActionButton(
        "search", 0.0, 0.5,
        "cell", False, "搜索", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF"
        )
    searchButton.connect("button-release-event", lambda w, e: searchCallback(searchEntry))
    searchBox.pack_start(searchButtonAlign)
    
    return (searchEntry, searchAlign, searchCompletion)
    
