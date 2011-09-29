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
import apt_pkg
import categorybar
import gobject
import gtk
import pygtk
import repoView
import search
import searchCompletion as sc
import sortedDict
import utils
pygtk.require('2.0')

class RepoPage:
    '''Interface for repository page.'''
    
    def __init__(self, repoCache, searchQuery, switchStatus, downloadQueue, entryDetailCallback, 
                 entrySearchCallback, sendVoteCallback, fetchVoteCallback):
        '''Init for repository page.'''
        # Init.
        self.repoCache = repoCache
        self.box = gtk.VBox()
        self.categorybar = categorybar.CategoryBar(self.repoCache.getCategorys(), self.selectCategory)
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
            fetchVoteCallback
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
        
        # Redraw sub-categorybar bar.
        self.topbar.updateTopbar(
            categoryName,
            self.repoCache.getCategoryNumber(categoryName)
            )
        
        # Update application view.
        self.repoView.update(
            categoryName, 
            self.repoCache.getCategoryNumber(categoryName)
            )

        # Reset repoView's index.
        self.repoView.setSelectItemIndex(0)

class Topbar:
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
        self.categoryLabel = gtk.Label()
        self.numLabel = gtk.Label()
        self.updateTopbar(category, itemNum)
        self.entrySearchCallback = entrySearchCallback
        self.updateCategoryCallback = updateCategoryCallback
        
        # Add classify number.
        self.box.pack_start(self.categoryLabel, False, False, self.paddingX)
        self.box.pack_start(self.numLabel, False, False, self.paddingX)
        
        # Add sort buttons.
        self.sortBox = gtk.HBox()
        self.sortAlign = gtk.Alignment()
        self.sortAlign.set(0.5, 0.5, 1.0, 1.0)
        self.sortAlign.set_padding(0, 0, self.SORT_BOX_PADDING_X, self.SORT_BOX_PADDING_X)
        self.sortAlign.add(self.sortBox)
        
        self.sortRecommendId = "sortRecommend"
        self.sortDownloadId = "sortDownload"
        self.sortVoteId = "sortVote"
        self.sortType = self.sortRecommendId

        self.normalColor = '#1A3E88'
        self.hoverColor = '#0084FF'
        self.selectColor = '#000000'
        
        (self.sortRecommendLabel, self.sortRecommendEventBox) = utils.setDefaultToggleLabel(
            "按推荐排序", self.sortRecommendId, self.setSortType, self.getSortType, True)
        self.sortRecommendEventBox.connect("button-press-event", lambda w, e: self.updateCategoryCallback())
        
        (self.sortDownloadLabel, self.sortDownloadEventBox) = utils.setDefaultToggleLabel(
            "按下载排序", self.sortDownloadId, self.setSortType, self.getSortType, False)
        self.sortDownloadEventBox.connect("button-press-event", lambda w, e: self.updateCategoryCallback())

        (self.sortVoteLabel, self.sortVoteEventBox) = utils.setDefaultToggleLabel(
            "按评分排序", self.sortVoteId, self.setSortType, self.getSortType, False)
        self.sortVoteEventBox.connect("button-press-event", lambda w, e: self.updateCategoryCallback())
        
        self.sortButtonPaddingX = 5
        self.sortBox.pack_start(self.sortRecommendEventBox, False, False, self.sortButtonPaddingX)
        self.sortBox.pack_start(self.sortDownloadEventBox, False, False, self.sortButtonPaddingX)
        self.sortBox.pack_start(self.sortVoteEventBox, False, False, self.sortButtonPaddingX)
        self.box.pack_start(self.sortAlign, False, False)
        
        # Add search entry and label.
        (self.searchEntry, searchAlign, self.searchCompletion) = newSearchUI(
            "请输入你要搜索的软件名称、版本或其他信息",
            lambda text: utils.getCandidates(map (lambda appInfo: appInfo.pkg.name, appInfos), text),
            self.clickCandidate,
            self.search)
        self.box.pack_start(searchAlign)
        
    def setSortType(self, sType):
        '''Set sort type.'''
        self.sortType = sType
        
        if self.sortType == self.sortRecommendId:
            self.sortRecommendLabel.set_markup(
                "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "按推荐排序"))
            self.sortDownloadLabel.set_markup(
                "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "按下载排序"))
            self.sortVoteLabel.set_markup(
                "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "按评分排序"))
        elif self.sortType == self.sortDownloadId:
            self.sortRecommendLabel.set_markup(
                "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "按推荐排序"))
            self.sortDownloadLabel.set_markup(
                "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "按下载排序"))
            self.sortVoteLabel.set_markup(
                "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "按评分排序"))
        else:
            self.sortRecommendLabel.set_markup(
                "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "按推荐排序"))
            self.sortDownloadLabel.set_markup(
                "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "按下载排序"))
            self.sortVoteLabel.set_markup(
                "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "按评分排序"))
        
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
        
    def updateTopbar(self, category, itemNum):
        '''Set number label.'''
        self.categoryLabel.set_markup("<span foreground='#1A3E88' size='%s'><b>%s</b></span>" % (LABEL_FONT_SIZE, category))
        self.numLabel.set_markup(
            ("<span size='%s'>共</span>" % (LABEL_FONT_SIZE))
            + "<span foreground='#006efe' size='%s'> %s</span>" % (LABEL_FONT_SIZE, str(itemNum))
            + ("<span size='%s'> 款软件</span>" % (LABEL_FONT_SIZE)))
    

#  LocalWords:  categorybar repoView's sortAlign efe
