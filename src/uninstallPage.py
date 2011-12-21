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
import gtk
import search
import searchCompletion as sc
import uninstallView
import utils

class UninstallPage(object):
    '''Interface for uninstall page.'''
	
    def __init__(self, repoCache, searchQuery, actionQueue, entryDetailCallback, entrySearchCallback, 
                 sendVoteCallback, fetchVoteCallback, messageCallback):
        '''Init for uninstall page.'''
        # Init.
        self.repoCache = repoCache
        self.searchQuery = searchQuery
        self.box = gtk.VBox()
        self.topbar = Topbar(len(self.repoCache.uninstallablePkgs),
                             repoCache,
                             entrySearchCallback,
                             messageCallback,
                             searchQuery)
        self.uninstallView = uninstallView.UninstallView(
            len(self.repoCache.uninstallablePkgs), 
            self.repoCache.getUninstallableAppList,
            actionQueue,
            entryDetailCallback,
            sendVoteCallback,
            fetchVoteCallback,
            )
        
        # Connect components.
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.pack_start(self.uninstallView.scrolledwindow)
        self.box.show_all()

class Topbar(object):
    '''Top bar.'''
	
    SEARCH_ENTRY_WIDTH = 300
    
    def __init__(self, upgradeNum, repoCache, entrySearchCallback, messageCallback, searchQuery):
        '''Init for top bar.'''
        # Init.
        self.searchQuery = searchQuery
        self.paddingX = 5
        self.repoCache = repoCache
        self.messageCallback = messageCallback
        self.entrySearchCallback = entrySearchCallback
        
        self.box = gtk.HBox()
        self.boxAlign = gtk.Alignment()
        self.boxAlign.set(0.0, 0.5, 1.0, 1.0)
        self.boxAlign.set_padding(0, 0, TOPBAR_PADDING_LEFT, TOPBAR_PADDING_RIGHT)
        self.boxAlign.add(self.box)
        self.eventbox = gtk.EventBox()
        drawTopbar(self.eventbox)
        self.numLabel = gtk.Label()
        
        # Add search entry and label.
        (self.searchEntry, searchAlign, self.searchCompletion) = newSearchUI(
            __("Please enter the name you want to uninstall the software, version or other information"),
            lambda text: getCandidates(self.repoCache.uninstallablePkgs, text),
            self.clickCandidate,
            self.search)
        
        # Connect.
        self.updateNum(upgradeNum)
        self.numLabel.set_alignment(0.0, 0.5)
        self.box.pack_start(self.numLabel, True, True, self.paddingX)
        self.box.pack_start(searchAlign)
        self.eventbox.add(self.boxAlign)

    def updateNum(self, upgradeNum):
        '''Update number.'''
        self.numLabel.set_markup(
            __("Topbar UninstallPage") % (LABEL_FONT_SIZE, 
                                          appTheme.getDynamicColor("topbarNum").getColor(),
                                          LABEL_FONT_SIZE, 
                                          str(upgradeNum), 
                                          LABEL_FONT_SIZE))

    def search(self, editable):
        '''Search'''
        content = self.searchEntry.get_chars(0, -1)
        keywords = content.split()
        if len(keywords) != 0:
            pkgList = filter (lambda n: n in self.repoCache.uninstallablePkgs, self.searchQuery.query(keywords))
            if pkgList != []:
                self.entrySearchCallback(PAGE_UNINSTALL, content, pkgList)
        
    def clickCandidate(self, candidate):
        '''Click candidate.'''
        keyword = self.searchEntry.get_chars(0, -1)
        self.entrySearchCallback(PAGE_UNINSTALL, keyword, [candidate])

#  LocalWords:  efe
