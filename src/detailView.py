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

from appItem import *
from draw import *
from constant import *
from draw import *
from math import pi
import appView
import gtk
import os
import pango
import pygtk
import subprocess
import threading as td
import time
import utils
import urllib2
import urllib
import json
import time
import base64
pygtk.require('2.0')

class DetailView:
    '''Detail view.'''

    PADDING = 10
    EXTRA_PADDING_X = 20
    SCREENSHOT_WIDTH = 240
    SCREENSHOT_HEIGHT = 180
    SCREENSHOT_PADDING = 20
    LANGUAGE_BOX_PADDING = 3
    DETAIL_PADDING_X = 10
    COMMENT_PADDING_TOP = 20
    COMMENT_PADDING_BOTTOM = 5
    ALIGN_X = 20
    ALIGN_Y = 10
    STAR_PADDING_X = 10
    INFO_PADDING_Y = 3

    def __init__(self, aptCache, pageId, appInfo, 
                 switchStatus, downloadQueue, actionQueue,
                 exitCallback, noscreenshotList, updateMoreCommentCallback,
                 messageCallback):
        '''Init for detail view.'''
        # Init.
        self.aptCache = aptCache
        self.pageId = pageId
        self.appInfo = appInfo
        pkg = appInfo.pkg
        self.bigScreenshot = None
        self.readMoreAlign = None
        self.commentNotifyAlign = None
        self.lastCommentId = ""
        self.updateMoreCommentCallback = updateMoreCommentCallback
        self.messageCallback = messageCallback
        
        self.box = gtk.VBox()
        self.eventbox = gtk.EventBox()
        self.eventbox.add(self.box)
        self.eventbox.connect("expose-event", lambda w, e: drawBackground(w, e, "#FFFFFF"))
        
        self.align = gtk.Alignment()
        self.align.set(0.0, 0.0, 1.0, 1.0)
        self.align.set_padding(0, 0, 0, 0)
        self.align.add(self.eventbox)
       
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        utils.addInScrolledWindow(self.scrolledWindow, self.align)
        
        # Add title bar.
        titleBox = gtk.HBox()
        titleEventbox = gtk.EventBox()
        titleEventbox.add(titleBox)
        self.box.pack_start(titleEventbox, False, False)
        eventBoxSetBackground(
            titleEventbox,
            True, False,
            "./icons/detail/background.png")

        # Add title.
        appInfoBox = gtk.HBox()
        titleBox.pack_start(appInfoBox)
        
        appIconAlign = createAppIcon(pkg, 48, self.ALIGN_X, 10, 10, 10)
        appInfoBox.pack_start(appIconAlign, False, False)

        paddingY = 4
        appMiddleBox = gtk.VBox()
        appMiddleAlign = gtk.Alignment()
        appMiddleAlign.add(appMiddleBox)
        appMiddleAlign.set(0.0, 0.5, 0.0, 0.0)
        appMiddleAlign.set_padding(paddingY, 0, 0, 0)
        appInfoBox.pack_start(appMiddleAlign, False, False)
        
        self.appNameBox = gtk.HBox()
        appMiddleBox.pack_start(self.appNameBox, False, False)
        
        pkgName = utils.getPkgName(pkg)
        appName = gtk.Label()
        appName.set_markup("<span foreground='#000000' size='%s'><b>%s</b></span>" % (LABEL_FONT_XX_LARGE_SIZE, pkgName))
        appNameAlign = gtk.Alignment()
        appNameAlign.set(0.0, 0.5, 0.0, 0.0)
        appNameAlign.add(appName)
        self.appNameBox.pack_start(appNameAlign, False, False)
        
        appIntro = gtk.Label()
        appIntro.set_markup("<span foreground='#333333' size='%s'>%s</span>" % (LABEL_FONT_LARGE_SIZE, utils.getPkgShortDesc(pkg)))
        appIntroAlign = gtk.Alignment()
        appIntroAlign.set(0.0, 0.0, 0.0, 0.0)
        appIntroAlign.add(appIntro)
        appMiddleBox.pack_start(appIntroAlign, False, False)
        
        # Add return button.
        self.returnButton = utils.newButtonWithoutPadding()
        self.returnButton.connect("button-release-event", lambda widget, event: exitCallback(pageId))
        self.returnButton.connect("button-release-event", lambda widget, event: self.closeBigScreenshot(True))
        drawButton(self.returnButton, "return", "cell", False, "返回", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF")
        
        buttonPaddingTop = 20
        buttonPaddingRight = 38
        returnButtonAlign = gtk.Alignment()
        returnButtonAlign.set(0.0, 0.0, 0.0, 0.0)
        returnButtonAlign.add(self.returnButton)
        returnButtonAlign.set_padding(buttonPaddingTop, 0, 0, buttonPaddingRight)
        titleBox.pack_start(returnButtonAlign, False, False)

        # Add top information.
        self.appInfoItem = AppInfoItem(self.aptCache, appInfo, switchStatus, downloadQueue, actionQueue)
        
        topAlign = gtk.Alignment()
        topAlign.set(0.0, 0.0, 1.0, 1.0)
        topAlign.set_padding(self.PADDING, self.PADDING, 0, 0)
        topAlign.add(self.appInfoItem.itemFrame)
        
        self.box.pack_start(topAlign, False, False)
        
        # Add body box.
        self.bodyBox = gtk.VBox()
        
        self.box.pack_start(self.bodyBox)
        
        # Action box.
        self.actionBox = gtk.HBox()
        self.actionAlign = gtk.Alignment()
        self.actionAlign.set(0.0, 0.0, 1.0, 1.0)
        self.actionAlign.set_padding(self.ALIGN_Y, self.ALIGN_Y, self.ALIGN_X, self.ALIGN_X)
        self.actionAlign.add(self.actionBox)
        self.bodyBox.pack_start(self.actionAlign, False, False)
        
        self.toggleTab = gtk.CheckButton()
        self.toggleTab.connect("button-press-event", lambda w, e: self.selectTab())
        self.actionBox.pack_start(self.toggleTab, False, False)
        toggleTabSetBackground(
            self.toggleTab,
            False, False,
            "./icons/detail/detailTab.png",
            "./icons/detail/helpTab.png",
            "详细信息",
            "协助翻译"
            )
        
        # Content box.
        self.contentBox = gtk.VBox()
        self.bodyBox.pack_start(self.contentBox, False, False)
        
        self.infoTab = self.createInfoTab(appInfo, pkg, noscreenshotList)
        self.helpTab = self.createHelpTab(pkg)
        
        self.toggleTab.set_active(False)
        self.selectTab()
        
        self.scrolledWindow.show_all()
        
    def selectTab(self):
        '''Select info tab.'''
        utils.containerRemoveAll(self.contentBox)        
        
        self.toggleTab.set_active(not self.toggleTab.get_active())
        
        if self.toggleTab.get_active():
            self.contentBox.pack_start(self.infoTab)
        else:
            self.contentBox.pack_start(self.helpTab)
        
        self.contentBox.show_all()
        
        return True
    
    def createInfoTab(self, appInfo, pkg, noscreenshotList):
        '''Select information tab.'''
        pkgName = utils.getPkgName(pkg)
        
        box = gtk.VBox()
        align = gtk.Alignment()
        align.set(0.0, 0.0, 1.0, 1.0)
        align.set_padding(0, 0, self.ALIGN_X, self.ALIGN_X)
        align.add(box)
        
        # Add info box.
        infoBox = gtk.HBox()
        box.pack_start(infoBox)
        
        # Add detail box.
        detailBox = gtk.VBox()
        infoBox.pack_start(detailBox)
        
        # Add summary.
        summaryAlignRight = 30
        summaryAlignTop = 10
        summaryLabel = gtk.Label()
        summaryLabel.set_markup("<span foreground='#1A3E88' size='%s'><b>详细介绍</b></span>" % (LABEL_FONT_LARGE_SIZE))
        summaryLabel.set_alignment(0.0, 0.5)
        detailBox.pack_start(summaryLabel)
        summaryView = createContentView(utils.getPkgLongDesc(pkg), False)
        summaryAlign = gtk.Alignment()
        summaryAlign.set(0.0, 0.0, 1.0, 1.0)
        summaryAlign.set_padding(summaryAlignTop, 0, 0, summaryAlignRight)
        summaryAlign.add(summaryView)
        detailBox.pack_start(summaryAlign)
        
        # Add screenshot.
        screenshotBox = gtk.VBox()
        
        screenshotLabel = gtk.Label()
        screenshotLabel.set_markup("<span foreground='#1A3E88' size='%s'><b>软件截图</b></span>" % (LABEL_FONT_LARGE_SIZE))
        screenshotLabel.set_alignment(0.0, 0.5)
        screenshotBox.pack_start(screenshotLabel, False, False)
        
        self.imageBox = gtk.EventBox()
        self.imageBox.set_size_request(self.SCREENSHOT_WIDTH, self.SCREENSHOT_HEIGHT)
        self.imageBox.connect("expose-event", lambda w, e: drawBackground(w, e, "#FFFFFF"))
        screenshotBox.pack_start(self.imageBox, False, False)
        
        self.screenshotImage = gtk.Image()
        self.imageBox.add(self.screenshotImage)
        self.imageBox.connect("button-press-event", lambda w, e: self.showBigScreenshot(w, pkgName, noscreenshotList))

        infoBox.pack_start(screenshotBox, False, False, self.DETAIL_PADDING_X)
        
        # Fetch screenshot.
        screenshotPath = SCREENSHOT_DOWNLOAD_DIR + pkgName
        screenshotWidth = self.SCREENSHOT_WIDTH - self.SCREENSHOT_PADDING
        screenshotHeight = self.SCREENSHOT_HEIGHT - self.SCREENSHOT_PADDING
        # Set screenshot image if has in cache.
        if os.path.exists (screenshotPath):
            self.screenshotImage.set_from_pixbuf(
                gtk.gdk.pixbuf_new_from_file_at_size(screenshotPath, screenshotWidth, screenshotHeight))
        # Otherwise just fetch screenshot when not in black list.
        elif not pkgName in noscreenshotList:
            # Init fetch thread.
            fetchScreenshot = FetchScreenshot(
                appInfo, noscreenshotList,
                self.imageBox, self.screenshotImage, 
                screenshotWidth, screenshotHeight)
            
            # Start fetch thread.
            fetchScreenshot.start()
            
            # Make sure download thread stop when detail view destroy.
            self.returnButton.connect("button-release-event", lambda widget, event: fetchScreenshot.stop())
            self.returnButton.connect("destroy", lambda widget: fetchScreenshot.stop())
        else:
            print "No screenshot for %s, don't need fetch." % (pkgName)
            
            # Set upload image.
            self.screenshotImage.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file("./icons/screenshot/upload.png"))        

        # Add comment label.
        self.commentAreaBox = gtk.VBox()
        detailBox.pack_start(self.commentAreaBox)
            
        self.commentListBox = gtk.VBox()
        
        # Add wait box.
        commentWaitBox = gtk.HBox()
        commentWaitAlign = gtk.Alignment()
        commentWaitAlign.set(0.5, 0.5, 0.0, 0.0)
        commentWaitAlign.set_padding(20, 20, 0, 0)
        commentWaitAlign.add(commentWaitBox)
        self.commentAreaBox.pack_start(commentWaitAlign)
        
        commentWaitSpinner = gtk.Spinner()
        commentWaitSpinner.start()
        commentWaitSpinnerAlign = gtk.Alignment()
        commentWaitSpinnerAlign.set(0.5, 0.5, 0.0, 0.0)
        commentWaitSpinnerAlign.set_padding(10, 10, 10, 10)
        commentWaitSpinnerAlign.add(commentWaitSpinner)
        commentWaitBox.pack_start(commentWaitSpinnerAlign, False, False)
        
        commentWaitLabel = gtk.Label()
        commentWaitLabel.set_markup("<span foreground='#1A3E88' size='%s'><b>读取用户评论...</b></span>"
                                    % (LABEL_FONT_LARGE_SIZE))
        commentWaitBox.pack_start(commentWaitLabel, False, False)
        
        return align
    
    def showBigScreenshot(self, imageWidget, pkgName, noscreenshotList):
        '''Show big screenshot.'''
        if not pkgName in noscreenshotList:
            screenshotPixbuf = self.screenshotImage.get_pixbuf()
            if screenshotPixbuf != None:
                if self.bigScreenshot == None:
                     screenshotPath = SCREENSHOT_DOWNLOAD_DIR + pkgName
                     self.bigScreenshot = BigScreenshot(self.scrolledWindow, screenshotPath, self.closeBigScreenshot)
        else:
            print "*** Help us upload screenshot!"
                 
    def closeBigScreenshot(self, destroy=False):
        '''Close big screenshot.'''
        if destroy and self.bigScreenshot != None:
            self.bigScreenshot.window.destroy()
        self.bigScreenshot = None
    
    def adjustTranslatePaned(self, widget):
        '''Adjust translate paned.'''
        self.translatePaned.set_position(widget.allocation.width / 2)
        
    def adjustTargetShortView(self):
        '''Adjust target short view.'''
        height = self.sourceShortView.allocation.height
        self.targetShortView.set_size_request(-1, height)
        
    def createHelpTab(self, pkg):
        '''Select help tab.'''
        helpBox = gtk.VBox()
        
        align = gtk.Alignment()
        align.set(0.0, 0.0, 1.0, 1.0)
        align.set_padding(0, 0, self.ALIGN_X, self.ALIGN_X)
        align.add(helpBox)
        
        self.translatePaned = gtk.HPaned()
        helpBox.connect("size-allocate", lambda w, e: self.adjustTranslatePaned(w))
        helpBox.pack_start(self.translatePaned)
        
        helpAlignX = 20

        sourceBox = gtk.VBox()
        sourceAlign = gtk.Alignment()
        sourceAlign.set(0.0, 0.0, 1.0, 1.0)
        sourceAlign.set_padding(0, 0, 0, helpAlignX)
        sourceAlign.add(sourceBox)
        self.translatePaned.pack1(sourceAlign)
        
        sourceLanguageBox = gtk.HBox()
        sourceBox.pack_start(sourceLanguageBox, False, False)
        
        sourceLabel = gtk.Label()
        sourceLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "原文"))
        sourceLanguageBox.pack_start(sourceLabel, False, False, self.LANGUAGE_BOX_PADDING)
        
        sourceComboBox = gtk.combo_box_new_text()
        sourceLanguageBox.pack_start(sourceComboBox, True, True, self.LANGUAGE_BOX_PADDING)
        sourceIndex = 0
        for (index, sourceLanguage) in enumerate(LANGUAGE):
            if sourceLanguage == SOURCE_LANGUAGE:
                sourceIndex = index
            sourceComboBox.append_text(sourceLanguage)
        sourceComboBox.set_active(sourceIndex)
        
        self.sourceShortView = createContentView(utils.getPkgShortDesc(pkg), False)
        sourceShortFrame = gtk.Frame("简介")
        sourceShortFrame.add(self.sourceShortView)
        sourceBox.pack_start(sourceShortFrame, False, False)
        
        sourceBox.pack_start(gtk.VSeparator(), False, False)
        
        sourceLongView = createContentView(utils.getPkgLongDesc(pkg), False)
        sourceLongFrame = gtk.Frame("详细介绍")
        sourceLongFrame.add(sourceLongView)
        sourceBox.pack_start(sourceLongFrame)

        targetBox = gtk.VBox()
        targetAlign = gtk.Alignment()
        targetAlign.set(1.0, 0.0, 1.0, 1.0)
        targetAlign.set_padding(0, 0, helpAlignX, 0)
        targetAlign.add(targetBox)
        self.translatePaned.pack2(targetAlign)
        
        targetLanguageBox = gtk.HBox()
        targetBox.pack_start(targetLanguageBox, False, False)
        
        targetLabel = gtk.Label()
        targetLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "译文"))
        targetLanguageBox.pack_start(targetLabel, False, False, self.LANGUAGE_BOX_PADDING)
        
        targetComboBox = gtk.combo_box_new_text()
        targetLanguageBox.pack_start(targetComboBox, True, True, self.LANGUAGE_BOX_PADDING)
        targetIndex = 0
        for (index, targetLanguage) in enumerate(LANGUAGE):
            if targetLanguage == TARGET_LANGUAGE:
                targetIndex = index
            targetComboBox.append_text(targetLanguage)
        targetComboBox.set_active(targetIndex)
            
        self.targetShortView = createContentView("", True)
        self.sourceShortView.connect("size-allocate", lambda w, e: self.adjustTargetShortView())
        targetShortFrame = gtk.Frame("简介")
        targetShortFrame.add(self.targetShortView)
        targetBox.pack_start(targetShortFrame, False, False)
        
        targetBox.pack_start(gtk.VSeparator(), False, False)
        
        targetLongView = createContentView("", True)
        targetLongFrame = gtk.Frame("详细介绍")
        targetLongFrame.add(targetLongView)
        targetBox.pack_start(targetLongFrame)
        
        statusBox = gtk.HBox()
        helpBox.pack_start(statusBox, False, False)
        
        statusLabel = gtk.Label()
        statusLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "目前文档尚未翻译完成， 感谢您帮助我们!"))
        statusLabel.set_alignment(0.0, 0.5)
        statusBox.pack_start(statusLabel)
        
        translateCommitButton = gtk.Button("提交翻译")
        statusBox.pack_start(translateCommitButton, False, False)
        
        return align
        
    def createComment(self, (commentName, commentIcon, commentDate, commentContent)):
        '''Create comment.'''
        align = 5
        padding = 10
        
        commentBox = gtk.VBox()
        commentAlign = gtk.Alignment()
        commentAlign.set(0.0, 0.5, 1.0, 1.0)
        commentAlign.set_padding(padding, padding, 0, 0)
        commentAlign.add(commentBox)
        
        box = gtk.HBox()    
        commentBox.pack_start(box, False, False)
        
        icon = gtk.image_new_from_file(commentIcon)
        iconAlign = gtk.Alignment()
        iconAlign.set(0.5, 0.5, 0.0, 0.0)
        iconAlign.set_padding(align, align, align, align)
        iconAlign.add(icon)
        box.pack_start(iconAlign, False, False)
        
        rightBox = gtk.VBox()
        box.pack_start(rightBox)
        
        infoBox = gtk.HBox()
        rightBox.pack_start(infoBox, False, False)
        
        nameLabel = gtk.Label()
        nameLabel.set_markup("<span foreground='#1A3E88' size='%s'>%s</span>" % (LABEL_FONT_SIZE, commentName))
        infoBox.pack_start(nameLabel, False, False)
        
        dataLabel = gtk.Label()
        dataLabel.set_markup("<span foreground='#333333' size='%s'>%s</span>" % (LABEL_FONT_SIZE, commentDate))
        dataLabel.set_alignment(1.0, 0.5)
        infoBox.pack_start(dataLabel)
        
        textView = gtk.TextView()
        textView.set_editable(False)
        textView.set_wrap_mode(gtk.WRAP_WORD)
        textBuffer = textView.get_buffer()
        textBuffer.set_text(commentContent)
        rightBox.pack_start(textView)
        
        line = gtk.Image()
        drawLine(line, "#DDDDDD", 1, False, LINE_BOTTOM)
        commentBox.pack_start(line)
            
        return commentAlign
    
    def updateDownloadingStatus(self, pkgName, progress, feedback):
        '''Update downloading status.'''
        if utils.getPkgName(self.appInfo.pkg) == pkgName:
            self.appInfoItem.updateDownloadingStatus(progress, feedback)
            
    def updateInstallingStatus(self, pkgName, progress, feedback):
        '''Update installing status.'''
        if utils.getPkgName(self.appInfo.pkg) == pkgName:
            self.appInfoItem.updateInstallingStatus(progress, feedback)
            
    def updateUpgradingStatus(self, pkgName, progress, feedback):
        '''Update upgrading status.'''
        if utils.getPkgName(self.appInfo.pkg) == pkgName:
            self.appInfoItem.updateUpgradingStatus(progress, feedback)
            
    def updateUninstallingStatus(self, pkgName, progress, feedback):
        '''Update upgrading status.'''
        if utils.getPkgName(self.appInfo.pkg) == pkgName:
            self.appInfoItem.updateUninstallingStatus(progress, feedback)
            
    def switchToStatus(self, pkgName, appStatus):
        '''Switch to downloading status.'''
        if utils.getPkgName(self.appInfo.pkg) == pkgName:
            self.appInfoItem.appInfo.status = appStatus
            self.appInfoItem.initAdditionStatus()
            
    def initNormalStatus(self, pkgName, isMarkDeleted):
        '''Init normal status.'''
        if isMarkDeleted:
            self.switchToStatus(pkgName, APP_STATE_NORMAL)
        else:
            self.switchToStatus(pkgName, APP_STATE_INSTALLED)
            
    def updateInfo(self, voteJson):
        '''Update detail information.'''
        # Get info.
        pkgName = utils.getPkgName(self.appInfo.pkg)
        softInfo = voteJson[pkgName]
        commentList = voteJson["comment_list"]
        
        starLevel = softInfo["mark"]
        voteNum = softInfo["vote_nums"]
        commentNum = softInfo["comment_nums"]
        
        # Update mark and vote number.
        appStar = createStarBox(starLevel, 24)
        appStarAlign = gtk.Alignment()
        appStarAlign.set(0.0, 0.5, 0.0, 0.0)
        appStarAlign.add(appStar)
        self.appNameBox.pack_start(appStarAlign, False, False, self.STAR_PADDING_X)
        
        if voteNum > 0:
            appVoteNum = gtk.Label()
            appVoteNum.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "(%s 人参与了评分)" % (voteNum)))
            appVoteAlign = gtk.Alignment()
            appVoteAlign.set(0.0, 1.0, 0.0, 0.0)
            appVoteAlign.add(appVoteNum)
            self.appNameBox.pack_start(appVoteAlign, False, False)
        
        # Update comment list.
        utils.containerRemoveAll(self.commentAreaBox)
        
        commentTitleBox = gtk.HBox()
        self.commentAreaBox.pack_start(commentTitleBox)
        
        commentLabel = gtk.Label()
        commentLabel.set_markup("<span foreground='#1A3E88' size='%s'><b>用户评论</b></span>" % (LABEL_FONT_LARGE_SIZE))
        commentLabelAlign = gtk.Alignment()
        commentLabelAlign.set(0.0, 1.0, 0.0, 0.0)
        commentLabelAlign.set_padding(self.COMMENT_PADDING_TOP, self.COMMENT_PADDING_BOTTOM, 0, 0)
        commentLabelAlign.add(commentLabel)
        commentTitleBox.pack_start(commentLabelAlign, False, False)
        
        # Temp send comment entry.
        commentViewHeight = 60
        self.commentView = gtk.TextView()
        self.commentView.set_size_request(-1, commentViewHeight)
        commentViewFrame = gtk.Frame()
        commentViewFrame.add(self.commentView)
        self.commentAreaBox.pack_start(commentViewFrame)
        
        sendCommentBox = gtk.HBox()
        self.commentAreaBox.pack_start(sendCommentBox)
        
        self.sendCommentSpinnerBox = gtk.VBox()
        sendCommentSpinnerAlign = gtk.Alignment()
        sendCommentSpinnerAlign.set(1.0, 0.5, 0.0, 0.0)
        sendCommentSpinnerAlign.set_padding(0, 0, 10, 10)
        sendCommentSpinnerAlign.add(self.sendCommentSpinnerBox)
        sendCommentBox.pack_start(sendCommentSpinnerAlign)
        
        (sendCommentButton, sendCommentAlign) = newActionButton(
            "update_selected", 1.0, 0.5, 
            "cell", True, "发表评论", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF",
            5
            )
        sendCommentButton.connect("button-press-event", lambda w, e: self.sendComment())
        sendCommentBox.pack_start(sendCommentAlign, False, False)
        
        if commentNum > 0:
            self.commentNumLabel = gtk.Label()
            self.commentNumLabel.set_markup(
                "<span foreground='#000000' size='%s'>%s 人参与了讨论</span>" % (LABEL_FONT_SIZE, commentNum))
            commentNumLabelAlign = gtk.Alignment()
            commentNumLabelAlign.set(1.0, 1.0, 0.0, 0.0)
            commentNumLabelAlign.set_padding(self.COMMENT_PADDING_TOP, self.COMMENT_PADDING_BOTTOM, 0, 0)
            commentNumLabelAlign.add(self.commentNumLabel)
            commentTitleBox.pack_start(commentNumLabelAlign)
            
        line = gtk.Image()
        drawLine(line, "#DDDDDD", 1, False, LINE_BOTTOM)
        self.commentAreaBox.pack_start(line)
            
        if len(commentList) == 0:
            notifyPaddingY = 20
            commentNotifyLabel = gtk.Label()
            commentNotifyLabel.set_markup(
                "<span foreground='#1A3E88' size='%s'><b>还不快抢沙发?</b></span>" % (LABEL_FONT_X_LARGE_SIZE))
            self.commentNotifyAlign = gtk.Alignment()
            self.commentNotifyAlign.set(0.5, 0.5, 0.0, 0.0)
            self.commentNotifyAlign.set_padding(notifyPaddingY, notifyPaddingY, 0, 0)
            self.commentNotifyAlign.add(commentNotifyLabel)
            self.commentAreaBox.pack_start(self.commentNotifyAlign)
        else:
            # Add comment list.
            self.commentAreaBox.pack_start(self.commentListBox)
            self.addCommentList(commentList, commentNum, True)
        
        self.scrolledWindow.show_all()
        
    def addCommentList(self, commentList, commentNum, firstTime=False):
        '''Add comment list.'''
        # Add comment list.
        for comment in commentList:
            commentName = comment["cuid"]
            commentIcon = "./icons/comment/me.png"
            commentDate = comment["ctime"]
            commentContent = comment["content"]
            
            commentBox = self.createComment((commentName, commentIcon, commentDate, commentContent))
            self.commentListBox.pack_start(commentBox, False, False)
            
        self.lastCommentId = commentList.pop()["cid"]
        
        # Add read more button.
        if self.readMoreAlign != None and self.readMoreAlign.get_parent() != None:
            self.commentAreaBox.remove(self.readMoreAlign)
        
        if (firstTime and commentNum > 20) or commentNum >= 20:
            (readMoreButton, self.readMoreAlign) = newActionButton(
                "update_selected", 1.0, 0.5, 
                "cell", True, "查看更多的评论", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF",
                20
                )
            self.commentAreaBox.pack_start(self.readMoreAlign, False, False)
            readMoreButton.connect("button-press-event", lambda w, e: self.fetchMoreComment())
            
    def sendComment(self):
        '''Send comment.'''
        # Get comment.
        commentBuffer = self.commentView.get_buffer()
        (startIter, endIter) = (commentBuffer.get_start_iter(), commentBuffer.get_end_iter())
        commentInput = commentBuffer.get_text(startIter, endIter)
        
        if len(commentInput.strip()) > 0:        
            comment = base64.b64encode(commentInput)
            commentBuffer.delete(startIter, endIter) # delete comment.
            
            # Get package name.
            pkgName = utils.getPkgName(self.appInfo.pkg)
            
            # Get user name.
            userName = base64.b64encode("深度Linuxer %s" % (time.ctime()))
            
            self.createSendCommentSpinner()
            sendCommentThread = SendComment(pkgName, userName, comment, 
                                            self.sendCommentSuccess, self.sendCommentFailed)    
            sendCommentThread.start()
        else:
            print "Don't allowed send blank comment."
            
    def createSendCommentSpinner(self):
        '''Create send comment spinner.'''
        utils.containerRemoveAll(self.sendCommentSpinnerBox)            
        self.sendCommentSpinner = gtk.Spinner()
        self.sendCommentSpinner.start()
        self.sendCommentSpinnerBox.pack_start(self.sendCommentSpinner, True, True)
        self.sendCommentSpinnerBox.show_all()
            
    @postGUI
    def sendCommentSuccess(self, pkgName, comment, userName):
        '''Send comment success.'''
        # Remove spinner box first.
        utils.containerRemoveAll(self.sendCommentSpinnerBox)            
        
        # Message.
        self.messageCallback("发表 %s 评论成功" % (pkgName))
        
        # Add comment in comment list.
        commentIcon = "./icons/comment/me.png"
        commentDate = utils.getCurrentTime()
        commentName = "深度Linuxer %s" % (commentDate)
        commentBox = self.createComment((
                commentName, 
                commentIcon, 
                commentDate, 
                base64.b64decode(comment)))
        
        # Remove notify widget if have it.
        if self.commentNotifyAlign != None:
            self.commentAreaBox.remove(self.commentNotifyAlign)
            self.commentAreaBox.pack_start(self.commentListBox)
        
        # Connect widget.
        self.commentListBox.pack_start(commentBox, False, False)
        self.commentListBox.reorder_child(commentBox, 0)

        self.commentAreaBox.show_all()
        
    @postGUI
    def sendCommentFailed(self, pkgName):
        '''Send comment failed.'''
        utils.containerRemoveAll(self.sendCommentSpinnerBox)            
        
        self.messageCallback("发表 %s 评论失败， 请检查你的网络链接" % (pkgName))
        
    def fetchMoreComment(self):
        '''Fetch more comment.'''
        FetchCommentThread = FetchMoreComment(
            self.pageId, 
            utils.getPkgName(self.appInfo.pkg),
            self.lastCommentId,
            self.updateMoreCommentCallback)
        FetchCommentThread.start()
        
    def updateMoreComment(self, voteJson):
        '''Update more comment.'''
        pkgName = utils.getPkgName(self.appInfo.pkg)
        commentList = voteJson["comment_list"]
        
        if len(commentList) == 0 and self.readMoreAlign != None:
            self.commentAreaBox.remove(self.readMoreAlign)
        else:
            # Add comment list.
            self.addCommentList(commentList, len(commentList))
                
        self.scrolledWindow.show_all()
        
class SendComment(td.Thread):
    '''Send comment.'''
	
    def __init__(self, pkgName, userName, comment, 
                 successCallback, failedCallback):
        '''Init for fetch detail.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        self.pkgName = pkgName
        self.userName = userName
        self.comment = comment
        self.successCallback = successCallback
        self.failedCallback = failedCallback
        
    def run(self):
        '''Run'''
        # try:
        args = {'n':self.pkgName, 'c':self.comment, 'u':self.userName}
        
        # try:
        connection = urllib2.urlopen(
            "http://test-linux.gteasy.com/comment.php?",
            data=urllib.urlencode(args),
            timeout=POST_TIMEOUT)
        self.successCallback(self.pkgName, self.comment, self.userName)
        # except Exception, e:
        #     self.failedCallback(self.pkgName)
            
class FetchMoreComment(td.Thread):
    '''Fetch more comment.'''
	
    def __init__(self, pageId, pkgName, lastCommentId, updateMoreCommentCallback):
        '''Init for fetch detail.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        self.pageId  = pageId
        self.pkgName = pkgName
        self.lastCommentId = lastCommentId
        self.updateMoreCommentCallback = updateMoreCommentCallback

    def run(self):
        '''Run'''
        try:
            connection = urllib2.urlopen(
                "http://test-linux.gteasy.com/getComment.php?n=%s&cid=%s" % (self.pkgName, self.lastCommentId), 
                timeout=GET_TIMEOUT)
            voteJson = json.loads(connection.read())        
            self.updateMoreCommentCallback(self.pageId, self.pkgName, voteJson)
        except Exception, e:
            print "Fetch more comment data failed."
        
def createContentView(content, editable=True):
    '''Create summary view.'''
    textView = gtk.TextView()
    textView.set_editable(editable)
    textView.set_wrap_mode(gtk.WRAP_CHAR)
    textBuffer = textView.get_buffer()
    textBuffer.set_text(content)

    return textView

class AppInfoItem(DownloadItem):
    '''Application information item.'''
	
    ICON_SIZE = 48
    STAR_PADDING_X = 20
    INFO_PADDING_Y = 3
    EXTRA_PADDING_X = 20
    ALIGN_X = 20
    
    def __init__(self, aptCache, appInfo, switchStatus, downloadQueue, actionQueue):
        '''Init for application item.'''
        DownloadItem.__init__(self, appInfo, switchStatus, downloadQueue)
        
        self.aptCache = aptCache
        self.itemFrame = gtk.VBox()
        self.itemBox = gtk.HBox()
        itemEventBox = gtk.EventBox()
        itemEventBox.add(self.itemBox)
        itemEventBox.connect("expose-event", lambda w, e: drawBackground(w, e, "#6FA2FE", "#6085C7"))
        itemAlign = gtk.Alignment()
        itemAlign.set_padding(0, 0, self.ALIGN_X, self.ALIGN_X)
        itemAlign.set(0.0, 0.5, 1.0, 1.0)
        itemAlign.add(itemEventBox)
        self.itemFrame.add(itemAlign)
        self.actionQueue = actionQueue
        
        # Widget that status will change.
        self.installingProgressbar = None
        self.installingFeedbackLabel = None
        self.upgradingProgressbar = None
        self.upgradingFeedbackLabel = None
        self.uninstallingProgressbar = None
        self.uninstallingFeedbackLabel = None
        
        pkg = appInfo.pkg
        pkgName = utils.getPkgName(pkg)
        
        topLeftBox = gtk.HBox()
        self.itemBox.pack_start(topLeftBox, False, False)
        self.appAdditionBox = gtk.HBox()
        appAdditionAlign = gtk.Alignment()
        appAdditionAlign.add(self.appAdditionBox)
        appAdditionAlign.set(1.0, 0.5, 0.0, 0.0)
        self.itemBox.pack_start(appAdditionAlign)

        # Add application version.
        self.appExtraBox = gtk.VBox()
        topLeftBox.pack_start(self.appExtraBox, False, False, self.EXTRA_PADDING_X)
        
        # Init basic status.
        self.initBasicStatus()

        # Init addition status.
        self.initAdditionStatus()

    def initBasicStatus(self):
        '''Init basic status.'''
        pkg = self.appInfo.pkg
        
        # Clean container first.
        utils.containerRemoveAll(self.appExtraBox)

        # Add application version.
        appVersion = gtk.Label()
        appVersion.set_markup(
            "版本: <span foreground='#FFFFFF' size='%s'>%s</span>" % (LABEL_FONT_SIZE, utils.getPkgVersion(pkg)))
        appVersion.set_alignment(0.0, 0.5)
        self.appExtraBox.pack_start(appVersion, False, False, self.INFO_PADDING_Y)

        # Add size information.
        appSizeBox = gtk.HBox()
        self.appExtraBox.pack_start(appSizeBox, False, False, self.INFO_PADDING_Y)
        if self.appInfo.status == APP_STATE_INSTALLED:
            (_, releaseSize) = utils.getPkgDependSize(self.aptCache, pkg, ACTION_UNINSTALL)
            releaseSizeLabel = gtk.Label()
            releaseSizeLabel.set_markup("卸载后释放 <span foreground='#FFFFFF' size='%s'>%s</span> 空间"
                                        % (LABEL_FONT_SIZE, utils.formatFileSize(releaseSize)))
            releaseSizeLabel.set_alignment(0.0, 0.5)
            appSizeBox.pack_start(releaseSizeLabel, False, False)
        else:
            useSizeLabel = gtk.Label()
            useSizeLabel.set_alignment(0.0, 0.5)
            
            if self.appInfo.status == APP_STATE_UPGRADE:
                actionLabel = "升级"
                (downloadSize, useSize) = utils.getPkgDependSize(self.aptCache, pkg, ACTION_UPGRADE)
            else:
                actionLabel = "安装"
                (downloadSize, useSize) = utils.getPkgDependSize(self.aptCache, pkg, ACTION_INSTALL)
            useSizeLabel.set_markup("    %s后占用 <span foreground='#FFFFFF' size='%s'>%s</span> 空间" % 
                                    (actionLabel, LABEL_FONT_SIZE, utils.formatFileSize(useSize)))
                
            downloadSizeLabel = gtk.Label()
            downloadSizeLabel.set_markup(
                "需要下载 <span foreground='#FFFFFF' size='%s'>%s</span>" % (LABEL_FONT_SIZE, utils.formatFileSize(downloadSize)))
            downloadSizeLabel.set_alignment(0.0, 0.5)
            appSizeBox.pack_start(downloadSizeLabel, False, False)
                
            appSizeBox.pack_start(useSizeLabel, False, False)
            
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
        elif status == APP_STATE_UNINSTALLING:
            self.initUninstallingStatus()
            
        self.itemFrame.show_all()
        
    def initNormalStatus(self):
        '''Init normal status.'''
        pkg = self.appInfo.pkg
            
        # Clean right box first.
        utils.containerRemoveAll(self.appAdditionBox)
        
        # Add action button.
        appActionBox = gtk.VBox()
        if self.appInfo.status == APP_STATE_INSTALLED:
            appActionButton = utils.newButtonWithoutPadding()
            appActionButton.connect("button-release-event", lambda widget, event: self.switchToUninstalling())
            drawButton(appActionButton, "uninstall", "cell", False, "卸载", BUTTON_FONT_SIZE_SMALL)
        elif self.appInfo.status == APP_STATE_UPGRADE:
            appActionButton = utils.newButtonWithoutPadding()
            appActionButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            drawButton(appActionButton, "update", "cell", False, "升级", BUTTON_FONT_SIZE_SMALL)
        else:
            appActionButton = utils.newButtonWithoutPadding()
            appActionButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            drawButton(appActionButton, "install", "cell", False, "安装", BUTTON_FONT_SIZE_SMALL)
        appActionBox.pack_start(appActionButton, False, False)
        self.appAdditionBox.pack_start(appActionBox, False, False, self.EXTRA_PADDING_X)
        
    def initInstallingStatus(self):
        '''Init installing status.'''
        (progressbar, feedbackLabel) = initActionStatus(
            self.appAdditionBox, 
            self.appInfo.installingProgress,
            self.appInfo.installingFeedback)
        
        self.installingProgressbar = progressbar
        self.installingFeedbackLabel = feedbackLabel
        
    def initUpgradingStatus(self):
        '''Init upgrading status.'''
        (progressbar, feedbackLabel) = initActionStatus(
            self.appAdditionBox, 
            self.appInfo.upgradingProgress, 
            self.appInfo.upgradingFeedback)
        
        self.upgradingProgressbar = progressbar
        self.upgradingFeedbackLabel = feedbackLabel
        
    def initUninstallingStatus(self):
        '''Init uninstalling status.'''
        (progressbar, feedbackLabel) = initActionStatus(
            self.appAdditionBox, 
            self.appInfo.uninstallingProgress,
            self.appInfo.uninstallingFeedback)
        
        self.uninstallingProgressbar = progressbar
        self.uninstallingFeedbackLabel = feedbackLabel
        
    def switchToUninstalling(self):
        '''Switch to uninstalling.'''
        self.appInfo.status = APP_STATE_UNINSTALLING
        self.initAdditionStatus()
        self.actionQueue.addAction(utils.getPkgName(self.appInfo.pkg), ACTION_UNINSTALL)

    def updateInstallingStatus(self, progress, feedback):
        '''Update installing status.'''
        if self.appInfo.status == APP_STATE_INSTALLING:
            if self.installingProgressbar != None and self.installingFeedbackLabel != None:
                self.installingProgressbar.setProgress(progress)
                self.installingFeedbackLabel.set_text("安装中")
                
                self.itemFrame.show_all()
                
    def updateUpgradingStatus(self, progress, feedback):
        '''Update upgrading status.'''
        if self.appInfo.status == APP_STATE_UPGRADING:
            if self.upgradingProgressbar != None and self.upgradingFeedbackLabel != None:
                self.upgradingProgressbar.setProgress(progress)
                self.upgradingFeedbackLabel.set_text("升级中")
                
                self.itemFrame.show_all()
                
    def updateUninstallingStatus(self, progress, feedback):
        '''Update uninstalling status.'''
        if self.appInfo.status == APP_STATE_UNINSTALLING:
            if self.uninstallingProgressbar != None and self.uninstallingFeedbackLabel != None:
                self.uninstallingProgressbar.setProgress(progress)
                self.uninstallingFeedbackLabel.set_text("卸载中")
                
                self.itemFrame.show_all()
                
class FetchScreenshot(td.Thread):
    '''Fetch screenshot.'''
	
    def __init__(self, appInfo, noscreenshotList, imageBox, image, width, height):
        '''Init for fetch screenshot.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        
        self.appInfo = appInfo
        self.imageBox = imageBox
        self.image = image
        self.proc = None
        self.returnCode = DOWNLOAD_FAILED
        self.width = width
        self.height = height
        self.noscreenshotList = noscreenshotList
        self.killed = False
        
    def stop(self):
        '''Stop download.'''
        if self.proc != None and self.returnCode == DOWNLOAD_FAILED:
            self.killed = True
            self.proc.kill()
            
    def run(self):
        '''Run'''
        # Add wait widget.
        padding = 40
        utils.containerRemoveAll(self.imageBox)
        waitSpinner = gtk.Spinner()
        waitSpinner.start()
        waitAlign = gtk.Alignment()
        waitAlign.set(0.5, 0.5, 1.0, 1.0)
        waitAlign.set_padding(padding, padding, padding, padding)
        waitAlign.add(waitSpinner)
        self.imageBox.add(waitAlign)
        
        # Download screenshot.
        pkgName = utils.getPkgName(self.appInfo.pkg)
        screenshotPath = SCREENSHOT_DOWNLOAD_DIR + pkgName
        
        cmdline = [
            'aria2c',
            "--dir=" + SCREENSHOT_DOWNLOAD_DIR,
            "http://screenshots.debian.net/screenshot/" + pkgName,
            '--auto-file-renaming=false',
            '--summary-interval=0',
            '--no-conf',
            '--remote-time=true',
            '--auto-save-interval=0',
            '--continue',    
            ]
        
        self.proc = subprocess.Popen(cmdline)
        self.returnCode = self.proc.wait()
        
        # Stop waiting widget.
        utils.containerRemoveAll(self.imageBox)
        self.imageBox.add(self.image)
        self.imageBox.show_all()
        
        # Set screenshot.
        if self.returnCode == DOWNLOAD_SUCCESS:
            self.image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(screenshotPath, self.width, self.height))
        else:
            if self.killed:
                pkgName = utils.getPkgName(self.appInfo.pkg)
                screenshotPath = SCREENSHOT_DOWNLOAD_DIR + pkgName
                if os.path.exists (screenshotPath):
                    os.remove(screenshotPath)
                    
                print "Download process stop."
            else:
                # Add in black list if haven't found screenshot.
                # Avoid send fetch request again. 
                if not pkgName in self.noscreenshotList: 
                    self.noscreenshotList.append(pkgName)
                    
                # Set upload image.
                self.image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file("./icons/screenshot/upload.png"))
            
                print "Haven't screenshot for %s !" % (pkgName)

class BigScreenshot:
    '''Big screenshot.'''
	
    def __init__(self, widget, screenshotPath, exitCallback):
        '''Init for big screenshot.'''
        self.closeIconWidth = 11
        self.closeIconHeight = 10
        self.borderWidth = 4
        self.borderTopHeight = 26
        self.borderBottomHeight = 7
        self.borderTopWidth = 7
        self.borderBottomWidth = 7
        
        self.topleftPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_topleft.png")
        self.toprightPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_topright.png")
        self.topmiddlePixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_topmiddle.png")
        self.bottomleftPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_bottomleft.png")
        self.bottomrightPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_bottomright.png")
        self.bottommiddlePixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_bottommiddle.png")
        self.leftPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_left.png")
        self.rightPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/background_right.png")
        
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(True)
        self.window.set_transient_for(widget.get_toplevel())
        self.window.set_property("accept-focus", False)
        
        (wx, wy) = widget.window.get_origin()
        rect = widget.get_allocation()
        self.requestWidth = rect.width * 4 / 5
        self.requestHeight = rect.height * 4 / 5
        self.pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
            screenshotPath, 
            self.requestWidth,
            self.requestHeight)
        self.eventbox = gtk.EventBox()
        self.window.add(self.eventbox)
        self.width = self.pixbuf.get_width()
        self.height = self.pixbuf.get_height()
        self.windowWidth = self.width + self.borderWidth * 2
        self.windowHeight = self.height + self.borderTopHeight + self.borderBottomHeight
        self.windowX = wx + rect.x + (rect.width - self.width) / 2 - self.borderWidth
        self.windowY = wy + rect.y + (rect.height - self.height) / 2 - self.borderTopHeight
        self.closeIconAdjust = 8
        self.closeIconX = self.windowX + self.windowWidth - self.closeIconWidth - self.closeIconAdjust
        self.closeIconY = self.windowY + self.closeIconAdjust
        self.window.move(self.windowX, self.windowY)
        self.window.set_default_size(self.windowWidth, self.windowHeight)
        
        self.window.connect("destroy", lambda w: exitCallback())
        self.window.connect("button-press-event", self.click)
        self.eventbox.connect("expose-event", self.show)
        
        self.window.show_all()

    def exit(self):
        '''Exit'''
        self.window.destroy()

        
    def click(self, widget, event):
        '''Click.'''
        point = event.get_root_coords()
        if point != ():
            (px, py) = point
            if utils.isInRect(
                (px, py), 
                (self.closeIconX, self.closeIconY,
                 self.closeIconWidth, self.closeIconHeight)):
                self.exit()
        
    def show(self, widget, event):
        '''Show.'''
        allocation = widget.get_allocation()
        
        windowWidth, windowHeight = allocation.width, allocation.height
        middleHeight = windowHeight - self.borderTopHeight - self.borderBottomHeight
        
        topmiddlePixbuf = self.topmiddlePixbuf.scale_simple(
            windowWidth - self.borderTopWidth * 2, 
            self.borderTopHeight, 
            gtk.gdk.INTERP_BILINEAR)
        bottommiddlePixbuf = self.bottommiddlePixbuf.scale_simple(
            windowWidth - self.borderBottomWidth * 2, 
            self.borderBottomHeight,
            gtk.gdk.INTERP_BILINEAR)
        leftPixbuf = self.leftPixbuf.scale_simple(
            self.borderWidth,
            middleHeight,
            gtk.gdk.INTERP_BILINEAR
            )
        rightPixbuf = self.rightPixbuf.scale_simple(
            self.borderWidth,
            middleHeight,
            gtk.gdk.INTERP_BILINEAR
            )
        middlePixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 
                                      False, 8, 
                                      windowWidth, middleHeight)
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, windowWidth, windowHeight)
        
        self.topleftPixbuf.copy_area(
            0, 0, self.borderTopWidth, self.borderTopHeight, pixbuf,
            0, 0)
        topmiddlePixbuf.copy_area(
            0, 0, windowWidth - self.borderTopWidth * 2, self.borderTopHeight, pixbuf, 
            self.borderTopWidth, 0)
        self.toprightPixbuf.copy_area(
            0, 0, self.borderTopWidth, self.borderTopHeight, pixbuf,
            windowWidth - self.borderTopWidth, 0)
        self.bottomleftPixbuf.copy_area(
            0, 0, self.borderBottomWidth, self.borderBottomHeight, pixbuf,
            0, windowHeight - self.borderBottomHeight)
        bottommiddlePixbuf.copy_area(
            0, 0, windowWidth - self.borderBottomWidth * 2, self.borderBottomHeight, pixbuf, 
            self.borderBottomWidth, self.windowHeight - self.borderBottomHeight)
        self.bottomrightPixbuf.copy_area(
            0, 0, self.borderBottomWidth, self.borderBottomHeight, pixbuf,
            windowWidth - self.borderBottomWidth, windowHeight - self.borderBottomHeight)
        middlePixbuf.copy_area(0, 0, windowWidth, middleHeight, pixbuf, 
                               0, self.borderTopHeight)
        leftPixbuf.copy_area(0, 0, self.borderWidth, middleHeight, pixbuf, 
                             0, self.borderTopHeight)
        rightPixbuf.copy_area(0, 0, self.borderWidth, middleHeight, pixbuf, 
                              windowWidth - self.borderWidth,
                              self.borderTopHeight)
        self.pixbuf.copy_area(0, 0, self.width, self.height, pixbuf, self.borderWidth, self.borderTopHeight)
        
        cr = widget.window.cairo_create()
        cr.set_source_pixbuf(pixbuf, 0, 0)
        cr.paint()
        
        closePixbuf = gtk.gdk.pixbuf_new_from_file("./icons/screenshot/close.png")
        cr.set_source_pixbuf(closePixbuf, 
                             self.windowWidth - self.closeIconWidth - self.closeIconAdjust,
                             self.closeIconAdjust)
        cr.paint()
        
        # (_, mask) = pixbuf.render_pixmap_and_mask(255)
        # if mask != None:
        #     self.window.shape_combine_mask(mask, 0, 0)

        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)

        return True
