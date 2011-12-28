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
from lang import __, getDefaultLanguage
from utils import *
import apt_pkg
import categorybar
import gtk
import sortedDict
import utils

class AppInfo(object):
    '''Application information.'''
    def __init__(self, pkg):
        '''Init for application information.'''
        # Init.
        self.pkg = pkg
        self.execPath = getPkgExecPath(self.pkg)
        
        if pkg.is_upgradable:
            self.status = APP_STATE_UPGRADE
        elif pkg.is_installed:
            self.status = APP_STATE_INSTALLED
        else:
            self.status = APP_STATE_NORMAL
            
        self.initStatus()
        
    def initStatus(self):
        '''Init status.'''
        self.downloadingFeedback = __("Action Wait Download")
        self.downloadingProgress = 0
        
        self.downloadPauseFeedback = ''
        
        self.installingFeedback = __("Action Wait Install")
        self.installingProgress = 0
        
        self.upgradingFeedback = __("Action Wait Update")
        self.upgradingProgress = 0
        
        self.uninstallingFeedback = __("Action Wait Uninstall")
        self.uninstallingProgress = 0
        
    def switchStatus(self, appStatus):
        '''Switch status.'''
        self.status = appStatus
        
        if appStatus in [APP_STATE_NORMAL, APP_STATE_INSTALLED]:
            self.initStatus()
        elif appStatus == APP_STATE_DOWNLOADING:
            self.downloadingProgress = 0
            self.downloadingFeedback = __("Action Wait Download")
        elif appStatus == APP_STATE_DOWNLOAD_PAUSE:
            self.downloadPauseFeedback = __("Pause")
        elif appStatus == APP_STATE_INSTALLING:
            self.installingProgress = 0
            self.installingFeedback = __("Action Wait Download")
        elif appStatus == APP_STATE_UPGRADING:
            self.upgradingProgress = 0
            self.upgradingFeedback = __("Action Wait Update")
        elif appStatus == APP_STATE_UNINSTALLING:
            self.uninstallingProgress = 0
            self.uninstallingFeedback = __("Action Wait Uninstall")
        
    def updateDownloadStatus(self, progress, feedback, status):
        '''Update download status'''
        self.status = status
        self.downloadingProgress = progress
        self.downloadingFeedback = feedback
        
    def updateInstallStatus(self, progress, feedback):
        '''Update install status.'''
        self.status = APP_STATE_INSTALLING
        self.installingProgress = progress
        self.installingFeedback = feedback

    def updateUpgradeStatus(self, progress, feedback):
        '''Update upgrade status.'''
        self.status = APP_STATE_UPGRADING
        self.upgradingProgress = progress
        self.upgradingFeedback = feedback

    def updateUninstallStatus(self, progress, feedback):
        '''Update uninstall status.'''
        self.status = APP_STATE_UNINSTALLING
        self.uninstallingProgress = progress
        self.uninstallingFeedback = feedback

class RepoCache(object):
    '''Repository cache.'''

    # @printExecTime
    def __init__(self, cache, updateDataDir):
        '''Init for repository cache.'''
        # Init.
        self.cache = {}
        self.updateDataDir = updateDataDir
        self.upgradablePkgs = []
        ignorePkgs = evalFile("./ignorePkgs", True)
        if ignorePkgs == None:
            self.ignorePkgs = []
        else:
            self.ignorePkgs = ignorePkgs
        self.uninstallablePkgs = []
        self.categoryDict = sortedDict.SortedDict(CLASSIFY_LIST)

        # Scan category dict.
        whiteList = []
        sortRecommendDir = self.updateDataDir + "pkgClassify/sortByDefault/%s/" % (getDefaultLanguage())
        sortDownloadDir =  self.updateDataDir + "pkgClassify/sortByDownload/"
        sortVoteDir =  self.updateDataDir + "pkgClassify/sortByVote/"
        
        for (categoryType, categoryFile) in CLASSIFY_FILES:
            sortRecommendList = []
            sortDownloadList = []
            sortVoteList = []
            
            # Scan default sort list.
            for line in open(sortRecommendDir + categoryFile).readlines():
                pkgName = line.rstrip("\n")
                if cache.has_key(pkgName) and cache[pkgName].candidate != None:
                    # Append in default sort list.
                    sortRecommendList.append(pkgName)
                    
                    # Add in white list.
                    whiteList.append(pkgName)
                else:
                    print pkgName
                    # print "Haven't found package '%s' in current system (%s). Make sure you use Linux Deepin or add deepin sourcelist." % (pkgName, sortRecommendDir + categoryFile)
                    
            # Scan download sort list.
            for line in open(sortDownloadDir + categoryFile).readlines():
                pkgName = line.rstrip("\n")
                if cache.has_key(pkgName) and cache[pkgName].candidate != None:
                    # Append in download sort list.
                    sortDownloadList.append(pkgName)
                else:
                    print pkgName
                    # print "Haven't found package '%s' in current system (%s). Make sure you use Linux Deepin or add deepin sourcelist." % (pkgName, sortDownloadDir + categoryFile)
                    
            # Scan vote sort list.
            for line in open(sortVoteDir + categoryFile).readlines():
                pkgName = line.rstrip("\n")
                if cache.has_key(pkgName) and cache[pkgName].candidate != None:
                    # Append in vote sort list.
                    sortVoteList.append(pkgName)
                else:
                    print pkgName
                    # print "Haven't found package '%s' in current system (%s). Make sure you use Linux Deepin or add deepin sourcelist." % (pkgName, sortVoteDir + categoryFile)
                    
            # Add sort list in category dict.
            (classifyIcon, _) = self.categoryDict[categoryType]
            self.categoryDict[categoryType] = (classifyIcon, (sortRecommendList, sortDownloadList, sortVoteList))
            
        # Build white list dict.
        self.whiteListDict = dict.fromkeys(whiteList)

        # Scan all packages to store and rank. 
        for pkg in cache:
            if pkg.candidate == None:
                print "Can't find candidate information for %s, skip it." % (pkg.name)
            else:
                # Add AppInfo.
                self.cache[pkg.name] = AppInfo(pkg)
                
                # Add upgradable packages.
                if pkg.is_upgradable and pkg.name not in self.ignorePkgs:
                    self.upgradablePkgs.append(pkg.name)
                    
                # Add uninstall packages.
                # Package must not essential and not library packages.
                if self.isPkgUninstallable(pkg):
                    self.uninstallablePkgs.append(pkg.name)
                    
        # Resort.
        self.upgradablePkgs = self.sortPackages(self.upgradablePkgs)
        self.ignorePkgs = self.sortPackages(self.ignorePkgs)
        
        # Find package in white list haven't execute path, just for develop usage.
        # self.testExecPath(whiteList)

    def testExecPath(self, whiteList):
        '''Find package in white list haven't execute path.'''
        for pkgName in whiteList:
            if self.cache[pkgName].execPath == None:
                print pkgName
        
    def getAppList(self, category, sortType, startIndex, endIndex):
        '''Get application list in given range.'''
        (_, (sortRecommendList, sortDownloadList, sortVoteList)) = self.categoryDict[category]
        if sortType == "sortRecommend":
            pkgNames = sortRecommendList
        elif sortType == "sortDownload":
            pkgNames = sortDownloadList
        elif sortType == "sortVote":
            pkgNames = sortVoteList
        else:
            print "Unknown sorte type: %s" % (sortType)
            
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = pkgNames[index]
            appList.append(self.cache[pkgName])
        return appList
    
    def getCategoryNumber(self, category):
        '''Get sub category number.'''
        (_, (categoryList, _, _)) = self.categoryDict[category]
        return len(categoryList)
    
    def getCategorys(self):
        '''Get category list.'''
        return map (lambda (categoryName, (categoryIcon, _)): (categoryName, categoryIcon),
                    self.categoryDict.items())
    
    def getCategoryNames(self):
        '''Get category names.'''
        return map (lambda (categoryName, (categoryIcon, _)): categoryName,
                    self.categoryDict.items())

    def getUpgradableNum(self):
        '''Get upgradable packages number.'''
        return len(self.upgradablePkgs)
    
    def getIgnoreNum(self):
        '''Get ignore package number.'''
        return len(self.ignorePkgs)    
    
    def getUpgradableAppList(self, startIndex, endIndex):
        '''Get upgradable application list.'''
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = self.upgradablePkgs[index]
            appList.append(self.cache[pkgName])
        return appList
    
    def getIgnoreAppList(self, startIndex, endIndex):
        '''Get Ignore application list.'''
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = self.ignorePkgs[index]
            appList.append(self.cache[pkgName])
        return appList
    
    def getUninstallableAppList(self, startIndex, endIndex):
        '''Get un-installable application list.'''
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = self.uninstallablePkgs[index]
            appList.append(self.cache[pkgName])
        return appList
    
    def removePkgFromUpgradableList(self, pkgName):
        '''Remove package from upgradable list.'''
        utils.removeFromList(self.upgradablePkgs, pkgName)
    
    def removePkgFromUninstallableList(self, pkgName):
        '''Remove package from uninstallable list.'''
        utils.removeFromList(self.uninstallablePkgs, pkgName)
    
    def addPkgInUninstallableList(self, pkgName):
        '''Add package in uninstallable list.'''
        if self.cache.has_key(pkgName):
            pkg = self.cache[pkgName].pkg
            if self.isPkgUninstallable(pkg, False) and not pkgName in self.uninstallablePkgs:
                self.uninstallablePkgs.append(pkgName)
                self.uninstallablePkgs = sorted(self.uninstallablePkgs)    

    def isPkgUninstallable(self, pkg, checkInstalled=True):
        '''Is package is uninstallable?'''
        if checkInstalled:
            return pkg.is_installed and self.whiteListDict.has_key(pkg.name)
        else:
            return self.whiteListDict.has_key(pkg.name)

    def addPkgInIgnoreList(self, pkgNames):
        '''Add package in ignore list.'''
        for pkgName in pkgNames:
            # Add package in ignore list.
            utils.addInList(self.ignorePkgs, pkgName)
                
            # Remove package from upgradable list.
            self.removePkgFromUpgradableList(pkgName)
        
        # Record.
        self.ignorePkgs = self.sortPackages(self.ignorePkgs)
                
        # Update file content.
        writeFile("./ignorePkgs", str(self.ignorePkgs))

    def removePkgFromIgnoreList(self, pkgNames):
        '''Remove package in ignore list.'''
        for pkgName in pkgNames:
            # Remove package from ignore list.
            utils.removeFromList(self.ignorePkgs, pkgName)
                
            # Add package to upgradable list if package upgradable.
            if self.cache.has_key(pkgName) and self.cache[pkgName].pkg.is_upgradable:
                self.upgradablePkgs.append(pkgName)
            
        # Record.
        self.upgradablePkgs = self.sortPackages(self.upgradablePkgs)
                
        # Update file content.
        writeFile("./ignorePkgs", str(self.ignorePkgs))
        
    def sortPackages(self, pkgs, keyword=None):
        '''Sort packages, first sort packages in white list, then other packages.'''
        # Don't consider keyword power if keyword is None.
        if keyword == None:
            # Init.
            whiteList = []
            otherlist = []
            
            # Split packages.
            for pkgName in pkgs:
                if self.whiteListDict.has_key(pkgName):
                    whiteList.append(pkgName)
                else:
                    otherlist.append(pkgName)
            
            return utils.sortAlpha(whiteList) + utils.sortAlpha(otherlist)
        # Otherwise sort package at front if package name match keyword.
        else:
            # Init.
            matchList = []
            whiteList = []
            otherList = []
            
            # Split packages.
            for pkgName in pkgs:
                if keyword in pkgName:
                    matchList.append(pkgName)
                elif self.whiteListDict.has_key(pkgName):
                    whiteList.append(pkgName)
                else:
                    otherList.append(pkgName)
                
            return utils.sortMatchKeyword(matchList, keyword) + utils.sortAlpha(whiteList) + utils.sortAlpha(otherList)

#  LocalWords:  pkgClassify AppInfo appList startIndex endIndex pkgName
#  LocalWords:  uninstallablePkgs removePkgFromUpgradableList upgradablePkgs
#  LocalWords:  removePkgFromUninstallableList isPkgUninstallable
#  LocalWords:  addPkgInUninstallableList checkInstalled
