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
    
    def __init__(self, repoCache, switchStatus, downloadQueue, entryDetailCallback, 
                 entrySearchCallback, sendVoteCallback, fetchVoteCallback):
        '''Init for repository page.'''
        # Init.
        self.repoCache = repoCache
        self.box = gtk.VBox()
        self.categorybar = categorybar.CategoryBar(self.repoCache.getCategorys(), self.selectCategory)
        self.contentBox = gtk.HBox()
        self.topbar = Topbar(
            CLASSIFY_WEB, 
            self.repoCache.getCategoryNumber(CLASSIFY_WEB),
            self.repoCache.cache.values(),
            entrySearchCallback)
        self.repoView = repoView.RepoView(
            CLASSIFY_WEB, 
            self.repoCache.getCategoryNumber(CLASSIFY_WEB),
            self.repoCache.getAppList,
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

    def selectCategory(self, category, categoryId):
        '''Select category.'''
        self.categorybar.categoryId = categoryId
        self.categorybar.box.queue_draw()
        
        # Redraw sub-categorybar bar.
        self.topbar.updateTopbar(
            category,
            self.repoCache.getCategoryNumber(category)
            )
        
        # Update application view.
        self.repoView.update(
            category, 
            self.repoCache.getCategoryNumber(category)
            )

        # Reset repoView's index.
        self.repoView.setSelectItemIndex(0)

class Topbar:
    '''Top bar.'''
	
    SEARCH_ENTRY_WIDTH = 300
    
    def __init__(self, category, itemNum, appInfos, entrySearchCallback):
        '''Init for top bar.'''
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

        # Add search entry and label.
        (self.searchEntry, searchAlign, self.searchCompletion) = newSearchUI(
            "请输入你要搜索的软件名称、版本或其他信息",
            lambda text: utils.getCandidates(map (lambda appInfo: appInfo.pkg.name, appInfos), text),
            self.clickCandidate,
            self.search)
        
        # Connect widgets.
        self.box.pack_start(self.categoryLabel, False, False, self.paddingX)
        self.box.pack_start(self.numLabel, False, False, self.paddingX)
        # self.box.pack_start(sortAlign, True, True, self.paddingX)
        self.box.pack_start(searchAlign)
        
    def search(self, editable):
        '''Search'''
        content = self.searchEntry.get_chars(0, -1)
        keywords = content.split()
        if len(keywords) != 0:
            pkgList = search.do_search(keywords)
            self.entrySearchCallback(PAGE_REPO, content, pkgList)
        
    def clickCandidate(self, candidate):
        '''Click candidate.'''
        keyword = self.searchEntry.get_chars(0, -1)
        self.entrySearchCallback(PAGE_REPO, keyword, [candidate])
        
    def updateTopbar(self, category, itemNum):
        '''Set number label.'''
        self.categoryLabel.set_markup("<span foreground='#00BBBB' size='%s'><b>%s</b></span>" % (LABEL_FONT_SIZE, category))
        self.numLabel.set_markup(
            ("<span size='%s'>共</span>" % (LABEL_FONT_SIZE))
            + "<span foreground='#00BB00' size='%s'> %s</span>" % (LABEL_FONT_SIZE, str(itemNum))
            + ("<span size='%s'> 款软件</span>" % (LABEL_FONT_SIZE)))
    
