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
import glib
import gtk
import recommendView
import sortedDict
import utils

class RecommendPage(object):
    '''Interface for recommend page.'''
	
    def __init__(self, repoCache, switchStatus, downloadQueue, entryDetailCallback, selectCategoryCallback,
                 launchApplicationCallback, updateDataDir):
        '''Init for recommend page.'''
        # Init.
        self.box = gtk.VBox()
        
        # Add slide bar.
        self.slidebar = SlideBar(
            repoCache, 
            switchStatus, 
            downloadQueue, 
            entryDetailCallback, 
            launchApplicationCallback,
            updateDataDir)
        
        # Add recommend view.
        self.recommendView = recommendView.RecommendView(
            repoCache, 
            switchStatus, 
            downloadQueue, 
            entryDetailCallback,
            selectCategoryCallback,
            launchApplicationCallback,
            updateDataDir)
        self.appBox = gtk.VBox()
        self.appBox.pack_start(self.recommendView.box, False, False)

        self.bodyBox = gtk.HBox()
        self.bodyBox.pack_start(self.appBox, False, False)
        self.bodyAlign = gtk.Alignment()
        self.bodyAlign.set(0.5, 0.0, 0.0, 0.0)
        self.bodyAlign.add(self.bodyBox)
        
        self.contentBox = gtk.VBox()
        self.contentBox.pack_start(self.slidebar.align)
        self.contentBox.pack_start(self.bodyAlign, False, False)
        self.box.pack_start(self.contentBox)
        
        self.eventbox = gtk.EventBox()
        self.eventbox.add(self.box)
        self.eventbox.connect("expose-event", lambda w, e: drawBackground(w, e, appTheme.getDynamicColor("background")))
        
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        drawVScrollbar(self.scrolledwindow)
        utils.addInScrolledWindow(self.scrolledwindow, self.eventbox)
        
        self.scrolledwindow.show_all()
        
class SlideItem(DownloadItem):
    '''Slide item.'''
	
    def __init__(self, appInfo, name, slideDir, index, height, switchStatus, downloadQueue,
                 launchApplicationCallback):
        '''Init for slide item.'''
        DownloadItem.__init__(self, appInfo, switchStatus, downloadQueue)
        
        self.launchApplicationCallback = launchApplicationCallback
        
        self.appInfo = appInfo
        self.name = name
        self.imagePath = "%s/%s.png" % (slideDir, index)
        self.smallImagePath = "%s/%s_small.png" % (slideDir, index)
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(self.imagePath)
        self.smallPixbuf = gtk.gdk.pixbuf_new_from_file(self.smallImagePath)
        
        # Widget that status will change.
        self.installingProgressbar = None
        self.installingFeedbackLabel = None

        self.upgradingProgressbar = None
        self.upgradingFeedbackLabel = None

        paddingX = 20
        self.itemBox = gtk.HBox()
        self.itemBox.set_size_request(-1, height)
        self.itemFrame = gtk.Alignment()
        self.itemFrame.set(0.0, 0.0, 0.0, 0.0)
        self.itemFrame.set_padding(0, 0, paddingX, paddingX)
        self.itemFrame.add(self.itemBox)
        
        self.itemNameLabel = gtk.Label()
        self.itemNameLabel.set_markup(
            "<span foreground='%s' size='%s'>%s</span>"
            % (appTheme.getDynamicColor("slideText").getColor(),
               LABEL_FONT_XXX_LARGE_SIZE, 
               self.name))
        self.itemNameLabel.set_alignment(0.0, 0.5)
        self.itemNameBox = gtk.EventBox()
        self.itemNameBox.set_visible_window(False)
        self.itemNameBox.add(self.itemNameLabel)
        self.itemBox.pack_start(self.itemNameBox)
        setClickableCursor(self.itemNameBox)
        
        self.appAdditionBox = gtk.HBox()
        self.appAdditionAlign = gtk.Alignment()
        self.appAdditionAlign.set(1.0, 0.5, 0.0, 0.0)
        self.appAdditionAlign.add(self.appAdditionBox)
        self.itemBox.pack_start(self.appAdditionAlign, False, False)
        
        self.initAdditionStatus()
        
        self.itemFrame.show_all()
        
    def initAdditionStatus(self):
        '''Add addition status.'''
        status = self.appInfo.status
        if status in [APP_STATE_NORMAL, APP_STATE_UPGRADE, APP_STATE_INSTALLED]:
            self.itemNameLabel.set_width_chars(70)
        else:        
            self.itemNameLabel.set_width_chars(45)
        
        if status in [APP_STATE_NORMAL, APP_STATE_UPGRADE, APP_STATE_INSTALLED]:
            self.initNormalStatus()
        elif status == APP_STATE_DOWNLOADING:
            self.initDownloadingStatus(self.appAdditionBox, True)
        elif status == APP_STATE_DOWNLOAD_PAUSE:
             self.initDownloadPauseStatus(self.appAdditionBox, True, appTheme.getDynamicColor("slideText"))
        elif status == APP_STATE_INSTALLING:
            self.initInstallingStatus(True)
        elif status == APP_STATE_UPGRADING:
            self.initUpgradingStatus(True)
            
        self.itemFrame.show_all()
        
    def initNormalStatus(self):
        '''Init normal status.'''
        # Clean right box first.
        utils.containerRemoveAll(self.appAdditionBox)
        
        # Add action button.
        (actionButtonBox, actionButtonAlign) = createActionButton()
        self.appAdditionBox.pack_start(actionButtonAlign, False, False)
        if self.appInfo.status == APP_STATE_NORMAL:
            (appButton, appButtonAlign) = newActionButton(
                "search", 0.5, 0.5,  "cell", False, __("Action Install"), BUTTON_FONT_SIZE_LARGE, "bigButtonFont"
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            actionButtonBox.pack_start(appButtonAlign)
        elif self.appInfo.status == APP_STATE_UPGRADE:
            (appButton, appButtonAlign) = newActionButton(
                "search", 0.5, 0.5, 
                "cell", False, __("Action Update"), BUTTON_FONT_SIZE_LARGE, "bigButtonFont"
                )
            appButton.connect("button-release-event", lambda widget, event: self.switchToDownloading())
            actionButtonBox.pack_start(appButtonAlign)
        else:
            execPath = self.appInfo.execPath
            if execPath:
                (appButton, appButtonAlign) = newActionButton(
                    "search", 0.5, 0.5, 
                    "cell", False, __("Action Startup"), BUTTON_FONT_SIZE_LARGE, "bigButtonFont"
                    )
                appButton.connect("button-release-event", lambda widget, event: self.launchApplicationCallback(execPath))
                actionButtonBox.pack_start(appButtonAlign)
            else:
                appInstalledDynamicLabel = DynamicSimpleLabel(
                    actionButtonBox,
                    __("Action Installed"),
                    appTheme.getDynamicColor("slideText"),
                    LABEL_FONT_LARGE_SIZE,
                    )
                appInstalledLabel = appInstalledDynamicLabel.getLabel()
                buttonImage = appTheme.getDynamicPixbuf("cell/update_hover.png").getPixbuf()
                appInstalledLabel.set_size_request(buttonImage.get_width(), buttonImage.get_height())
                actionButtonBox.pack_start(appInstalledLabel)

class SlideBar(object):
    '''Slide bar'''
	
    def __init__(self, repoCache, switchStatus, downloadQueue, entryDetailCallback, launchApplicationCallback, updateDataDir):
        '''Init for slide bar.'''
        # Init.
        self.entryDetailCallback = entryDetailCallback
        self.launchApplicationCallback = launchApplicationCallback
        self.padding = 10
        self.imageWidth = 600
        self.imageHeight = 300
        self.maskHeight = 50
        self.times = 10
        self.interval = 300 / self.times
        self.smallImagePaddingY = 10
        self.hoverTimeoutIds = {}
        self.hoverTimeout = 100

        self.repoCache = repoCache
        self.slideDir = updateDataDir + "slide/%s" % (getDefaultLanguage())
        self.infoList = evalFile("%s/index.txt" % (self.slideDir))
        self.itemDict = sortedDict.SortedDict(map(lambda (pkgName, _): (pkgName, None), self.infoList))
        self.initItems(switchStatus, downloadQueue)
        self.sourceIndex = 1
        self.targetIndex = 0
        
        self.sourceImage = self.createSlideImage(self.sourceIndex)
        self.targetImage = self.createSlideImage(self.targetIndex)
        self.maskPixbuf = appTheme.getDynamicPixbuf("recommend/mask.png")
        
        self.stop = True
        self.ticker = self.times
        self.index = 0
        self.alphaInterval = 1
        
        self.align = gtk.Alignment()
        self.align.set(0.5, 0.5, 0.0, 0.0)
        self.align.set_padding(self.padding, self.padding, self.padding, self.padding)
        
        # Add slide label.
        self.labelBox = gtk.VBox()
        for (index, _) in enumerate(self.infoList):
            self.createSlideLabel(index)
        
        # Add slide area.
        self.drawingArea = gtk.EventBox()
        self.drawingArea.set_visible_window(False)
        self.drawingArea.set_size_request(self.imageWidth, self.imageHeight)
        self.drawingArea.connect("expose_event", self.exposeBigArea)
        self.drawingArea.connect(
            "button-press-event",
            lambda w, e: self.entryDetailView())
        setClickableCursor(self.drawingArea)
        self.drawingArea.queue_draw()
        
        self.slideItemBox = gtk.VBox()
        self.slideItemAlign = gtk.Alignment()
        self.slideItemAlign.set(0.0, 1.0, 0.0, 0.0)
        self.slideItemAlign.add(self.slideItemBox)
        self.drawingArea.add(self.slideItemAlign)
        
        self.slideItemBox.pack_start(self.getSlideItem(self.targetIndex).itemFrame)
        
        # Connect widgets.
        self.box = gtk.HBox()
        self.box.pack_start(self.drawingArea, False, False)
        self.box.pack_start(self.labelBox, False, False)
        
        self.align.add(self.box)
        
    def entryDetailView(self):
        '''Entry detail view.'''
        appInfo = self.getSlideItem(self.targetIndex).appInfo
        self.entryDetailCallback(PAGE_RECOMMEND, appInfo)
        
    def initItems(self, switchStatus, downloadQueue):
        '''Init items.'''
        for (index, (pkgName, name)) in enumerate(self.infoList):
            appInfo = self.repoCache.cache[pkgName]
            slideItem = SlideItem(
                appInfo, name, self.slideDir, index + 1,
                self.maskHeight, switchStatus, downloadQueue,
                self.launchApplicationCallback)
            self.itemDict[pkgName] = slideItem
            
    def switchToStatus(self, pkgName, appStatus):
        '''Switch to downloading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.appInfo.status = appStatus
            appItem.initAdditionStatus()
            
    def initNormalStatus(self, pkgName, isMarkDeleted):
        '''Init normal status.'''
        if isMarkDeleted:
            self.switchToStatus(pkgName, APP_STATE_NORMAL)
        else:
            self.switchToStatus(pkgName, APP_STATE_INSTALLED)
            
    def updateDownloadingStatus(self, pkgName, progress, feedback):
        '''Update downloading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateDownloadingStatus(progress, feedback, appTheme.getDynamicColor("slideText").getColor())
            
    def updateInstallingStatus(self, pkgName, progress, feedback):
        '''Update installing status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateInstallingStatus(progress, feedback, appTheme.getDynamicColor("slideText").getColor())
            
    def updateUpgradingStatus(self, pkgName, progress, feedback):
        '''Update upgrading status.'''
        if self.itemDict.has_key(pkgName):
            appItem = self.itemDict[pkgName]
            appItem.updateUpgradingStatus(progress, feedback, appTheme.getDynamicColor("slideText").getColor())
            
    def getSlideItem(self, index):
        '''Get slide item.'''
        return (self.itemDict.values())[index]
        
    def createSlideImage(self, index):
        '''Create slide image.'''
        return (self.getSlideItem(index)).pixbuf
    
    def createSlideLabel(self, index):
        '''Create slide label.'''
        imagePath = (self.getSlideItem(index)).imagePath
        image = gtk.EventBox()
        image.set_visible_window(False)
        image.set_size_request(self.imageWidth / 3, 
                               (self.imageHeight - self.smallImagePaddingY * 2) / 3)
        image.connect("expose_event", lambda w, e: self.exposeSmallArea(w, e, index))
        image.queue_draw()
        setClickableCursor(image)
        
        imageAlign = gtk.Alignment()
        if index == 1:
            imagePaddingY = self.smallImagePaddingY
        else:
            imagePaddingY = 0
        imagePaddingLeft = 10
        imageAlign.set_padding(imagePaddingY, imagePaddingY, imagePaddingLeft, 0)
        imageAlign.add(image)
        labelBox = gtk.EventBox()
        labelBox.add(imageAlign)
        labelBox.connect("button-press-event", lambda widget, event: self.start(index))
        labelBox.connect("enter-notify-event", lambda w, e: self.onSlideLabelEnter(index))
        labelBox.connect("leave-notify-event", lambda w, e: self.onSlideLabelLeave(index))
        labelBox.connect("expose-event", lambda w, e: drawBackground(w, e, appTheme.getDynamicColor("background")))
        self.labelBox.pack_start(labelBox, True, True)
        
    def onSlideLabelEnter(self, index):
        '''On slide label enter.'''
        # Start slide when 100 milliseconds after hover.
        if not self.hoverTimeoutIds.has_key(index):
            self.hoverTimeoutIds[index] = glib.timeout_add(self.hoverTimeout, lambda : self.start(index))
        
    def onSlideLabelLeave(self, index):
        '''On slide label leave.'''
        # Remove hover timeout handler.
        if self.hoverTimeoutIds.has_key(index):
            glib.source_remove(self.hoverTimeoutIds[index])
            del self.hoverTimeoutIds[index]
        
    def exposeSmallArea(self, drawArea, event, index):
        '''Expose small area.'''
        # Draw image.
        x, y = drawArea.allocation.x, drawArea.allocation.y
        imgPath = (self.getSlideItem(index)).imagePath
        sourcePath = (self.getSlideItem(self.sourceIndex)).imagePath
        targetPath = (self.getSlideItem(self.targetIndex)).imagePath
        cr = drawArea.window.cairo_create()
        cr.set_source_pixbuf((self.getSlideItem(index)).smallPixbuf, x, y)
        
        interval = 0.5 / self.times
        if targetPath == imgPath:
            cr.paint_with_alpha(0.5 + self.ticker * interval)
        elif sourcePath == imgPath:
            cr.paint_with_alpha(1.0 - self.ticker * interval)
        else:
            cr.paint_with_alpha(0.5)
        
    def exposeBigArea(self, drawArea, event):
        '''Expose callback for the drawing area.'''
        x, y = drawArea.allocation.x, drawArea.allocation.y
        width, height = self.targetImage.get_width(), self.targetImage.get_height()

        # Draw background.
        cr = self.drawingArea.window.cairo_create()
        if self.ticker < self.times / 2:
            targetPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
            self.targetImage.copy_area(0, 0, width, height, targetPixbuf, 0, 0)
            cr.set_source_pixbuf(targetPixbuf, x, y)
            cr.paint_with_alpha(self.ticker * self.alphaInterval)
            
            sourcePixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
            self.sourceImage.copy_area(0, 0, width, height, sourcePixbuf, 0, 0)
            cr.set_source_pixbuf(sourcePixbuf, x, y)
            cr.paint_with_alpha((self.times - self.ticker) * self.alphaInterval)
        elif self.ticker == self.times:
            targetPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
            self.targetImage.copy_area(0, 0, width, height, targetPixbuf, 0, 0)
            cr.set_source_pixbuf(targetPixbuf, x, y)
            cr.paint_with_alpha(1)
        else:
            sourcePixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
            self.sourceImage.copy_area(0, 0, width, height, sourcePixbuf, 0, 0)
            cr.set_source_pixbuf(sourcePixbuf, x, y)
            cr.paint_with_alpha((self.times - self.ticker) * self.alphaInterval)
            
            targetPixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
            self.targetImage.copy_area(0, 0, width, height, targetPixbuf, 0, 0)
            cr.set_source_pixbuf(targetPixbuf, x, y)
            cr.paint_with_alpha(self.ticker * self.alphaInterval)

        # Draw mask.
        cr.set_source_pixbuf(self.maskPixbuf.getPixbuf(), x, y + height - self.maskHeight)
        cr.paint_with_alpha(0.5)

    def start(self, index):
        '''Start show slide.'''
        # Stop if index same as current one.
        if self.index == index:
            return False
        # Just start slide when stop.
        elif self.stop:
            # Get path.
            self.sourceIndex = self.index
            self.targetIndex = index
            
            # Get new image.
            self.sourceImage = self.createSlideImage(self.sourceIndex)
            self.targetImage = self.createSlideImage(self.targetIndex)
            
            # Reset.
            self.stop = False
            self.index = index
            self.ticker = 0
            self.alphaInterval = 1.0 / self.times
            
            # Change slide item.
            self.updateSlideItem()
                        
            # Start slide.
            glib.timeout_add(self.interval, self.slide)
            
            return False
            
    def updateSlideItem(self):
        '''Update slide item.'''
        utils.containerRemoveAll(self.slideItemBox)        
        self.slideItemBox.pack_start(self.getSlideItem(self.targetIndex).itemFrame)

    def slide(self):
        '''Slide.'''
        # Update ticker.
        self.ticker += 1
        
        # Redraw.
        self.drawingArea.queue_draw() # redraw big logo
        self.labelBox.queue_draw()    # redraw small logo
        
        # Stop slide if ticker reach times.
        if self.ticker == self.times:
            self.stop = True
            return False
        else:
            return True

