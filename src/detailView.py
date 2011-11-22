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

from lang import __
from utils import *
from theme import *
from appItem import *
from draw import *
from constant import *
from draw import *
from math import pi
import browser
import copy
import zipfile
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

(ARIA2_MAJOR_VERSION, ARIA2_MINOR_VERSION, _) = utils.getAria2Version()

class DetailView(object):
    '''Detail view.'''

    PADDING = 10
    EXTRA_PADDING_X = 20
    LANGUAGE_BOX_PADDING = 3
    DETAIL_PADDING_X = 10
    ALIGN_X = 20
    ALIGN_Y = 10
    STAR_PADDING_X = 10
    INFO_PADDING_Y = 3

    def __init__(self, aptCache, pageId, appInfo, 
                 switchStatus, downloadQueue, actionQueue,
                 exitCallback, 
                 messageCallback):
        '''Init for detail view.'''
        # Init.
        self.aptCache = aptCache
        self.pageId = pageId
        self.appInfo = appInfo
        pkg = appInfo.pkg
        self.readMoreBox = gtk.HBox()
        self.readMoreAlign = None
        self.messageCallback = messageCallback
        self.smallScreenshot = None
        
        self.box = gtk.VBox()
        self.eventbox = gtk.EventBox()
        self.eventbox.add(self.box)
        self.eventbox.connect("expose-event", lambda w, e: drawBackground(w, e, appTheme.getDynamicColor("background")))
        
        self.align = gtk.Alignment()
        self.align.set(0.0, 0.0, 1.0, 1.0)
        self.align.set_padding(0, 0, 0, 0)
        self.align.add(self.eventbox)
       
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.scrolledWindow.connect(
            "hierarchy-changed", 
            lambda w, t: self.smallScreenshot.toggleBigScreenshot())
        drawVScrollbar(self.scrolledWindow)
        utils.addInScrolledWindow(self.scrolledWindow, self.align)
        
        # Add title bar.
        titleBox = gtk.HBox()
        titleEventbox = gtk.EventBox()
        titleEventbox.add(titleBox)
        self.box.pack_start(titleEventbox, False, False)
        eventBoxSetBackground(
            titleEventbox,
            True, False,
            appTheme.getDynamicPixbuf("detail/background.png"))

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
        appNameAlign = gtk.Alignment()
        appNameLabel = DynamicSimpleLabel(
            appNameAlign,
            "<b>%s</b>" % (pkgName),
            appTheme.getDynamicColor("detailName"),
            LABEL_FONT_XXX_LARGE_SIZE,
            )
        appName = appNameLabel.getLabel()
        
        appNameAlign.set(0.0, 0.5, 0.0, 0.0)
        appNameAlign.add(appName)
        
        self.appNameBox.pack_start(appNameAlign, False, False)
        
        appIntroAlign = gtk.Alignment()
        appIntroLabel = DynamicSimpleLabel(
            appIntroAlign,
            utils.getPkgShortDesc(pkg),
            appTheme.getDynamicColor("detailSummary"),
            LABEL_FONT_LARGE_SIZE,
            )
        appIntro = appIntroLabel.getLabel()
        appIntroAlign.set(0.0, 0.0, 0.0, 0.0)
        appIntroAlign.add(appIntro)
        appMiddleBox.pack_start(appIntroAlign, False, False)
        
        # Add return button.
        self.returnButton = utils.newButtonWithoutPadding()
        self.returnButton.connect("button-release-event", lambda widget, event: exitCallback(pageId, utils.getPkgName(pkg)))
        drawButton(self.returnButton, "return", "cell", False, __("Return"), BUTTON_FONT_SIZE_MEDIUM, "bigButtonFont")
        
        buttonPaddingTop = 20
        buttonPaddingRight = 20
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
        
        # Content box.
        self.contentBox = gtk.VBox()
        self.bodyBox.pack_start(self.contentBox, False, False)
        
        self.infoTab = self.createInfoTab(appInfo, pkg)
        
        self.commentArea = browser.Browser("%s/softcenter/v1/comment?n=%s" % (SERVER_ADDRESS, pkgName))
        self.commentAreaAlign = gtk.Alignment()
        self.commentAreaAlign.set(0.0, 0.0, 1.0, 1.0)
        self.commentAreaAlign.set_padding(self.ALIGN_Y, 0, self.ALIGN_X, self.ALIGN_X)
        self.commentAreaAlign.add(self.commentArea)
        self.commentArea.connect("console-message", lambda view, message, line, sourceId: self.scrollCommentAreaToTop(message))
        
        # Set small width to avoid comment area can't shrink window when main window shrink.
        self.commentArea.set_size_request(DEFAULT_WINDOW_WIDTH / 2, -1) 
        
        self.contentBox.pack_start(self.infoTab)
        self.contentBox.pack_start(self.commentAreaAlign)
        self.contentBox.show_all()
        
        self.scrolledWindow.show_all()
        
    def scrollCommentAreaToTop(self, message):
        '''Scroll comment area to top.'''
        if message in ["home", "end", "next", "prev"]:
            vadj = self.scrolledWindow.get_vadjustment()
            (_, offsetY) = self.commentArea.translate_coordinates(self.scrolledWindow, 0, 0)
            currentY = vadj.get_value()
            vadj.set_value(currentY + offsetY)
        
    def createInfoTab(self, appInfo, pkg):
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
        summaryDLabel = DynamicSimpleLabel(
            detailBox,
            "<b>%s</b>" % (__("Long Description")),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_LARGE_SIZE,
            )
        summaryLabel = summaryDLabel.getLabel()
        summaryLabel.set_alignment(0.0, 0.5)
        detailBox.pack_start(summaryLabel, False, False)
        
        summaryAlign = gtk.Alignment()
        summaryView = createContentView(summaryAlign, utils.getPkgLongDesc(pkg), False)
        summaryAlign.set(0.0, 0.0, 1.0, 1.0)
        summaryAlign.set_padding(summaryAlignTop, 0, 0, summaryAlignRight)
        summaryAlign.add(summaryView)
        detailBox.pack_start(summaryAlign)
        
        homepage = utils.getPkgHomepage(pkg)
        if homepage != "":
            homepageAlignY = 20
            (homepageLabel, homepageEventBox) = setDefaultClickableDynamicLabel(
                __("Homepage"),
                "link",
                )
            homepageLabel.set_alignment(0.0, 0.0)
            homepageEventBox.connect("button-press-event", lambda w, e: utils.sendCommand("xdg-open %s" % (homepage)))
            detailBox.pack_start(homepageEventBox, False, False)
            
            # Show home page when hover link.
            utils.setHelpTooltip(homepageEventBox, homepage)
            
        # Add help translation.
        lang = utils.getDefaultLanguage()
        if lang == "zh_CN":
            translationAlignY = 20
            (translationLabel, translationEventBox) = setDefaultClickableDynamicLabel(
                __("Translate description"),
                "link"
                )
            translationLabel.set_alignment(0.0, 0.0)
            translationEventBox.connect(
                "button-press-event", 
                lambda w, e: utils.sendCommand("xdg-open http://pootle.linuxdeepin.com/zh_CN/ddtp-done/%s.po/translate/" % (pkgName)))
            detailBox.pack_start(translationEventBox, False, False)
            
            # Show translation  when hover link.
            utils.setHelpTooltip(translationEventBox, __("Translate description"))
        
        # Add screenshot.
        screenshotBox = gtk.VBox()
        
        screenshotDLabel = DynamicSimpleLabel(
            screenshotBox,
            "<b>%s</b>" % (__("Screenshot")),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_LARGE_SIZE,
            )
        screenshotLabel = screenshotDLabel.getLabel()
        
        screenshotLabel.set_alignment(0.0, 0.5)
        screenshotBox.pack_start(screenshotLabel, False, False)
        
        self.smallScreenshot = SmallScreenshot(pkgName, self.scrolledWindow)
        screenshotBox.pack_start(self.smallScreenshot.box, False, False)
        self.smallScreenshot.start()
        
        infoBox.pack_start(screenshotBox, False, False, self.DETAIL_PADDING_X)
            
        # Make sure download thread stop when detail view destroy.
        self.returnButton.connect(
            "button-release-event", 
            lambda widget, event: self.smallScreenshot.stop())
        self.returnButton.connect(
            "button-release-event", 
            lambda widget, event: self.smallScreenshot.closeBigScreenshotWindow())
        self.returnButton.connect("destroy", lambda widget: self.smallScreenshot.stop())

        return align
    
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
            
def createContentView(parent, content, editable=True):
    '''Create summary view.'''
    dTextView = DynamicTextView(
        parent,
        appTheme.getDynamicColor("background"),
        appTheme.getDynamicColor("foreground"),
        )
    textView = dTextView.textView
    textView.modify_font(pango.FontDescription("%s %s" % (DEFAULT_FONT, DEFAULT_FONT_SIZE)))
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
        itemEventBox.set_visible_window(False)
        itemEventBox.add(self.itemBox)
        drawDetailItemBackground(itemEventBox)
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
        appVersionLabel = DynamicSimpleLabel(
            self.appExtraBox,
            __("Version: ") + utils.getPkgVersion(pkg),
            appTheme.getDynamicColor("detailAction"),
            LABEL_FONT_MEDIUM_SIZE,
            )
        appVersion = appVersionLabel.getLabel()
        appVersion.set_alignment(0.0, 0.5)
        self.appExtraBox.pack_start(appVersion, False, False, self.INFO_PADDING_Y)

        # Add size information.
        appSizeBox = gtk.HBox()
        self.appExtraBox.pack_start(appSizeBox, False, False, self.INFO_PADDING_Y)
        if self.appInfo.status == APP_STATE_INSTALLED:
            (_, rSize) = utils.getPkgDependSize(self.aptCache, pkg, ACTION_UNINSTALL)
            uninstallSizeLabel = DynamicSimpleLabel(
                appSizeBox,
                (__("Uninstall to release %s space") % (utils.formatFileSize(rSize))),
                appTheme.getDynamicColor("detailAction"),
                LABEL_FONT_MEDIUM_SIZE,
                )
            uninstallSize = uninstallSizeLabel.getLabel()
            uninstallSize.set_alignment(0.0, 0.5)
            appSizeBox.pack_start(uninstallSize, False, False)
        else:
            useSizeLabel = gtk.Label()
            useSizeLabel.set_alignment(0.0, 0.5)
            
            if self.appInfo.status == APP_STATE_UPGRADE:
                actionLabel = __("Action Update")
                (downloadSize, useSize) = utils.getPkgDependSize(self.aptCache, pkg, ACTION_UPGRADE)
            else:
                actionLabel = __("Action Install")
                (downloadSize, useSize) = utils.getPkgDependSize(self.aptCache, pkg, ACTION_INSTALL)

            updateSizeLabel = DynamicSimpleLabel(
                appSizeBox,
                (__("Download to eat %s space") % (actionLabel, utils.formatFileSize(useSize), utils.formatFileSize(downloadSize))),
                appTheme.getDynamicColor("detailAction"),
                LABEL_FONT_MEDIUM_SIZE,
                )
            updateSize = updateSizeLabel.getLabel()
            updateSize.set_alignment(0.0, 0.5)
            appSizeBox.pack_start(updateSize, False, False)
            
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
            drawButton(appActionButton, "uninstall", "cell", False, __("Action Uninstall"), BUTTON_FONT_SIZE_SMALL, "buttonFont")
        elif self.appInfo.status == APP_STATE_UPGRADE:
            appActionButton = utils.newButtonWithoutPadding()
            appActionButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            drawButton(appActionButton, "update", "cell", False, __("Action Update"), BUTTON_FONT_SIZE_SMALL, "buttonFont")
        else:
            appActionButton = utils.newButtonWithoutPadding()
            appActionButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            drawButton(appActionButton, "install", "cell", False, __("Action Install"), BUTTON_FONT_SIZE_SMALL, "buttonFont")
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
        '''Init un-installing status.'''
        (progressbar, feedbackLabel) = initActionStatus(
            self.appAdditionBox, 
            self.appInfo.uninstallingProgress,
            self.appInfo.uninstallingFeedback)
        
        self.uninstallingProgressbar = progressbar
        self.uninstallingFeedbackLabel = feedbackLabel
        
    def switchToUninstalling(self):
        '''Switch to un-installing.'''
        self.appInfo.status = APP_STATE_UNINSTALLING
        self.initAdditionStatus()
        self.actionQueue.addAction(utils.getPkgName(self.appInfo.pkg), ACTION_UNINSTALL)

    def updateInstallingStatus(self, progress, feedback):
        '''Update installing status.'''
        if self.appInfo.status == APP_STATE_INSTALLING:
            if self.installingProgressbar != None and self.installingFeedbackLabel != None:
                self.installingProgressbar.setProgress(progress)
                self.installingFeedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, __("Action Installing")))
                
                self.itemFrame.show_all()
                
    def updateUpgradingStatus(self, progress, feedback):
        '''Update upgrading status.'''
        if self.appInfo.status == APP_STATE_UPGRADING:
            if self.upgradingProgressbar != None and self.upgradingFeedbackLabel != None:
                self.upgradingProgressbar.setProgress(progress)
                self.upgradingFeedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, __("Action Updating")))
                
                self.itemFrame.show_all()
                
    def updateUninstallingStatus(self, progress, feedback):
        '''Update un installing status.'''
        if self.appInfo.status == APP_STATE_UNINSTALLING:
            if self.uninstallingProgressbar != None and self.uninstallingFeedbackLabel != None:
                self.uninstallingProgressbar.setProgress(progress)
                self.uninstallingFeedbackLabel.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, __("Action Uninstalling")))
                
                self.itemFrame.show_all()
                
class FetchScreenshot(td.Thread):
    '''Fetch screenshot.'''
	
    def __init__(self, appInfo, imageBox, image, width, height):
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
        self.killed = False
        
    def stop(self):
        '''Stop download.'''
        if self.proc != None and self.returnCode == DOWNLOAD_FAILED:
            self.killed = True
            self.proc.kill()
            
    def run(self):
        '''Run'''
        # Add wait widget.
        utils.containerRemoveAll(self.imageBox)
        waitAlign = gtk.Alignment()
        waitAnimation = DynamicImage(
            waitAlign,
            appTheme.getDynamicPixbufAnimation("wait.gif"),
            ).image
        waitAlign.set(0.5, 0.5, 1.0, 1.0)
        waitAlign.add(waitAnimation)
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
            '--remote-time=true',
            '--auto-save-interval=0',
            ]
        
        # Make software center can work with aria2c 1.9.x.
        if ARIA2_MAJOR_VERSION >= 1 and ARIA2_MINOR_VERSION <= 9:
            cmdline.append("--no-conf")
            cmdline.append("--continue")
        else:
            cmdline.append("--no-conf=true")
            cmdline.append("--continue=true")
            
        # Append proxy configuration.
        proxyString = readFirstLine("./proxy", True)
        if proxyString != "":
            cmdline.append("=".join(["--all-proxy", proxyString]))
        
        self.proc = subprocess.Popen(cmdline)
        self.returnCode = self.proc.wait()
        
        # Stop waiting widget.
        utils.containerRemoveAll(self.imageBox)
        self.imageBox.add(self.image)
        self.imageBox.show_all()
        
        # Set screenshot.
        if self.returnCode == DOWNLOAD_SUCCESS:
            self.image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(screenshotPath, self.width, self.height))
            utils.setCustomizeClickableCursor(
                self.imageBox, 
                self.image, 
                appTheme.getDynamicPixbuf("screenshot/zoom_in.png"))
            utils.setHelpTooltip(self.imageBox, __("Click Zoom In"))
        else:
            if self.killed:
                pkgName = utils.getPkgName(self.appInfo.pkg)
                screenshotPath = SCREENSHOT_DOWNLOAD_DIR + pkgName
                if os.path.exists (screenshotPath):
                    os.remove(screenshotPath)
                    
                print "Download process stop."
            else:
                # Set upload image.
                self.image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file("../theme/default/image/screenshot/upload.png"))
            
                print "Haven't screenshot for %s !" % (pkgName)

class SmallScreenshot(td.Thread):
    '''Small screenshot.'''
	
    SMALL_SCREENSHOT_ROW = 3
    SMALL_SCREENSHOT_COLUMN = 3
    SCREENSHOT_WIDTH = 280
    SCREENSHOT_HEIGHT = 210
    SMALL_SCREENSHOT_WIDTH = 80
    SMALL_SCREENSHOT_HEIGHT = 60 
    SMALL_SCREENSHOT_PADDING_X = 10
    SMALL_SCREENSHOT_PADDING_Y = 10
    SCREENSHOT_MAX_NUM = 9
    
    def __init__(self, pkgName, scrolledWindow):
        '''Init small screenshot.'''
        # Init.
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        
        self.scrolledWindow = scrolledWindow
        self.images = []
        self.imageIndex = 0
        self.pkgName = pkgName
        self.proc = None
        self.box = gtk.VBox()
        self.topBox = gtk.HBox()
        self.topBox.set_size_request(self.SCREENSHOT_WIDTH, self.SCREENSHOT_HEIGHT)
        self.bottomBox = gtk.VBox()
        self.bigScreenshotImage = None
        self.bigScreenshot = None
        
        self.box.pack_start(self.topBox, False, False)
        self.box.pack_start(self.bottomBox, False, False)
        self.box.show_all()
        
    def toggleBigScreenshot(self):
        '''Toggle big screenshot.'''
        if self.bigScreenshot != None:
            if self.bigScreenshot.window.get_visible():
                self.bigScreenshot.hide()
            else:
                self.bigScreenshot.show()
        
    @postGUI
    def initWaitStatus(self):
        '''Init wait status.'''
        # Clean top box.
        utils.containerRemoveAll(self.topBox)
        
        # Init wait box.
        waitBox = gtk.HBox()
        waitAlign = gtk.Alignment()
        waitAlign.set(0.5, 0.5, 0.0, 0.0)
        waitAlign.add(waitBox)
        self.topBox.add(waitAlign)

        # Add wait animation.
        waitAnimation = DynamicImage(
            waitBox,
            appTheme.getDynamicPixbufAnimation("wait.gif"),
            ).image
        waitBox.pack_start(waitAnimation, False, False)

        # Add wait message.
        waitMessage = DynamicSimpleLabel(
            waitBox,
            __("Query screenshot ..."),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_SIZE,
            ).getLabel()
        waitBox.pack_start(waitMessage, False, False)
        
    @postGUI
    def initDownloadingStatus(self):
        '''Init downloading status.'''
        # Clean top box.
        utils.containerRemoveAll(self.topBox)
        
        # Init downloading box.
        downloadingBox = gtk.HBox()
        downloadingAlign = gtk.Alignment()
        downloadingAlign.set(0.5, 0.5, 0.0, 0.0)
        downloadingAlign.add(downloadingBox)
        self.topBox.add(downloadingAlign)

        # Add downloading animation.
        downloadingAnimation = DynamicImage(
            downloadingBox,
            appTheme.getDynamicPixbufAnimation("wait.gif"),
            ).image
        downloadingBox.pack_start(downloadingAnimation, False, False)

        # Add downloading message.
        downloadingMessage = DynamicSimpleLabel(
            downloadingBox,
            __("Downloading screenshot ..."),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_SIZE,
            ).getLabel()
        downloadingBox.pack_start(downloadingMessage, False, False)
        
    @postGUI
    def initQueryErrorStatus(self):
        '''Init network query status.'''
        # Clean top box.
        utils.containerRemoveAll(self.topBox)
        
        # Init query box.
        queryBox = gtk.HBox()
        queryAlign = gtk.Alignment()
        queryAlign.set(0.5, 0.5, 0.0, 0.0)
        queryAlign.add(queryBox)
        self.topBox.add(queryAlign)
        
        # Add query message.
        queryMessage = DynamicSimpleLabel(
            queryBox,
            __("Query fails, check your network and click refresh and try again."),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_SIZE,
            ).getLabel()
        queryBox.pack_start(queryMessage, False, False)
        
    @postGUI
    def initDownloadErrorStatus(self):
        '''Init network download status.'''
        # Clean top box.
        utils.containerRemoveAll(self.topBox)
        
        # Init download box.
        downloadBox = gtk.HBox()
        downloadAlign = gtk.Alignment()
        downloadAlign.set(0.5, 0.5, 0.0, 0.0)
        downloadAlign.add(downloadBox)
        self.topBox.add(downloadAlign)
        
        # Add download message.
        downloadMessage = DynamicSimpleLabel(
            downloadBox,
            __("Download fails, check your network and click refresh and try again."),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_SIZE,
            ).getLabel()
        downloadBox.pack_start(downloadMessage, False, False)
        
    @postGUI
    def initNoneedStatus(self):
        '''Init no need status.'''
        # Clean top box.
        utils.containerRemoveAll(self.topBox)
        
        # Init noneed box.
        noneedBox = gtk.HBox()
        noneedAlign = gtk.Alignment()
        noneedAlign.set(0.5, 0.5, 0.0, 0.0)
        noneedAlign.add(noneedBox)
        self.topBox.add(noneedAlign)
        
        # Add noneed message.
        noneedMessage = DynamicSimpleLabel(
            noneedBox,
            __("The software does not screenshot"),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_SIZE,
            ).getLabel()
        noneedBox.pack_start(noneedMessage, False, False)
    
    @postGUI
    def initUploadStatus(self):
        '''Init upload status.'''
        # Clean top box.
        utils.containerRemoveAll(self.topBox)
        
        # Init upload box.
        uploadBox = gtk.HBox()
        uploadAlign = gtk.Alignment()
        uploadAlign.set(0.5, 0.5, 0.0, 0.0)
        uploadAlign.add(uploadBox)
        self.topBox.add(uploadAlign)
        
        # Add upload message.
        uploadMessage = DynamicSimpleLabel(
            uploadBox,
            __("Upload screenshot"),
            appTheme.getDynamicColor("detailTitle"),
            LABEL_FONT_SIZE,
            ).getLabel()
        uploadBox.pack_start(uploadMessage, False, False)
        
        
    def getTimestamp(self):
        '''Get timestamp of screenshot.'''
        timestampDict = evalFile("./screenshotTimestamp", True)    
        
        if timestampDict != None and timestampDict.has_key(self.pkgName):
            return timestampDict[self.pkgName]
        else:
            return -1
        
    def updateTimestamp(self, timestamp):
        '''Update timestamp.'''
        timestampDict = evalFile("./screenshotTimestamp", True)    
        if timestampDict == None:
            timestampDict = {self.pkgName : timestamp}
        else:
            timestampDict[self.pkgName] = timestamp
        writeFile("./screenshotTimestamp", str(timestampDict))
        
    def hasScreenshot(self):
        '''Whether has screenshot.'''
        screenshotPath = SCREENSHOT_DOWNLOAD_DIR + self.pkgName
        if os.path.exists(screenshotPath) and os.listdir(screenshotPath) != []:
            return True
        else:
            return False
        
    def stop(self):
        '''Stop download.'''
        if self.proc != None:
            self.killed = True
            self.proc.kill()
            
    @postGUI
    def show(self):
        '''Show screenshot.'''
        # Add images.
        for image in os.listdir(os.path.join(SCREENSHOT_DOWNLOAD_DIR, self.pkgName))[0:self.SCREENSHOT_MAX_NUM]:
            self.images.append(os.path.join(SCREENSHOT_DOWNLOAD_DIR, self.pkgName, image))
            
        # Show big screenshot.
        self.showBigScreenshotArea(0)
        
        # Show small screenshot.
        if len(self.images) > 1:
            self.showSmallScreenshotArea()

    def showBigScreenshotArea(self, index):
        '''Show big screenshot.'''
        
        # Update image index.
        self.imageIndex = index
        
        # Clean top box.
        utils.containerRemoveAll(self.topBox)
        
        eventbox = gtk.EventBox()
        eventbox.set_visible_window(False)
        self.topBox.add(eventbox)
        
        self.bigScreenshotImage = gtk.image_new_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file_at_size(self.images[index], self.SCREENSHOT_WIDTH, self.SCREENSHOT_HEIGHT)
            )
        eventbox.add(self.bigScreenshotImage)
        
        eventbox.connect("button-press-event", lambda w, e: self.popupBigScreenshotWindow())
        utils.setCustomizeClickableCursor(
            eventbox,
            self.bigScreenshotImage,
            appTheme.getDynamicPixbuf("screenshot/zoom_in.png"))
        utils.setHelpTooltip(eventbox, __("Click Zoom In"))
        
        self.box.show_all()
        
    def popupBigScreenshotWindow(self):
        '''Popup big screenshot window.'''
        if self.images != [] and self.bigScreenshot == None:
            self.bigScreenshot = BigScreenshot(self.scrolledWindow, self.images, self.imageIndex, self.closeBigScreenshotWindow)
            
    def closeBigScreenshotWindow(self):
        '''Close big screenshot.'''
        if self.bigScreenshot != None:
            self.bigScreenshot.window.destroy()
            self.bigScreenshot = None
        
    def getImageIndex(self):
        '''Get image index.'''
        return self.imageIndex
        
    def showSmallScreenshotArea(self):
        '''Show small screenshot.'''
        self.bottomBox.set_size_request(
            self.SMALL_SCREENSHOT_WIDTH * self.SMALL_SCREENSHOT_COLUMN + (self.SMALL_SCREENSHOT_COLUMN + 1) * self.SMALL_SCREENSHOT_PADDING_X,
            self.SMALL_SCREENSHOT_HEIGHT * self.SMALL_SCREENSHOT_ROW + (self.SMALL_SCREENSHOT_ROW + 1) * self.SMALL_SCREENSHOT_PADDING_Y,
            )
        
        utils.containerRemoveAll(self.bottomBox)
        
        listLen = len(self.images)
        boxlist = map (lambda n: gtk.HBox(), range(0, listLen / self.SMALL_SCREENSHOT_COLUMN + listLen % self.SMALL_SCREENSHOT_COLUMN))
        for (index, box) in enumerate(boxlist):
            if index == 0:
                paddingTop = self.SMALL_SCREENSHOT_PADDING_Y
            else:
                paddingTop = self.SMALL_SCREENSHOT_PADDING_Y / 2
            align = gtk.Alignment()
            align.set(0.0, 0.0, 1.0, 1.0)
            align.set_padding(
                paddingTop,
                self.SMALL_SCREENSHOT_PADDING_Y / 2, 
                self.SMALL_SCREENSHOT_PADDING_X / 2,
                self.SMALL_SCREENSHOT_PADDING_X / 2)
            align.add(box)
            self.bottomBox.pack_start(align, False, False)
        
        for (index, image) in enumerate(self.images):
            box = boxlist[index / self.SMALL_SCREENSHOT_COLUMN]
            box.pack_start(self.createSmallScreenshot(index, image), False, False)
            
        self.box.show_all()
            
    def createSmallScreenshot(self, index, image):
        '''Create small screenshot.'''
        align = gtk.Alignment()
        align.set(0.0, 0.0, 1.0, 1.0)
        align.set_padding(
            0, 0,
            self.SMALL_SCREENSHOT_PADDING_X / 2,
            self.SMALL_SCREENSHOT_PADDING_X / 2)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(image, self.SMALL_SCREENSHOT_WIDTH, self.SMALL_SCREENSHOT_HEIGHT)
        eventbox = gtk.Button()
        eventbox.set_size_request(self.SMALL_SCREENSHOT_WIDTH, self.SMALL_SCREENSHOT_HEIGHT)
        eventbox.connect("button-press-event", lambda w, e: self.switchBigScreenshot(index))
        eventbox.connect("expose-event", lambda w, e: exposeSmallScreenshot(w, e, pixbuf, index, self.getImageIndex))
        align.add(eventbox)
            
        return align
    
    def switchBigScreenshot(self, index):
        '''Switch big screenshot.'''
        self.showBigScreenshotArea(index)
        
        self.bottomBox.queue_draw()    
    
    def downloadScreenshot(self):
        '''Download screenshot.'''
        cmdline = [
            'aria2c',
            "--dir=" + SCREENSHOT_DOWNLOAD_DIR,
            "%s/screenshots/package?n=" % (SERVER_ADDRESS) + self.pkgName,
            '--auto-file-renaming=false',
            '--summary-interval=0',
            '--remote-time=true',
            '--auto-save-interval=0',
            ]
        
        # Make software center can work with aria2c 1.9.x.
        if ARIA2_MAJOR_VERSION >= 1 and ARIA2_MINOR_VERSION <= 9:
            cmdline.append("--no-conf")
            cmdline.append("--continue")
        else:
            cmdline.append("--no-conf=true")
            cmdline.append("--continue=true")
            
        # Append proxy configuration.
        proxyString = readFirstLine("./proxy", True)
        if proxyString != "":
            cmdline.append("=".join(["--all-proxy", proxyString]))
        
        self.proc = subprocess.Popen(cmdline)
        self.proc.wait()
        
        # Extract file.
        f = zipfile.ZipFile(os.path.join(SCREENSHOT_DOWNLOAD_DIR, self.pkgName) + ".zip")
        f.extractall(os.path.join(SCREENSHOT_DOWNLOAD_DIR, self.pkgName))
        f.close()
        
        # Delete zip file.
        removeFile(os.path.join(SCREENSHOT_DOWNLOAD_DIR, self.pkgName) + ".zip")
        
    def run(self):
        '''Run'''
        self.fetchScreenshot()
        
    def fetchScreenshot(self):
        '''Update.'''
        # Init wait status.
        self.initWaitStatus()
        
        try:
            # Fetch screenshot information.
            connection = urllib2.urlopen(("%s/screenshots/screenshot?n=" % (SERVER_ADDRESS)) + self.pkgName, timeout=GET_TIMEOUT)
            voteJson = json.loads(connection.read())
            
            # Get timestamp.
            timestamp = voteJson["timestamp"]
            if timestamp == SCREENSHOT_NONEED:
                self.initNoneedStatus()
            elif timestamp == SCREENSHOT_UPLOAD:
                self.initUploadStatus()
            else:
                currentTimestamp = self.getTimestamp()
                if timestamp == currentTimestamp and self.hasScreenshot():
                    self.show()
                    
                    print "Tell user screenshot has newest."
                else:
                    try:
                        # Init downloading status.
                        self.initDownloadingStatus()
                        
                        # Downloading.
                        self.downloadScreenshot()
                        print "Download finish."
                        
                        # Update timestamp.
                        self.updateTimestamp(timestamp)
                        
                        # Show.
                        self.show()
                    except Exception, e:
                        print "Download screenshot error: %s" % (e)
                        
                        if self.hasScreenshot():
                            self.show()
                            
                            print "Tell user use old screenshot."
                        else:
                            self.initDownloadErrorStatus()
        except Exception, e:
            print "Query screenshot error: %s" % (e)
            
            if self.hasScreenshot():
                self.show()
                
                print "Tell user use old screenshot."
            else:
                self.initQueryErrorStatus()
                
class BigScreenshot(object):
    '''Big screenshot.'''
    
    CURSOR_BROWSE_PREV = 1
    CURSOR_BROWSE_NEXT = 2
    CURSOR_ZOOM_OUT = 3
	
    def __init__(self, widget, images, imageIndex, exitCallback):
        '''Init big screenshot.'''
        # Init. 
        self.widget = widget
        self.images = images
        self.imageIndex = imageIndex
        self.exitCallback = exitCallback
        
        self.browsePadding = 80
        self.x = self.y = self.width = self.height = 0
        self.imgX = self.imgY = self.imgWidth = self.imgHeight = 0
        self.cursorType = self.CURSOR_ZOOM_OUT
        
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(True)
        self.window.set_transient_for(widget.get_toplevel())
        self.window.set_opacity(0.95)
        self.window.set_property("accept-focus", False)
        self.window.connect("destroy", lambda w: exitCallback())
        self.window.connect("expose-event", self.expose)
        
        self.eventbox = gtk.EventBox()
        self.eventbox.set_visible_window(False)
        self.eventbox.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.eventbox.add_events(gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.eventbox.connect("motion-notify-event", self.updateCursor)
        self.eventbox.connect("button-press-event", self.click)
        self.window.add(self.eventbox)
        
        self.updateAllocate()
        
        self.window.show_all()
        
        self.widget.get_toplevel().connect("size-allocate", lambda w, a: self.updateAllocate())
        self.widget.get_toplevel().connect("configure-event", lambda w, a: self.updateAllocate())
        
    def show(self):
        '''Show.'''
        self.window.show_all()
    
    def hide(self):
        '''Hide.'''
        self.window.hide_all()
        
    def click(self, widget, event):
        '''Click.'''
        point = event.get_coords()
        if point != ():
            (px, py) = point
            if utils.isInRect((px, py), (0, 0, self.imgX, self.imgHeight)):
                self.browsePrev()
            elif utils.isInRect((px, py), (self.imgX + self.imgWidth, 0, self.imgX, self.imgHeight)):
                self.browseNext()
            else:
                self.exit()
        
    def updateCursor(self, widget, event):
        '''Update cursor.'''
        point = event.get_coords()
        if point != ():
            (px, py) = point
            if utils.isInRect((px, py), (0, 0, self.imgX, self.imgHeight)):
                # Set default cursor.
                widget.window.set_cursor(None)
                
                # Set cursor type.
                self.cursorType = self.CURSOR_BROWSE_PREV
                
                self.window.queue_draw()
            elif utils.isInRect((px, py), (self.imgX + self.imgWidth, 0, self.imgX, self.imgHeight)):
                # Set default cursor.
                widget.window.set_cursor(None)
                
                # Set cursor type.
                self.cursorType = self.CURSOR_BROWSE_NEXT
                
                self.window.queue_draw()
            else:
                # Change to zoom out cursor.
                widget.window.set_cursor(gtk.gdk.Cursor(
                        gtk.gdk.display_get_default(),
                        appTheme.getDynamicPixbuf("screenshot/zoom_out.png").getPixbuf(),
                        0, 0))
                
                # Set cursor type.
                self.cursorType = self.CURSOR_ZOOM_OUT
                
                self.window.queue_draw()

    def updateAllocate(self):
        '''Update allocate.'''
        if self.widget.get_child().window != None:
            (self.x, self.y) = self.widget.get_child().window.get_origin()
            rect = self.widget.get_allocation()
            (self.width, self.height) = (rect.width, rect.height)
            
            self.window.move(self.x, self.y)
            self.window.resize(self.width, self.height)
            
            self.window.queue_draw()
        
    def exit(self):
        '''Exit'''
        self.window.destroy()
        
    def browseNext(self):
        '''Browse next.'''
        if self.imageIndex == len(self.images) - 1:
            self.imageIndex = 0
        else:
            self.imageIndex += 1
            
        self.window.queue_draw()
    
    def browsePrev(self):
        '''Browse previous.'''
        if self.imageIndex == 0:
            self.imageIndex = len(self.images) - 1
        else:
            self.imageIndex -= 1
            
        self.window.queue_draw()

    def expose(self, widget, event):
        '''Show.'''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.get_allocation()
        
        # Draw background.
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.5)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()
        
        # Draw screenshot.
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
            self.images[self.imageIndex],
            self.width - self.browsePadding,
            self.height - self.browsePadding,
            )
        self.imgWidth = pixbuf.get_width()
        self.imgHeight = pixbuf.get_height()
        self.imgX = rect.x + (self.width - self.imgWidth) / 2
        self.imgY = rect.y + (self.height - self.imgHeight) / 2
        drawPixbuf(cr, pixbuf, self.imgX, self.imgY)
        
        # Draw cursor.
        if self.cursorType == self.CURSOR_BROWSE_PREV and len(self.images) > 1:
            drawPixbuf(
                cr, 
                appTheme.getDynamicPixbuf("screenshot/prev.png").getPixbuf(),
                self.imgX / 2,
                self.imgHeight / 2,
                )
        elif self.cursorType == self.CURSOR_BROWSE_NEXT and len(self.images) > 1:
            drawPixbuf(
                cr, 
                appTheme.getDynamicPixbuf("screenshot/next.png").getPixbuf(),
                self.imgX * 3 / 2 + self.imgWidth,
                self.imgHeight / 2,
                )
            
        # Draw index.
        fontSize = 20
        height = 22
        drawFont(
            cr, 
            "(%s/%s)" % (self.imageIndex + 1, len(self.images)),
            fontSize,
            "#FFFFFF",
            self.imgX + self.imgWidth / 2 - 2 * fontSize,
            getFontYCoordinate(self.imgY + self.imgHeight + height / 2, height, fontSize)
            )
        
        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)

        return True
    
#  LocalWords:  FFFFFF toggleTab xdg DDDDDD nums cuid cid feedbackLabel td
#  LocalWords:  initActionStatus appAdditionBox uninstallingProgressbar appInfo
#  LocalWords:  uninstallingFeedbackLabel switchToUninstalling UNINSTALLING
#  LocalWords:  initAdditionStatus getPkgName updateInstallingStatus imageBox
#  LocalWords:  installingProgressbar installingFeedbackLabel FetchScreenshot
#  LocalWords:  updateUpgradingStatus upgradingProgressbar 
#  LocalWords:  upgradingFeedbackLabel updateUninstallingStatus setDaemon
#  LocalWords:  returnCode waitAlign pkgName screenshotPath cmdline
#  LocalWords:  subprocess
