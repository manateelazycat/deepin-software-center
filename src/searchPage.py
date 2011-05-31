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
import appView
import gtk
import pango
import pygtk
import search
import searchCompletion as sc
import searchView
import utils
pygtk.require('2.0')

class SearchPage:
    '''Search page.'''
	
    def __init__(self, pageId, repoCache, keyword, pkgList, 
                 switchStatus, downloadQueue, 
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback, exitSearchPageCallback):
        '''Init for search page.'''
        # Init.
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
            fetchVoteCallback
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
            pkgList = search.do_search(keywords)
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
    
class Topbar:
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
        self.numLabel = gtk.Label()
        self.updateTopbar(keyword, itemNum)

        # Add search entry and label.
        (self.searchEntry, searchAlign, self.searchCompletion) = newSearchUI(
            "请输入你要搜索的软件名称、版本或其他信息",
            lambda text: utils.getCandidates(map (lambda appInfo: appInfo.pkg.name, appInfos), text),
            clickCandidateCallback,
            searchCallback)
        
        # Add return button.
        (returnButton, returnButtonAlign) = newActionButton(
            "search", 1.0, 0.5, "cell", False, "返回", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF",
            0, 10
            )
        returnButton.connect("button-release-event", lambda widget, event: exitSearchPageCallback(pageId))
        
        # Connect widgets.
        self.box.pack_start(self.keywordLabel, False, False, self.paddingX)
        self.box.pack_start(self.numLabel, False, False, self.paddingX)
        self.box.pack_start(searchAlign, True, True, self.paddingX)
        self.box.pack_start(returnButtonAlign, False, False)
        
    def updateTopbar(self, keyword, itemNum):
        '''Set number label.'''
        self.keywordLabel.set_markup(
            ("<span size='%s'>搜到和 </span>" % (LABEL_FONT_SIZE))
            + ("<span foreground='#00BBBB' size='%s'><b>%s</b></span>" % (LABEL_FONT_SIZE, keyword)))
        self.numLabel.set_markup(
            ("<span size='%s'>相关的软件共</span>" % (LABEL_FONT_SIZE))
            + "<span foreground='#00BB00' size='%s'>%s</span>" % (LABEL_FONT_SIZE, str(itemNum)) 
            + ("<span size='%s'>款</span>" % (LABEL_FONT_SIZE)))
    
