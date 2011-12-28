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
from draw import *
from lang import __, getDefaultLanguage
import appView
import gtk
import pango
import search
import searchCompletion as sc
import searchView
import utils

class SearchPage(object):
    '''Search page.'''
	
    def __init__(self, searchQuery, pageId, repoCache, keyword, pkgList, 
                 switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback, exitSearchPageCallback,
                 launchApplicationCallback):
        '''Init for search page.'''
        # Init.
        self.searchQuery = searchQuery
        self.repoCache = repoCache
        self.pkgList = pkgList
        
        self.box = gtk.VBox()
        self.topbar = Topbar(pageId,
                             keyword,
                             len(pkgList),
                             self.repoCache.cache.values(),
                             exitSearchPageCallback,
                             self.search,
                             self.clickCandidate)
        self.searchView = searchView.SearchView(
            len(pkgList),
            self.getSearchAppList,
            switchStatus,
            downloadQueue,
            entryDetailCallback,
            sendVoteCallback,
            fetchVoteCallback,
            launchApplicationCallback
            )
        
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.pack_start(self.searchView.scrolledwindow)
        
        # Connect components.
        self.box.show_all()
        
    def getSearchAppList(self, startIndex, endIndex):
        '''Get search application list.'''
        return (map (lambda i: self.repoCache.cache[self.pkgList[i]], range(startIndex, endIndex)))
    
    def search(self, editable):
        '''Search'''
        content = editable.get_chars(0, -1)
        keywords = content.split()
        if len(keywords) != 0:
            pkgList = self.searchQuery.query(keywords)
            if pkgList != []:
                self.pkgList = pkgList
                self.topbar.searchCompletion.hide()
                self.topbar.updateTopbar(content, len(pkgList))
                self.searchView.updateSearch(len(pkgList))
            
    def clickCandidate(self, candidate):
        '''Click candidate.'''
        self.pkgList = [candidate]
        self.topbar.searchCompletion.hide()
        self.topbar.updateTopbar(candidate, len(self.pkgList))
        self.searchView.updateSearch(len(self.pkgList))
    
class Topbar(object):
    '''Top bar.'''
	
    SEARCH_ENTRY_WIDTH = 300
    
    def __init__(self, pageId, keyword, itemNum, appInfos, 
                 exitSearchPageCallback, searchCallback, clickCandidateCallback):
        '''Init for top bar.'''
        self.paddingX = 5
        self.box = gtk.HBox()
        self.boxAlign = gtk.Alignment()
        self.boxAlign.set(0.0, 0.5, 1.0, 1.0)
        if itemNum > 20:
            paddingRight = TOPBAR_SEARCH_RIGHT
        else:
            paddingRight = TOPBAR_SEARCH_ADJUST_RIGHT
        self.boxAlign.set_padding(0, 0, TOPBAR_PADDING_LEFT, paddingRight)
        self.boxAlign.add(self.box)
        self.eventbox = gtk.EventBox()
        drawTopbar(self.eventbox)
        self.eventbox.add(self.boxAlign)
        self.keywordLabel = gtk.Label()
        self.updateTopbar(keyword, itemNum)

        # Add search entry and label.
        (self.searchEntry, searchAlign, self.searchCompletion) = newSearchUI(
            __("Please enter the name you want to search for software, version or other information"),
            lambda text: getCandidates(map (lambda appInfo: appInfo.pkg.name, appInfos), text),
            clickCandidateCallback,
            searchCallback)
        
        # Add return button.
        (returnButton, returnButtonAlign) = newActionButton(
            "search", 1.0, 0.5, "cell", False, __("Return"), BUTTON_FONT_SIZE_MEDIUM, "bigButtonFont",
            0, 10
            )
        returnButton.connect("button-release-event", lambda widget, event: exitSearchPageCallback(pageId))
        
        # Connect widgets.
        self.box.pack_start(self.keywordLabel, False, False)
        self.box.pack_start(searchAlign, True, True, self.paddingX)
        self.box.pack_start(returnButtonAlign, False, False)
        
    def updateTopbar(self, keyword, itemNum):
        '''Set number label.'''
        
        self.keywordLabel.set_markup(
            __("Topbar SearchPage") % (LABEL_FONT_SIZE, 
                                       appTheme.getDynamicColor("topbarKeyword").getColor(),
                                       LABEL_FONT_SIZE, 
                                       keyword.strip(), 
                                       LABEL_FONT_SIZE, 
                                       appTheme.getDynamicColor("topbarNum").getColor(),
                                       LABEL_FONT_SIZE, 
                                       str(itemNum), 
                                       LABEL_FONT_SIZE))
    

#  LocalWords:  BBBB
