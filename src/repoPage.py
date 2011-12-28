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
from utils import *
import apt_pkg
import categorybar
import gobject
import gtk
import repoView
import search
import searchCompletion as sc
import sortedDict
import utils

class RepoPage(object):
    '''Interface for repository page.'''
    
    def __init__(self, repoCache, searchQuery, switchStatus, downloadQueue, entryDetailCallback, 
                 entrySearchCallback, sendVoteCallback, fetchVoteCallback, 
                 launchApplicationCallback):
        '''Init for repository page.'''
        # Init.
        self.repoCache = repoCache
        self.box = gtk.VBox()
        self.categorybar = categorybar.CategoryBar(
            self.repoCache.getCategorys(), 
            self.repoCache.getCategoryNumber,
            self.selectCategory,
            )
        self.contentBox = gtk.HBox()
        self.topbar = Topbar(
            searchQuery,
            CLASSIFY_WEB, 
            self.repoCache.getCategoryNumber(CLASSIFY_WEB),
            self.repoCache.cache.values(),
            entrySearchCallback,
            self.updateCategory)
        self.repoView = repoView.RepoView(
            CLASSIFY_WEB, 
            self.repoCache.getCategoryNumber(CLASSIFY_WEB),
            self.repoCache.getAppList,
            self.topbar.getSortType,
            switchStatus, 
            downloadQueue,
            entryDetailCallback,
            sendVoteCallback,
            fetchVoteCallback,
            launchApplicationCallback
            )

        # Connect components.
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.pack_start(self.contentBox)
        self.contentBox.pack_start(self.categorybar.box, False, False)
        self.contentBox.pack_start(self.repoView.scrolledwindow)
        self.box.show_all()
        
    def updateCategory(self):
        '''Update category.'''
        self.selectCategory(self.categorybar.categoryName,
                            self.categorybar.categoryId)

    def selectCategory(self, categoryName, categoryId):
        '''Select category.'''
        self.categorybar.categoryName = categoryName
        self.categorybar.categoryId = categoryId
        self.categorybar.box.queue_draw()
        
        # Update application view.
        self.repoView.update(
            categoryName, 
            self.repoCache.getCategoryNumber(categoryName)
            )

        # Reset repoView's index.
        self.repoView.setSelectItemIndex(0)

class Topbar(object):
    '''Top bar.'''

    SORT_BOX_PADDING_X = 50
    SEARCH_ENTRY_WIDTH = 300
    
    def __init__(self, searchQuery, category, itemNum, appInfos, 
                 entrySearchCallback, updateCategoryCallback):
        '''Init for top bar.'''
        self.searchQuery = searchQuery
        self.paddingX = 5
        self.box = gtk.HBox()
        self.boxAlign = gtk.Alignment()
        self.boxAlign.set(0.0, 0.5, 1.0, 1.0)
        self.boxAlign.set_padding(0, 0, TOPBAR_PADDING_LEFT, TOPBAR_PADDING_RIGHT)
        self.boxAlign.add(self.box)
        self.eventbox = gtk.EventBox()
        self.eventbox.add(self.boxAlign)
        drawTopbar(self.eventbox)
        self.numLabel = gtk.Label()
        self.entrySearchCallback = entrySearchCallback
        self.updateCategoryCallback = updateCategoryCallback
        
        # Add classify number.
        self.box.pack_start(self.numLabel)
        
        # Add sort buttons.
        self.sortBox = gtk.HBox()
        self.sortAlign = gtk.Alignment()
        self.sortAlign.set(0.0, 0.5, 1.0, 1.0)
        self.sortAlign.add(self.sortBox)
        
        self.sortRecommendId = "sortRecommend"
        self.sortDownloadId = "sortDownload"
        self.sortVoteId = "sortVote"
        self.sortType = self.sortRecommendId

        (self.sortRecommendBox, self.sortRecommendEventBox) = setDefaultRadioButton(
            __("Sort By Recommend"), self.sortRecommendId, self.setSortType, self.getSortType, self.updateRadioStatus
            )

        (self.sortDownloadBox, self.sortDownloadEventBox) = setDefaultRadioButton(
            __("Sort By Download"), self.sortDownloadId, self.setSortType, self.getSortType, self.updateRadioStatus
            )
        
        (self.sortVoteBox, self.sortVoteEventBox) = setDefaultRadioButton(
            __("Sort By Vote"), self.sortVoteId, self.setSortType, self.getSortType, self.updateRadioStatus
            )
        
        self.sortButtonPaddingX = 10
        self.sortBox.pack_start(self.sortRecommendBox, False, False, self.sortButtonPaddingX)
        self.sortBox.pack_start(self.sortDownloadBox, False, False, self.sortButtonPaddingX)
        self.sortBox.pack_start(self.sortVoteBox, False, False, self.sortButtonPaddingX)
        self.box.pack_start(self.sortAlign)
        
        # Add search entry and label.
        (self.searchEntry, searchAlign, self.searchCompletion) = newSearchUI(
            __("Please enter the name you want to search for software, version or other information"),
            lambda text: getCandidates(map (lambda appInfo: appInfo.pkg.name, appInfos), text),
            self.clickCandidate,
            self.search)
        self.box.pack_start(searchAlign)
        
    def updateRadioStatus(self):
        '''Update radio status.'''
        self.sortRecommendEventBox.queue_draw()    
        self.sortDownloadEventBox.queue_draw()    
        self.sortVoteEventBox.queue_draw()    
        
        self.updateCategoryCallback()
        
    def setSortType(self, sType):
        '''Set sort type.'''
        self.sortType = sType
        
    def getSortType(self):
        '''Get sort type.'''
        return self.sortType
    
    def search(self, editable):
        '''Search'''
        content = self.searchEntry.get_chars(0, -1)
        keywords = content.split()
        if len(keywords) != 0:
            pkgList = self.searchQuery.query(keywords)
            if pkgList != []:
                self.entrySearchCallback(PAGE_REPO, content, pkgList)
        
    def clickCandidate(self, candidate):
        '''Click candidate.'''
        keyword = self.searchEntry.get_chars(0, -1)
        self.entrySearchCallback(PAGE_REPO, keyword, [candidate])

#  LocalWords:  categorybar repoView's sortAlign efe
