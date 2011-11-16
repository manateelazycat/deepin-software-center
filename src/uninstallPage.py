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
import gtk
import pygtk
import search
import searchCompletion as sc
import uninstallView
import utils
pygtk.require('2.0')

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
        self.numColor = '#006efe'
        self.textColor = '#1A3E88'
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
            "请输入您要卸载的软件名称、版本或其他信息",
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
            ("<span size='%s'>有 </span>" % (LABEL_FONT_SIZE))
            + ("<span foreground='%s' size='%s'>%s</span>" % (self.numColor, LABEL_FONT_SIZE, str(upgradeNum)))
            + ("<span size='%s'> 款软件可以直接卸载</span>" % (LABEL_FONT_SIZE)))

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
