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

from constant import *
import apt_pkg
import categorybar
import gtk
import pygtk
import sortedDict
import subCategorybar
import utils
pygtk.require('2.0')

class AppInfo:
    '''Application information.'''
    def __init__(self, pkg):
        '''Init for application information.'''
        # Init.
        self.pkg = pkg
        
        if pkg.is_upgradable:
            self.status = APP_STATE_UPGRADE
        elif pkg.is_installed:
            self.status = APP_STATE_INSTALLED
        else:
            self.status = APP_STATE_NORMAL
            
        self.initStatus()
        
    def initStatus(self):
        '''Init status.'''
        self.downloadingFeedback = '等待下载'
        self.downloadingProgress = 0
        
        self.downloadPauseFeedback = ''
        
        self.installingFeedback = '等待安装'
        self.installingProgress = 0
        
        self.upgradingFeedback = '等待升级'
        self.upgradingProgress = 0
        
        self.uninstallingFeedback = '等待卸载'
        self.uninstallingProgress = 0
        
    def switchStatus(self, appStatus):
        '''Switch status.'''
        self.status = appStatus
        
        if appStatus in [APP_STATE_NORMAL, APP_STATE_INSTALLED]:
            self.initStatus()
        elif appStatus == APP_STATE_DOWNLOADING:
            self.downloadingProgress = 0
            self.downloadingFeedback = "等待下载"
        elif appStatus == APP_STATE_DOWNLOAD_PAUSE:
            self.downloadPauseFeedback = "暂停"
        elif appStatus == APP_STATE_INSTALLING:
            self.installingProgress = 0
            self.installingFeedback = "等待安装"
        elif appStatus == APP_STATE_UPGRADING:
            self.upgradingProgress = 0
            self.upgradingFeedback = "等待升级"
        elif appStatus == APP_STATE_UNINSTALLING:
            self.uninstallingProgress = 0
            self.uninstallingFeedback = "等待卸载"
        
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

class RepoCache:
    '''Repository cache.'''

    def __init__(self, cache):
        '''Init for repository cache.'''
        # Init.
        self.cache = {}
        self.upgradablePkgs = []
        self.uninstallablePkgs = []
        self.categoryDict = sortedDict.SortedDict(CATEGORY_LIST)

        # Scan all packages to store and rank. 
        for pkg in cache:
            if pkg.candidate == None:
                print "Can't find candidate information for %s, skip it." % (pkg.name)
            else:
                # Add AppInfo.
                self.cache[pkg.name] = AppInfo(pkg)
                
                # Rank packages.
                self.rankPkg(pkg)
                
                # Add upgradable packages.
                if pkg.is_upgradable:
                    self.upgradablePkgs.append(pkg.name)
                    
                # Add uninstall packages.
                # Package must not essential and not library packages.
                if utils.isPkgUninstallable(pkg):
                    self.uninstallablePkgs.append(pkg.name)

    def rankPkg(self, pkg):
        '''Rank package.'''
        # Get package section
        pkgSection = pkg.candidate.section
        splitResult = pkgSection.split('/')
        if len (splitResult) == 2:
            # Remove repository prefix, such as, pick pkg from `universal/pkg`
            section = splitResult[1]
        else:
            section = pkgSection

        # Get category and sub-category.
        if RANK_DICT.has_key(section):
            (category, subCategory) = RANK_DICT[section]
        # Put in CATE_OTHERS/SUBCATE_OTHERS if got unknown section. 
        else:
            print "Unknown section : ", section
            (category, subCategory) = (CATE_OTHERS, SUBCATE_OTHERS)

        # Add in all item of category.
        (categoryItemIcon, categoryItem) = self.categoryDict[category]
        categoryItem[SUBCATE_ALL].append(pkg.name)
        categoryItem[subCategory].append(pkg.name)

    def getSubcategorys(self, category):
        '''Get sub category list.'''
        (_, categoryItem) = self.categoryDict[category]
        return categoryItem.keys()
    
    def getSubcategoryNumber(self, category, subCategory):
        '''Get sub category number.'''
        (_, categoryItem) = self.categoryDict[category]
        return len(categoryItem[subCategory])
    
    def getAppList(self, category, subCategory, startIndex, endIndex):
        '''Get application list in given range.'''
        (_, categoryItem) = self.categoryDict[category]
        pkgNames = categoryItem[subCategory]
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = pkgNames[index]
            appList.append(self.cache[pkgName])
        return appList
    
    def getCategorys(self):
        '''Get category list.'''
        return map (lambda (categoryName, (categoryIcon, _)): (categoryName, categoryIcon),
                    self.categoryDict.items())

    def getUpgradableAppList(self, startIndex, endIndex):
        '''Get upgradable application list.'''
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = self.upgradablePkgs[index]
            appList.append(self.cache[pkgName])
        return appList
    
    def getUninstallableAppList(self, startIndex, endIndex):
        '''Get uninstallable application list.'''
        appList = []
        for index in range(startIndex, endIndex):
            pkgName = self.uninstallablePkgs[index]
            appList.append(self.cache[pkgName])
        return appList
    
    def removePkgFromUpgradableList(self, pkgName):
        '''Remove package from upgradable list.'''
        if pkgName in self.upgradablePkgs:
            self.upgradablePkgs.remove(pkgName)
    
    def removePkgFromUninstallableList(self, pkgName):
        '''Remove package from uninstallable list.'''
        if pkgName in self.uninstallablePkgs:
            self.uninstallablePkgs.remove(pkgName)
    
    def addPkgInUninstallableList(self, pkgName):
        '''Add package in uninstallable list.'''
        if self.cache.has_key(pkgName):
            pkg = self.cache[pkgName].pkg
            if utils.isPkgUninstallable(pkg, False) and not pkgName in self.uninstallablePkgs:
                self.uninstallablePkgs.append(pkgName)
                self.uninstallablePkgs = sorted(self.uninstallablePkgs)    
