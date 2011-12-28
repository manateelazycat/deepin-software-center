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
from copy import deepcopy
from draw import *
from lang import __, getDefaultLanguage
from theme import *
from tooltips import *
from utils import postGUI
import action
import apt
import apt_pkg
import cairo
import checkUpdate
import detailView
import download
import downloadManagePage
import getopt
import glib
import gobject
import gtk
import ignorePage
import json
import math
import moreWindow
import navigatebar
import os
import pango
import pangocairo
import recommendPage
import repoCache
import repoPage
import search
import searchPage
import searchUninstallPage as sp
import socket
import statusbar
import subprocess
import sys
import themeSelect
import threading as td
import titlebar
import uninstallPage
import updateList
import updatePage
import urllib
import urllib2
import utils

class DeepinSoftwareCenter(object):
    '''Interface for software center.'''

    def __init__(self):
        '''Init.'''
        # Init gdk threads.
        gtk.gdk.threads_init()
        
        # Init apt cache.
        self.detailViewDict = {}
        self.searchViewDict = {}
        self.entryIgnorePage = False
        self.downloadQueue = None
        self.actionQueue = None
        self.pauseList = []
        self.defaultPageId = PAGE_RECOMMEND
        
        # dpkg will failed if not set TERM and PATH environment variable.  
        os.environ["TERM"] = "xterm"
        os.environ["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/X11R6/bin"
        
        # Remove lock file if it exist.
        if os.path.exists("/var/lib/apt/lists/lock"):
            os.remove("/var/lib/apt/lists/lock")
        
        # Init widgets.
        self.window = self.initMainWindow()
        self.window.connect("size-allocate", lambda w, a: updateShape(w, a, RADIUS))
        self.hasMax = False
        self.leftLine = gtk.Image()
        self.rightLine = gtk.Image()
        drawVerticalLine(self.leftLine, 1)
        drawVerticalLine(self.rightLine, 1)
        self.mainBox = gtk.VBox()
        self.topbox = gtk.VBox()
        self.topbar = gtk.EventBox()
        self.themeSelectWindow = themeSelect.ThemeSelect(self.window, self.selectTheme)
        self.moreWindow = moreWindow.MoreWindow(self.window, self.message)
        
        self.statusbar = statusbar.Statusbar()
        self.statusbar.eventbox.connect("button-press-event", lambda w, e: utils.resizeWindow(w, e, self.window))
        self.statusbar.eventbox.connect("button-press-event", lambda w, e: utils.moveWindow(w, e, self.window))
        
        drawNavigateBackground(
            self.topbar,
            appTheme.getDynamicPixbuf("navigate/background.png"),
            appTheme.getDynamicDrawType("navigatebar"),
            appTheme.getDynamicAlphaColor("frameLigtht"),
            appTheme.getDynamicAlphaColor("topbarBottom"),
            )

        # make window movable or re-sizable even window is decorated.
        self.topbar.connect('button-press-event', lambda w, e: utils.moveWindow(w, e, self.window))
        self.topbar.connect("button-press-event", self.doubleClickWindow)
        self.titlebar = titlebar.Titlebar(
            self.showThemeSelectWindow, 
            self.showMoreWindow,
            self.minWindow, 
            self.toggleWindow, 
            self.closeWindow)
        self.navigatebar = navigatebar.NavigateBar()
        self.bodyBox = gtk.HBox()
        self.contentBox = gtk.VBox()
        
        self.window.connect_after("show", lambda w: self.createTooltips())
        
    def showThemeSelectWindow(self, widget, event):
        '''Show theme select window.'''
        if self.themeSelectWindow.window.get_visible():
            self.themeSelectWindow.hide()
        else:
            # Hide popup window.
            self.hidePopupWindow()
            
            # Show theme select window.
            rect = widget.allocation
            (wx, wy) = widget.window.get_origin()
            (x, y) = widget.translate_coordinates(self.window, wx, wy)
            self.themeSelectWindow.show(x + rect.width - THEME_WINDOW_WIDTH, y + rect.height)
            
    def showMoreWindow(self, widget, event):
        '''Show more window.'''
        if self.moreWindow.window.get_visible():
            self.moreWindow.hide()
        else:
            # Hide popup window.
            self.hidePopupWindow()
            
            # Show more window.
            rect = widget.allocation
            (wx, wy) = widget.window.get_origin()
            (x, y) = widget.translate_coordinates(self.window, wx, wy)
            self.moreWindow.show(x, y + rect.height)
                
    def hidePopupWindow(self):
        '''Hide popup window.'''
        # Hide more window if it visible now.
        if self.moreWindow.window.get_visible():
            self.moreWindow.hide()
            
        # Hide theme select window if it visible now.
        if self.themeSelectWindow.window.get_visible():
            self.themeSelectWindow.hide()
        
        # Hide new feature window if it visible now.
        if self.moreWindow.newFeatureWindow.window.get_visible():
            self.moreWindow.newFeatureWindow.hide()
            
        # Hide proxy setup window if it visible now.
        if self.moreWindow.proxySetupWindow.window.get_visible():
            self.moreWindow.proxySetupWindow.hide()
            
    def selectTheme(self, themeName):
        '''Select theme.'''
        # Change theme.
        appTheme.changeTheme(themeName)            
        
        # Redraw.
        self.window.queue_draw()
        
        # Redraw big screenshot.
        for dView in self.detailViewDict.values():
            if dView.smallScreenshot != None and dView.smallScreenshot.bigScreenshot != None:
                dView.smallScreenshot.bigScreenshot.window.queue_draw()
                
        # Redraw theme select window.
        if self.themeSelectWindow.window.get_visible():
            self.themeSelectWindow.window.queue_draw()

    def createTooltips(self):
        '''Create tooltips.'''
        self.tooltips = Tooltips(self.window, self.statusbar.eventbox)

    def message(self, message):
        '''Show message.'''
        self.tooltips.start(message)

    def switchStatus(self, pkgName, appStatus):
        '''Switch status.'''
        # Update slide bar.
        self.recommendPage.slidebar.switchToStatus(pkgName, appStatus)

        # Update recommend view.
        recommendView = self.recommendPage.recommendView
        recommendView.switchToStatus(pkgName, appStatus)

        # Update repository view.
        repoView = self.repoPage.repoView
        repoView.switchToStatus(pkgName, appStatus)

        # Update application view.
        updateView = self.updatePage.updateView
        updateView.switchToStatus(pkgName, appStatus)
        
        # Update download manage view.
        self.updateDownloadManageView(pkgName, appStatus)

        # Update detail view.
        for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
            if self.detailViewDict.has_key(pageId):
                detailView = self.detailViewDict[pageId]
                detailView.switchToStatus(pkgName, appStatus)
            elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                searchView = self.searchViewDict[pageId].searchView
                searchView.switchToStatus(pkgName, appStatus)
                
    @postGUI
    def downloadUpdateCallback(self, pkgName, progress, feedback, status=APP_STATE_DOWNLOADING):
        '''Update downloading callback.'''
        if self.repoCache.cache.has_key(pkgName):
            # Update Application information.
            appInfo = self.repoCache.cache[pkgName]
            appInfo.updateDownloadStatus(progress, feedback, status)

            # Update slide bar.
            self.recommendPage.slidebar.updateDownloadingStatus(pkgName, progress, feedback)

            # Update recommend view.
            recommendView = self.recommendPage.recommendView
            recommendView.updateDownloadingStatus(pkgName, progress, feedback)

            # Update repository view.
            repoView = self.repoPage.repoView
            repoView.updateDownloadingStatus(pkgName, progress, feedback)

            # Update application view.
            updateView = self.updatePage.updateView
            updateView.updateDownloadingStatus(pkgName, progress, feedback)

            # Update download manage view.
            downloadManageView = self.downloadManagePage.downloadManageView
            downloadManageView.updateDownloadingStatus(pkgName, progress, feedback)
            
            # Update detail view.
            for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                if self.detailViewDict.has_key(pageId):
                    detailView = self.detailViewDict[pageId]
                    detailView.updateDownloadingStatus(pkgName, progress, feedback)
                elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                    searchView = self.searchViewDict[pageId].searchView
                    searchView.updateDownloadingStatus(pkgName, progress, feedback)
        else:
            print "Impossible: %s not in RepoCache" % (pkgName)

    @postGUI
    def downloadFinishCallback(self, pkgName):
        '''Download finish callback.'''
        if self.repoCache.cache.has_key(pkgName):
            # Update application information.
            appInfo = self.repoCache.cache[pkgName]
            if appInfo.pkg.is_upgradable:
                appStatus = APP_STATE_UPGRADING
            else:
                appStatus = APP_STATE_INSTALLING
            appInfo.switchStatus(appStatus)

            # Update slide bar.
            self.recommendPage.slidebar.switchToStatus(pkgName, appStatus)

            # Update application view.
            recommendView = self.recommendPage.recommendView
            recommendView.switchToStatus(pkgName, appStatus)

            # Update repository view.
            repoView = self.repoPage.repoView
            repoView.switchToStatus(pkgName, appStatus)

            # Update update view.
            updateView = self.updatePage.updateView
            updateView.switchToStatus(pkgName, appStatus)

            # Update download manage view.
            self.updateDownloadManageView(pkgName, appStatus)

            # Update detail view.
            for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                if self.detailViewDict.has_key(pageId):
                    detailView = self.detailViewDict[pageId]
                    detailView.switchToStatus(pkgName, appStatus)
                elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                    searchView = self.searchViewDict[pageId].searchView
                    searchView.switchToStatus(pkgName, appStatus)

            # Require new install action.
            if appStatus == APP_STATE_UPGRADING:
                self.actionQueue.addAction(pkgName, ACTION_UPGRADE)
            else:
                self.actionQueue.addAction(pkgName, ACTION_INSTALL)
        else:
            print "Impossible: %s not in RepoCache" % (pkgName)

    @postGUI
    def downloadFailedCallback(self, pkgName):
        '''Download failed callback.'''
        if self.repoCache.cache.has_key(pkgName):
            # Update application information.
            appInfo = self.repoCache.cache[pkgName]
            if appInfo.pkg.is_upgradable:
                appStatus = APP_STATE_UPGRADE
            else:
                appStatus = APP_STATE_NORMAL

            # Update slide bar.
            self.recommendPage.slidebar.switchToStatus(pkgName, appStatus)

            # Update application view.
            recommendView = self.recommendPage.recommendView
            recommendView.switchToStatus(pkgName, appStatus)

            # Update repository view.
            repoView = self.repoPage.repoView
            repoView.switchToStatus(pkgName, appStatus, True)

            # Update update view.
            updateView = self.updatePage.updateView
            updateView.switchToStatus(pkgName, appStatus, True)

            # Update download manage view.
            self.updateDownloadManageView(pkgName, appStatus)

            # Update detail view.
            for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                if self.detailViewDict.has_key(pageId):
                    detailView = self.detailViewDict[pageId]
                    detailView.switchToStatus(pkgName, appStatus)
                elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                    searchView = self.searchViewDict[pageId].searchView
                    searchView.switchToStatus(pkgName, appStatus, True)
        else:
            print "Impossible: %s not in RepoCache" % (pkgName)

    @postGUI
    def actionUpdateCallback(self, actionType, pkgName, progress, feedback):
        '''Installing update callback.'''
        if self.repoCache.cache.has_key(pkgName):
            if actionType == ACTION_INSTALL:
                # Update application information.
                appInfo = self.repoCache.cache[pkgName]
                appInfo.updateInstallStatus(progress, feedback)

                # Update slide bar.
                self.recommendPage.slidebar.updateInstallingStatus(pkgName, progress, feedback)

                # Update application view.
                recommendView = self.recommendPage.recommendView
                recommendView.updateInstallingStatus(pkgName, progress, feedback)

                # Update repository view.
                repoView = self.repoPage.repoView
                repoView.updateInstallingStatus(pkgName, progress, feedback)
                
                # Update download manage view.
                downloadManageView = self.downloadManagePage.downloadManageView
                downloadManageView.updateInstallingStatus(pkgName, progress, feedback)

                # Update detail view.
                for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                    if self.detailViewDict.has_key(pageId):
                        detailView = self.detailViewDict[pageId]
                        detailView.updateInstallingStatus(pkgName, progress, feedback)
                    elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                        searchView = self.searchViewDict[pageId].searchView
                        searchView.updateInstallingStatus(pkgName, progress, feedback)
            elif actionType == ACTION_UPGRADE:
                # Update application information.
                appInfo = self.repoCache.cache[pkgName]
                appInfo.updateUpgradeStatus(progress, feedback)

                # Update slide bar.
                self.recommendPage.slidebar.updateUpgradingStatus(pkgName, progress, feedback)

                # Update application view.
                recommendView = self.recommendPage.recommendView
                recommendView.updateUpgradingStatus(pkgName, progress, feedback)

                # Update repository view.
                repoView = self.repoPage.repoView
                repoView.updateUpgradingStatus(pkgName, progress, feedback)

                # Update update view.
                updateView = self.updatePage.updateView
                updateView.updateUpgradingStatus(pkgName, progress, feedback)

                # Update download manage view.
                downloadManageView = self.downloadManagePage.downloadManageView
                downloadManageView.updateUpgradingStatus(pkgName, progress, feedback)

                # Update detail view.
                for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                    if self.detailViewDict.has_key(pageId):
                        detailView = self.detailViewDict[pageId]
                        detailView.updateUpgradingStatus(pkgName, progress, feedback)
                    elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                        searchView = self.searchViewDict[pageId].searchView
                        searchView.updateUpgradingStatus(pkgName, progress, feedback)
            elif actionType == ACTION_UNINSTALL:
                # Update application information.
                appInfo = self.repoCache.cache[pkgName]
                appInfo.updateUninstallStatus(progress, feedback)

                # Update application view.
                uninstallView = self.uninstallPage.uninstallView
                uninstallView.updateUninstallingStatus(pkgName, progress, feedback)

                # Update detail view.
                for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                    if self.detailViewDict.has_key(pageId):
                        detailView = self.detailViewDict[pageId]
                        detailView.updateUninstallingStatus(pkgName, progress, feedback)
                    elif pageId == PAGE_UNINSTALL and self.searchViewDict.has_key(pageId):
                        searchView = self.searchViewDict[pageId].searchView
                        searchView.updateUninstallingStatus(pkgName, progress, feedback)
        else:
            print "Impossible: %s not in RepoCache" % (pkgName)

    @postGUI
    def actionFinishCallback(self, actionType, pkgList):
        '''Installing finish callback.'''
        if actionType == ACTION_INSTALL:
            for (pkgName, isMarkDeleted) in pkgList:
                if self.repoCache.cache.has_key(pkgName):
                    # Update application information.
                    appInfo = self.repoCache.cache[pkgName]
                    if isMarkDeleted:
                        appStatus = APP_STATE_NORMAL
                        appInfo.switchStatus(appStatus)
                    else:
                        appStatus = APP_STATE_INSTALLED
                        appInfo.switchStatus(appStatus)

                    # Update slide bar.
                    self.recommendPage.slidebar.initNormalStatus(pkgName, isMarkDeleted)

                    # Update recommend view.
                    recommendView = self.recommendPage.recommendView
                    recommendView.initNormalStatus(pkgName, isMarkDeleted)

                    # Update repository view.
                    repoView = self.repoPage.repoView
                    repoView.initNormalStatus(pkgName, isMarkDeleted, True)

                    # Update download manage view.
                    self.updateDownloadManageView(pkgName, appStatus)

                    # Update detail view.
                    for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                        if self.detailViewDict.has_key(pageId):
                            detailView = self.detailViewDict[pageId]
                            detailView.initNormalStatus(pkgName, isMarkDeleted)
                        elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                            searchView = self.searchViewDict[pageId].searchView
                            searchView.initNormalStatus(pkgName, isMarkDeleted, True)

                    # Add in uninstall list.
                    self.updateUninstallView(pkgName, not isMarkDeleted)
                else:
                    print "Impossible: %s not in RepoCache" % (pkgName)
        elif actionType == ACTION_UPGRADE:
            for (pkgName, isMarkDeleted) in pkgList:
                if self.repoCache.cache.has_key(pkgName):
                    # Update application information.
                    appInfo = self.repoCache.cache[pkgName]
                    if isMarkDeleted:
                        appStatus = APP_STATE_NORMAL
                        appInfo.switchStatus(appStatus)
                    else:
                        appStatus = APP_STATE_INSTALLED
                        appInfo.switchStatus(appStatus)

                        # Remove upgradabled packages.
                        self.repoCache.removePkgFromUpgradableList(pkgName)

                        # Update topbar.
                        pkgNum = self.repoCache.getUpgradableNum()
                        self.updatePage.topbar.updateNum(pkgNum)

                        # Update update view.
                        updateView = self.updatePage.updateView
                        updateView.unselectPkg(pkgName) # remove from select list
                        updateView.update(pkgNum)

                        # Update notify number.
                        self.navigatebar.updateIcon.queue_draw()

                    # Update slide bar.
                    self.recommendPage.slidebar.initNormalStatus(pkgName, isMarkDeleted)

                    # Update recommend view.
                    recommendView = self.recommendPage.recommendView
                    recommendView.initNormalStatus(pkgName, isMarkDeleted)

                    # Update repository view.
                    repoView = self.repoPage.repoView
                    repoView.initNormalStatus(pkgName, isMarkDeleted, True)

                    # Update download manage view.
                    self.updateDownloadManageView(pkgName, appStatus)

                    # Update detail view.
                    for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                        if self.detailViewDict.has_key(pageId):
                            detailView = self.detailViewDict[pageId]
                            detailView.initNormalStatus(pkgName, isMarkDeleted)
                        elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                            searchView = self.searchViewDict[pageId].searchView
                            searchView.initNormalStatus(pkgName, isMarkDeleted, True)

                    # Add in uninstall list.
                    self.updateUninstallView(pkgName, not isMarkDeleted)
                    
                    # Save upgrade number.
                    self.saveUpgradeNum()
                else:
                    print "Impossible: %s not in RepoCache" % (pkgName)
        elif actionType == ACTION_UNINSTALL:
            for (pkgName, isMarkDeleted) in pkgList:
                # Send uninstall count.
                SendUninstallCount(pkgName).start()
                
                if self.repoCache.cache.has_key(pkgName):
                    # Update application information.
                    appInfo = self.repoCache.cache[pkgName]
                    appInfo.switchStatus(APP_STATE_NORMAL)

                    self.updateUninstallView(pkgName, False)

                    # Update slide bar.
                    self.recommendPage.slidebar.initNormalStatus(pkgName, isMarkDeleted)

                    # Update recommend view.
                    recommendView = self.recommendPage.recommendView
                    recommendView.initNormalStatus(pkgName, isMarkDeleted)

                    # Update repository view.
                    repoView = self.repoPage.repoView
                    repoView.initNormalStatus(pkgName, isMarkDeleted, True)

                    # Update detail view.
                    for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                        if self.detailViewDict.has_key(pageId):
                            detailView = self.detailViewDict[pageId]
                            detailView.initNormalStatus(pkgName, isMarkDeleted)
                        elif pageId == PAGE_UNINSTALL and self.searchViewDict.has_key(pageId):
                            searchPage = self.searchViewDict[pageId]
                            searchPage.update(pkgName)
                else:
                    print "Impossible: %s not in RepoCache" % (pkgName)

    @postGUI
    def actionFailedCallback(self, actionType, pkgName):
        '''Installing failed callback.'''
        if actionType == ACTION_INSTALL:
            if self.repoCache.cache.has_key(pkgName):
                # Update application information.
                appInfo = self.repoCache.cache[pkgName]
                appStatus = APP_STATE_NORMAL
                appInfo.switchStatus(appStatus)

                # Update slide bar.
                self.recommendPage.slidebar.initNormalStatus(pkgName, True)

                # Update recommend view.
                recommendView = self.recommendPage.recommendView
                recommendView.initNormalStatus(pkgName, True)

                # Update repository view.
                repoView = self.repoPage.repoView
                repoView.initNormalStatus(pkgName, True, True)

                # Update download manage view.
                self.updateDownloadManageView(pkgName, appStatus)

                # Update detail view.
                for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                    if self.detailViewDict.has_key(pageId):
                        detailView = self.detailViewDict[pageId]
                        detailView.initNormalStatus(pkgName, True)
                    elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                        searchView = self.searchViewDict[pageId].searchView
                        searchView.initNormalStatus(pkgName, True, True)
            else:
                print "Impossible: %s not in RepoCache" % (pkgName)
        elif actionType == ACTION_UPGRADE:
            if self.repoCache.cache.has_key(pkgName):
                # Update application information.
                appInfo = self.repoCache.cache[pkgName]
                appStatus = APP_STATE_UPGRADE
                appInfo.switchStatus(appStatus)

                # Update slide bar.
                self.recommendPage.slidebar.initNormalStatus(pkgName, APP_STATE_UPGRADE)

                # Update recommend view.
                recommendView = self.recommendPage.recommendView
                recommendView.switchToStatus(pkgName, APP_STATE_UPGRADE)

                # Update repository view.
                repoView = self.repoPage.repoView
                repoView.switchToStatus(pkgName, APP_STATE_UPGRADE, True)

                # Update update view.
                updateView = self.updatePage.updateView
                updateView.switchToStatus(pkgName, APP_STATE_UPGRADE, True)

                # Update download manage view.
                self.updateDownloadManageView(pkgName, appStatus)

                # Update detail view.
                for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                    if self.detailViewDict.has_key(pageId):
                        detailView = self.detailViewDict[pageId]
                        detailView.switchToStatus(pkgName, APP_STATE_UPGRADE)
                    elif pageId == PAGE_REPO and self.searchViewDict.has_key(pageId):
                        searchView = self.searchViewDict[pageId].searchView
                        searchView.switchToStatus(pkgName, APP_STATE_UPGRADE, True)
            else:
                print "Impossible: %s not in RepoCache" % (pkgName)
        elif actionType == ACTION_UNINSTALL:
            if self.repoCache.cache.has_key(pkgName):
                # Update application information.
                appInfo = self.repoCache.cache[pkgName]
                appInfo.switchStatus(APP_STATE_INSTALLED)

                # Update uninstall view.
                uninstallView = self.uninstallPage.uninstallView
                uninstallView.initUninstallStatus(pkgName, True)

                # Update detail view.
                for pageId in [PAGE_RECOMMEND, PAGE_REPO, PAGE_UPGRADE, PAGE_UNINSTALL]:
                    if self.detailViewDict.has_key(pageId):
                        detailView = self.detailViewDict[pageId]
                        detailView.initNormalStatus(pkgName, False)
                    elif pageId == PAGE_UNINSTALL and self.searchViewDict.has_key(pageId):
                        searchView = self.searchViewDict[pageId].searchView
                        searchView.initUninstallStatus(pkgName, True)
            else:
                print "Impossible: %s not in RepoCache" % (pkgName)

    def updateDownloadManageView(self, pkgName, appStatus, updateVote=False):
        '''Update download manage view.'''
        downloadManageView = self.downloadManagePage.downloadManageView
        if appStatus in [APP_STATE_DOWNLOADING, 
                         APP_STATE_INSTALLING,
                         APP_STATE_UPGRADING]:
            # Switch status if exist in list.
            if downloadManageView.itemDict.has_key(pkgName):
                downloadManageView.switchToStatus(pkgName, appStatus, updateVote)
            # Else refresh download manage view.
            else:
                self.refreshDownloadManageView(pkgName)
        elif appStatus == APP_STATE_DOWNLOAD_PAUSE:
            # Switch status.
            downloadManageView.switchToStatus(pkgName, appStatus, updateVote)
            
            # Add package in pause list.
            self.addInPauseList(pkgName)
        elif appStatus in [APP_STATE_NORMAL, APP_STATE_UPGRADE, APP_STATE_INSTALLED]:
            # Refresh download manage view.
            self.refreshDownloadManageView(pkgName)
        else:
            print "Impossible status: %s (%s)" % (pkgNum, appStatus)
            
    def refreshDownloadManageView(self, pkgName):
        '''Refresh download manage view.'''
        # Remove from pause list.
        self.removeFromPauseList(pkgName)
        
        # Get running number.
        pkgNum = self.getRunningNum()
        
        # Update topbar status.
        self.downloadManagePage.topbar.updateNum(pkgNum)
        
        # Update download manage view status.
        self.downloadManagePage.downloadManageView.update(pkgNum)
        
        # Update download icon number.
        self.navigatebar.downloadIcon.queue_draw()

    def updateUninstallView(self, pkgName, isAdd):
        '''Update uninstall view.'''
        if isAdd:
            self.repoCache.addPkgInUninstallableList(pkgName)
        else:
            self.repoCache.removePkgFromUninstallableList(pkgName)

        pkgNum = len(self.repoCache.uninstallablePkgs)
        self.uninstallPage.topbar.updateNum(pkgNum)

        uninstallView = self.uninstallPage.uninstallView
        uninstallView.update(pkgNum)
        
    def addIgnorePkg(self, pkgName):
        '''Add package in ignore list.'''
        # Add package in ignore list.
        self.repoCache.addPkgInIgnoreList([pkgName])
        
        # Get number of upgradable packages.
        pkgNum = self.repoCache.getUpgradableNum()
        ignoreNum = self.repoCache.getIgnoreNum()
        
        # Update topbar.
        self.updatePage.topbar.updateNum(pkgNum)
        self.updatePage.topbar.updateIgnoreNum(ignoreNum)
        
        # Update view.
        updateView = self.updatePage.updateView
        updateView.unselectPkg(pkgName) # remove from select list
        updateView.update(pkgNum)
        
        # Update notify number.
        self.navigatebar.updateIcon.queue_draw()
        
    def removeIgnorePkgs(self, pkgNames):
        '''Remove package from ignore list.'''
        # Remove package from ignore list.
        self.repoCache.removePkgFromIgnoreList(pkgNames)
        
        # Get number of upgradable packages.
        ignoreNum = self.repoCache.getIgnoreNum()
        
        # Update topbar.
        self.ignorePage.topbar.updateNum(ignoreNum)
        
        # Update view.
        ignoreView = self.ignorePage.ignoreView
        updateView = self.updatePage.updateView
        for pkgName in deepcopy(pkgNames):
            ignoreView.unselectPkg(pkgName)
            updateView.selectPkg(pkgName)
        ignoreView.update(ignoreNum)
        
        # Update notify number.
        self.navigatebar.updateIcon.queue_draw()
        
    def showIgnorePage(self):
        '''Show ignore page.'''
        # Enable tag.
        self.entryIgnorePage = True
        
        # Show ignore page.
        self.selectPage(PAGE_UPGRADE)

    def exitIgnorePage(self):
        '''Exit ignore page.'''
        # Disable tag.
        self.entryIgnorePage = False
        
        # Get number of upgradable packages.
        pkgNum = self.repoCache.getUpgradableNum()
        ignoreNum = self.repoCache.getIgnoreNum()
        
        # Update topbar.
        self.updatePage.topbar.updateNum(pkgNum)
        self.updatePage.topbar.updateIgnoreNum(ignoreNum)
        
        # Update view.
        self.updatePage.updateView.update(pkgNum)
        
        # Show update page.
        self.selectPage(PAGE_UPGRADE)

    def initMainWindow(self):
        '''Init main window.'''
        # Create main window.
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_decorated(False)

        # Init.
        window.set_title(__("Deepin Software Center"))
        window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        (width, height) = utils.getScreenSize(window)
        window.set_default_size(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        window.set_geometry_hints(
            None,
            DEFAULT_WINDOW_WIDTH,  # minimum width
            DEFAULT_WINDOW_HEIGHT, # minimum height
            -1, -1, -1, -1, -1, -1, -1, -1
            )

        # Set icon.
        gtk.window_set_default_icon_from_file("../icon/icon.ico")

        return window

    def minWindow(self):
        '''Minimum window.'''
        self.window.iconify()

    def doubleClickWindow(self, widget, event):
        '''Handle double click on window.'''
        if utils.isDoubleClick(event):
            self.toggleWindow()

    def toggleWindow(self):
        '''Toggle window.'''
        if self.hasMax:
            self.window.unmaximize()
        else:
            self.window.maximize()

        self.hasMax = not self.hasMax
        
        # Hide popup window.
        self.hidePopupWindow()

    def closeWindow(self):
        '''Close window'''
        # Hide window immediately when user click close button,
        # user will feeling this software very quick, ;p
        self.window.hide_all()

        self.destroy(self.window)

    def destroy(self, widget, data=None):
        '''Destroy main window.'''
        # Stop download thread.
        # if self.downloadQueue != None and self.downloadQueue.signalChannel != None:
        #     self.downloadQueue.signalChannel.put("STOP")
        if self.downloadQueue != None:
            self.downloadQueue.stopAllDownloads()

        # Close socket.
        self.socketThread.socket.close()
        
        gtk.main_quit()
        
        # Exit command proxy.
        sendCommand("exit")
        
    def main(self):
        '''Main'''
        # Connect components.
        self.window.add(self.mainBox)
        self.mainBox.pack_start(self.topbar, False)
        self.topbar.add(self.topbox)
        self.topbox.pack_start(self.titlebar.box, False)
        self.topbox.pack_start(self.navigatebar.box, False)
        self.mainBox.pack_start(self.bodyBox)
        self.bodyBox.pack_start(self.leftLine, False, False)
        self.bodyBox.pack_start(self.contentBox)
        self.bodyBox.pack_start(self.rightLine, False, False)

        # Add statusbar.
        self.mainBox.pack_start(self.statusbar.eventbox, False, False)

        # Adjust body box height.
        topbarHeight = appTheme.getDynamicPixbuf("topbar/background.png").getPixbuf().get_height()
        subCategoryHeight = appTheme.getDynamicPixbuf("category/sidebar_normal.png").getPixbuf().get_height()
        subCategoryNum = len(CLASSIFY_LIST)
        self.bodyBox.set_size_request(-1, topbarHeight + subCategoryHeight * subCategoryNum)

        # Set main window.
        self.window.connect("destroy", self.destroy)
        self.window.show_all()

        # Select software update page if add "show-update" option.
        if len(sys.argv) >= 2 and sys.argv[1] == "show-update":
            self.defaultPageId = PAGE_UPGRADE
            
        # Listen socket message for select upgrade page.
        self.socketThread = SocketThread(self.showUpgrade, self.raiseToTop)
        self.socketThread.start()
        
        # Init thread for long time calculate.
        # To make startup faster.
        initThread = InitThread(self)
        initThread.start()
        
        # Run.
        gtk.main()
        
    @postGUI
    def prevInitThread(self):
        '''Execute before init thread start.'''
        backgroundBox = gtk.EventBox()
        backgroundBox.connect("expose-event", lambda w, e: drawBackground(w, e, appTheme.getDynamicColor("background")))
        
        waitBox = gtk.HBox()
        waitBoxAlign = gtk.Alignment()
        waitBoxAlign.set(0.5, 0.5, 0.0, 0.0)
        waitBoxAlign.add(waitBox)
        backgroundBox.add(waitBoxAlign)
        
        waitAnimation = DynamicImage(
            waitBox,
            appTheme.getDynamicPixbufAnimation("wait.gif"),
            ).image
        waitBox.pack_start(waitAnimation)
        
        waitLabel = gtk.Label()
        waitLabel.set_markup(
            "<span foreground='%s' size='%s'>%s</span>" % (
                appTheme.getDynamicColor("waiting").getColor(),
                LABEL_FONT_LARGE_SIZE,
                __(" Loading, please wait ...")))
        waitAlign = gtk.Alignment()
        waitAlign.set(0.5, 0.7, 0.0, 0.0)
        waitAlign.add(waitLabel)
        waitBox.pack_start(waitAlign)
        
        self.contentBox.pack_start(backgroundBox)
        self.contentBox.show_all()
        
    @postGUI
    def postInitThread(self):
        '''Execute after init thread finish.'''
        # Select default page.
        self.selectPage(self.defaultPageId, False)
        
        # Save upgrade number.
        self.saveUpgradeNum()

        # Update List.
        self.updateList.start()
        
    @postGUI
    def raiseToTop(self):
        '''Raise main window to top of the window stack.'''
        # I don't know why function `gtk.window.present` can't work.
        # So use `gtk.window.set_keep_above` instead.
        self.window.set_keep_above(True)
        self.window.set_keep_above(False)
        
    def saveUpgradeNum(self):
        '''Save upgrade number.'''
        upgradeNum = self.repoCache.getUpgradableNum()
        writeFile("./upgradeNum", str(upgradeNum))

    def selectPage(self, pageId, hideWindow=True):
        '''Select recommend page.'''
        # Hide popup window.
        if hideWindow:
            self.hidePopupWindow()
        
        # Clean content.
        utils.containerRemoveAll(self.contentBox)

        self.navigatebar.pageId = pageId
        self.navigatebar.box.queue_draw()

        if self.detailViewDict.has_key(pageId):
            child = self.detailViewDict[pageId].scrolledWindow
        elif self.searchViewDict.has_key(pageId):
            child = self.searchViewDict[pageId].box
        else:
            if pageId == PAGE_RECOMMEND:
                child = self.recommendPage.scrolledwindow
            elif pageId == PAGE_REPO:
                child = self.repoPage.box
            elif pageId == PAGE_UPGRADE:
                if self.entryIgnorePage:
                    self.ignorePage = ignorePage.IgnorePage(
                        self.repoCache,
                        self.entryDetailView,
                        self.sendVote,
                        self.fetchVote,
                        self.removeIgnorePkgs,
                        self.exitIgnorePage)
                    child = self.ignorePage.box
                else:
                    child = self.updatePage.box
            elif pageId == PAGE_UNINSTALL:
                child = self.uninstallPage.box
            elif pageId == PAGE_DOWNLOAD_MANAGE:
                child = self.downloadManagePage.box

        self.contentBox.pack_start(child)
        self.contentBox.show_all()

    def selectCategory(self, category, categoryId):
        '''Select category.'''
        # Delete PAGE_REPO value from detailViewDict and searchViewDict.
        if self.detailViewDict.has_key(PAGE_REPO):
            del self.detailViewDict[PAGE_REPO]

        if self.searchViewDict.has_key(PAGE_REPO):
            del self.searchViewDict[PAGE_REPO]

        # Select repository page.
        self.selectPage(PAGE_REPO)

        # Select category.
        self.repoPage.selectCategory(category, categoryId)

    @postGUI
    def showUpgrade(self):
        '''Show upgrade page.'''
        # Delete PAGE_UPGRADE value from detailViewDict and searchViewDict.
        if self.detailViewDict.has_key(PAGE_UPGRADE):
            del self.detailViewDict[PAGE_UPGRADE]

        if self.searchViewDict.has_key(PAGE_UPGRADE):
            del self.searchViewDict[PAGE_UPGRADE]

        # Select upgrade page.
        self.selectPage(PAGE_UPGRADE)

    def entryDetailView(self, pageId, appInfo):
        '''Entry detail view.'''
        view = detailView.DetailView(
            self.aptCache, pageId, appInfo, self.switchStatus, self.downloadQueue, self.actionQueue,
            self.exitDetailView, self.message)
        self.detailViewDict[pageId] = view

        self.selectPage(pageId)

    def sendVote(self, name, vote):
        '''Send vote.'''
        sendVoteThread = SendVote(name, vote, self.message)
        sendVoteThread.start()

    def exitDetailView(self, pageId, pkgName):
        '''Exit detail view.'''
        # Remove detail view first.
        if self.detailViewDict.has_key(pageId):
            del self.detailViewDict[pageId]

        # Back page.
        self.selectPage(pageId)
        
        # Update vote.
        self.fetchVote(pageId, [pkgName], self.searchViewDict.has_key(pageId))

    def entrySearchView(self, pageId, keyword, pkgList):
        '''Entry search view.'''
        if pageId == PAGE_REPO:
            page = searchPage.SearchPage(
                self.searchQuery,
                pageId, self.repoCache, keyword, pkgList,
                self.switchStatus, self.downloadQueue,
                self.entryDetailView, self.sendVote, self.fetchVote, self.exitSearchView,
                self.launchApplication)
        elif pageId == PAGE_UNINSTALL:
            page = sp.SearchUninstallPage(
                self.searchQuery,
                pageId, self.repoCache, keyword, pkgList,
                self.actionQueue,
                self.entryDetailView, self.sendVote, self.fetchVote, self.exitSearchView,
                self.message)
        self.searchViewDict[pageId] = page
        self.selectPage(pageId)

    def exitSearchView(self, pageId):
        '''Exit search view.'''
        # Remove search view first.
        if self.searchViewDict.has_key(pageId):
            del self.searchViewDict[pageId]

        # Select page.
        self.selectPage(pageId)

    def fetchVote(self, pageId, appList, isSearchPage=False):
        '''Fetch vote data.'''
        fetchVoteThread = FetchVote(pageId, appList, self.updateVote, isSearchPage)
        fetchVoteThread.start()

    @postGUI
    def updateVote(self, voteJson, pageId, isSearchPage):
        '''Update vote UI.'''
        view = None
        if pageId == PAGE_REPO:
            if isSearchPage:
                if self.searchViewDict.has_key(pageId):
                    view = self.searchViewDict[pageId].searchView
            else:
                view = self.repoPage.repoView

        elif pageId == PAGE_UPGRADE:
            if self.entryIgnorePage:
                view = self.ignorePage.ignoreView
            else:
                view = self.updatePage.updateView
        elif pageId == PAGE_UNINSTALL:
            if isSearchPage:
                if self.searchViewDict.has_key(pageId):
                    view = self.searchViewDict[pageId].searchView
            else:
                view = self.uninstallPage.uninstallView

        if view != None:
            for vote in voteJson.items():
                try:
                    (pkgName, [starLevel, commentNum]) = vote
                    view.updateVoteView(pkgName, float(starLevel), commentNum)
                except Exception, e:
                    print "updateVote Error: %s" % (e)
                
    def upgradeSelectedPkgs(self, selectList):
        '''Upgrade select packages.'''
        # Get download and action packages.
        downloadPkgs = self.downloadQueue.getDownloadPkgs()
        actionPkgs = self.actionQueue.getActionPkgs()

        # Upgrade package if it not in wait queue.
        for pkgName in selectList:
            if not pkgName in downloadPkgs + actionPkgs:
                # Add in download queue.
                self.downloadQueue.addDownload(pkgName)
    
                # Switch status.
                self.repoCache.cache[pkgName].switchStatus(APP_STATE_DOWNLOADING)
                self.switchStatus(pkgName, APP_STATE_DOWNLOADING)

    def addInPauseList(self, pkgName):
        '''Add pause package in list.'''
        utils.addInList(self.pauseList, pkgName)
            
    def removeFromPauseList(self, pkgName):
        '''Remove pause package from list.'''
        utils.removeFromList(self.pauseList, pkgName)
            
    def getRunningPkgs(self):
        '''Get running packages.'''
        # Get install or upgrade list.
        actionList = []
        for (pkgName, actionType) in self.actionQueue.getActionQueue():
            if actionType != ACTION_UNINSTALL:
                actionList.append(pkgName)
                
        return actionList + self.downloadQueue.getDownloadPkgs() + self.pauseList
                
    def getRunningNum(self):
        '''Get running package number.'''
        runningList = self.getRunningPkgs()
        return len(runningList)
                
    def getRunningList(self, startIndex, endIndex):
        '''Get running (download, install or upgrade) action list.'''
        # Get running packages.
        pkgNames = self.getRunningPkgs()
        
        # Return application list.
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = pkgNames[index]
            appList.append(self.repoCache.cache[pkgName])
            
        return appList 
    
    def launchApplication(self, command):
        '''Launch application.'''
        self.message(__("Send startup request (%s)") % (command))
        sendCommand(command)
        
    def cleanDownloadCache(self):
        '''Clean download cache.'''
        # Get downloading packages.
        downloadingPkgs = self.downloadQueue.getDownloadPkgs()
        
        # Get action packages.
        actionPkgs = self.actionQueue.getActionPkgs()
        
        # Get packages.
        pkgs = downloadingPkgs + actionPkgs
        
        # Get depend packages.
        dependPkgs = []
        for pkgName in pkgs:
            for dependency in self.aptCache[pkgName].candidate.dependencies:
                dependPkgs.append(map(lambda baseDep: baseDep.name, dependency.or_dependencies))
        
        # Get black list.
        debs = []
        for pList in dependPkgs:
            if pList != []:
                debs.append(os.path.basename(self.aptCache[pList[0]].candidate.filename))
                
        # Init clean size.
        packageNum = 0
        cleanSize = 0
                
        # Delete cache directory.
        archiveDir = apt_pkg.config.find_dir('Dir::Cache::Archives')
        partialDir = os.path.join(archiveDir, "deepin_software_center_cache")
        for pDir in os.listdir(partialDir):
            # Get path.
            dirPath = os.path.join(partialDir, pDir)
                
            if pDir in pkgs:
                print "*** Can't remove directory: %s, software center using it." % (pDir)
            elif os.path.isdir(dirPath):
                # Update number.
                packageNum += len(os.listdir(dirPath))
                cleanSize += utils.getDirSize(dirPath)
                
                # Remove directory.
                utils.removeDirectory(dirPath)
                print "Delete directory: %s" % (dirPath)
                
        # Delete deb packages.
        for debFile in os.listdir(archiveDir):
            # Get path.
            filePath = os.path.join(archiveDir, debFile)
            
            if os.path.isfile(filePath) and os.path.splitext(debFile):
                if debFile in debs:
                    print "*** Can't remove deb file: %s, software center using it." % (debFile)
                else:
                    # Update number.
                    packageNum += 1
                    cleanSize += os.path.getsize(filePath)
                    
                    # Remove file.
                    utils.removeFile(filePath)
                    print "Delete deb file: %s" % (filePath)
                    
        # Notify clean size.
        if cleanSize == 0:
            if pkgs == []:
                self.message(__("Congratulations, your system is clean."))
            else:
                self.message(__("Software Center is using the downloaded package, please wait clearing."))
        else:
            self.message(__("Cleaned up %s package, release %s space.") % (packageNum, utils.formatFileSize(cleanSize)))            
        
class InitThread(td.Thread):
    '''Add long time calculate in init thread to make startup faster.'''

    def __init__(self, softwareCenter):
        '''Init anonymity thread.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit
        
        self.softwareCenter = softwareCenter

    # @printExecTime            
    def run(self):
        '''Run.'''
        # Execute operation before init start.
        center = self.softwareCenter
        center.prevInitThread()
        
        # Init apt operation.
        apt_pkg.init()
        center.aptCache = apt.Cache()
        
        # Get update data directory.
        osVersion = getOSVersion()
        if osVersion == OS_VERSION:
            if os.path.exists(UPDATE_DATA_DIR):
                center.updateDataDir = UPDATE_DATA_DIR
                # center.updateDataDir = UPDATE_DATA_BACKUP_DIR
                print "Use newest data from %s" % UPDATE_DATA_DIR
            else:
                center.updateDataDir = UPDATE_DATA_BACKUP_DIR
                print "Haven't found directory: %s, use %s instead" % (UPDATE_DATA_DIR, UPDATE_DATA_BACKUP_DIR)
        else:
            center.updateDataDir = UPDATE_DATA_BACKUP_DIR
            print "Your system is not %s, deepin software center won't update `recommend list` to keep your system safety, if you want deepin software center update `recommend list` on your system, please contact AUTHOR (lazycat.manatee@gmail.com)." % OS_VERSION
        
        # Init repo cache.
        center.repoCache = repoCache.RepoCache(
            center.aptCache,
            center.updateDataDir,
            )
        
        # Init update list.
        center.updateList = updateList.UpdateList(center.aptCache, center.statusbar)       
        
        # Init search query.
        center.searchQuery = search.Search(center.repoCache, center.message, center.statusbar)
        
        # Download queue.
        center.downloadQueue = download.DownloadQueue(
            center.downloadUpdateCallback,
            center.downloadFinishCallback,
            center.downloadFailedCallback,
            center.message
            )

        # Action queue.
        center.actionQueue = action.ActionQueue(
            center.actionUpdateCallback,
            center.actionFinishCallback,
            center.actionFailedCallback,
            center.message
            )

        # Init pages.
        center.recommendPage = recommendPage.RecommendPage(
            center.repoCache,
            center.switchStatus,
            center.downloadQueue,
            center.entryDetailView,
            center.selectCategory,
            center.launchApplication,
            center.updateDataDir,
            )
        center.repoPage = repoPage.RepoPage(
            center.repoCache,
            center.searchQuery,
            center.switchStatus,
            center.downloadQueue,
            center.entryDetailView,
            center.entrySearchView,
            center.sendVote,
            center.fetchVote,
            center.launchApplication,
            )
        center.updatePage = updatePage.UpdatePage(
            center.repoCache,
            center.switchStatus,
            center.downloadQueue,
            center.entryDetailView,
            center.sendVote,
            center.fetchVote,
            center.upgradeSelectedPkgs,
            center.addIgnorePkg,
            center.showIgnorePage
            )
        center.ignorePage = None
        center.uninstallPage = uninstallPage.UninstallPage(
            center.repoCache,
            center.searchQuery,
            center.actionQueue,
            center.entryDetailView,
            center.entrySearchView,
            center.sendVote,
            center.fetchVote,
            center.message,
            )
        
        center.downloadManagePage = downloadManagePage.DownloadManagePage(
            center.repoCache,
            center.getRunningNum,
            center.getRunningList,
            center.switchStatus,
            center.downloadQueue,
            center.entryDetailView,
            center.sendVote,
            center.fetchVote,
            center.cleanDownloadCache,
            )
        
        # Set callback for navigatebar.
        center.navigatebar.setUpgradableNumCallback(
            center.repoCache.getUpgradableNum)
        center.navigatebar.setSelectPageCallback(
            center.selectPage)
        center.navigatebar.setRunningNumCallback(
            center.getRunningNum)
        
        # Update update icon.
        center.navigatebar.updateIcon.queue_draw()
        
        # Execute operation when finish init.
        center.postInitThread()
                
class FetchVote(td.Thread):
    '''Fetch vote.'''

    def __init__(self, pageId, pkgNames, updateVoteCallback, isSearchPage):
        '''Init for fetch vote.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit

        self.pageId = pageId
        self.isSearchPage = isSearchPage
        self.updateVoteCallback = updateVoteCallback

        self.pkgArguments = ""
        for pkgName in pkgNames:
            self.pkgArguments += pkgName + ","
        self.pkgArguments = self.pkgArguments.rstrip(",") # remove last , from arguments

    def run(self):
        '''Run.'''
        try:
            args = {'n' : self.pkgArguments, "t" : "comment"}
            connection = urllib2.urlopen(
                "%s/softcenter/v1/mark" % (SERVER_ADDRESS),
                data=urllib.urlencode(args),
                timeout=POST_TIMEOUT
                )
            voteJson = json.loads(connection.read())            
            self.updateVoteCallback(voteJson, self.pageId, self.isSearchPage)
        except Exception, e:
            print "Fetch vote data failed: %s." % (e)

class SendVote(td.Thread):
    '''Vote'''

    def __init__(self, name, vote, messageCallback):
        '''Init for vote.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit
        self.name = name
        self.vote = vote
        self.messageCallback = messageCallback

    def run(self):
        '''Run'''
        try:
            voteFile = "../voteBlacklist/%s" % (self.name)
            if os.path.exists(voteFile) and getLastUpdateHours(voteFile) <= 24:
            # if False:
                self.messageCallback(__("To ensure fairness, only a day to %s score once.") % (self.name))
            else:
                args = {'n' : self.name, 'm' : self.vote}
                connection = urllib2.urlopen(
                    "%s/softcenter/v1/mark" % (SERVER_ADDRESS),
                    data=urllib.urlencode(args),
                    timeout=POST_TIMEOUT
                    )
                self.messageCallback(__("%s vote success, thanks!") % (self.name))
                utils.touchFile(voteFile)
        except Exception, e:
            self.messageCallback(__("%s vote failed, please check your network link.") % (self.name))
            print "Error: ", e

class SocketThread(td.Thread):
    '''Socket thread.'''

    def __init__(self, showUpdateCallback, raiseToTopCallback):
        '''Init socket thread.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit

        self.showUpdateCallback = showUpdateCallback
        self.raiseToTopCallback = raiseToTopCallback

    def run(self):
        '''Run.'''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # make sure socket port always work
        self.socket.bind(SOCKET_SOFTWARECENTER_ADDRESS)

        while True:
            data, addr = self.socket.recvfrom(2048)
            print "received: '%s' from %s" % (data, addr)
            if data == "showUpdate":
                self.showUpdateCallback()
            elif data == "show":
                self.raiseToTopCallback()

        self.socket.close()
        
class SendUninstallCount(td.Thread):
    '''Send uninstall count.'''
	
    def __init__(self, pkgName):
        '''Init for vote.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        self.pkgName = pkgName

    def run(self):
        '''Run'''
        try:
            args = {'a' : 'u', 'n' : self.pkgName}
            
            connection = urllib2.urlopen(
                "%s/softcenter/v1/analytics" % (SERVER_ADDRESS),
                data=urllib.urlencode(args),
                timeout=POST_TIMEOUT
                )
            print "Send uninstall count (%s) successful." % (self.pkgName)
        except Exception, e:
            print "Send uninstall count (%s) failed." % (self.pkgName)
            print "Error: ", e
            
            
        
if __name__ == "__main__":
    DeepinSoftwareCenter().main()

#  LocalWords:  param os RepoCache upgradabled topbar REPO
#  LocalWords:  selectPage statusbar detailViewDict searchViewDict setDaemon
