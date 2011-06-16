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
import gtk
import pygtk
import updateView
import utils
pygtk.require('2.0')

class UpdatePage:
    '''Interface for update page.'''
	
    def __init__(self, repoCache, switchStatus, downloadQueue, entryDetailCallback, 
                 sendVoteCallback, fetchVoteCallback):
        '''Init for update page.'''
        # Init.
        self.repoCache = repoCache
        self.box = gtk.VBox()
        self.topbar = Topbar(len(self.repoCache.upgradablePkgs))
        self.updateView = updateView.UpdateView(
            len(self.repoCache.upgradablePkgs), 
            self.repoCache.getUpgradableAppList,
            switchStatus, 
            downloadQueue,
            entryDetailCallback,
            sendVoteCallback,
            fetchVoteCallback
            )
        
        # Connect components.
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.pack_start(self.updateView.scrolledwindow)
        
        self.box.show_all()
        
class Topbar:
    '''Top bar.'''
	
    def __init__(self, upgradeNum):
        '''Init for top bar.'''
        # Init.
        self.paddingX = 5
        self.numColor = '#00BBBB'
        self.textColor = '#1A3E88'
        
        self.box = gtk.HBox()
        self.boxAlign = gtk.Alignment()
        self.boxAlign.set(0.0, 0.5, 1.0, 1.0)
        self.boxAlign.set_padding(0, 0, TOPBAR_PADDING_LEFT, TOPBAR_PADDING_UPDATE_RIGHT)
        self.boxAlign.add(self.box)
        self.eventbox = gtk.EventBox()
        drawTopbar(self.eventbox)
        
        upgradeBox = gtk.HBox()
        upgradeAlign = gtk.Alignment()
        upgradeAlign.set(1.0, 0.0, 0.0, 1.0)
        upgradeAlign.add(upgradeBox)
        
        self.numLabel = gtk.Label()
        self.selectAllLabel = gtk.Label()
        self.selectAllLabel.set_markup("<span foreground='%s' size='%s'>%s</span>" % (self.textColor, LABEL_FONT_SIZE, "全选"))
        upgradeBox.pack_start(self.selectAllLabel, False, False, self.paddingX)
        
        self.unselectAllLabel = gtk.Label()
        self.unselectAllLabel.set_markup("<span foreground='%s' size='%s'>%s</span>" % (self.textColor, LABEL_FONT_SIZE, "全不选"))
        upgradeBox.pack_start(self.unselectAllLabel, False, False, self.paddingX)
        
        (self.upgradeButton, upgradeButtonAlign) = newActionButton(
             "update_selected", 0.0, 0.5, "cell", True, "升级选中的软件", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF")
        upgradeBox.pack_start(upgradeButtonAlign, False, False, self.paddingX)
        
        # Connect.
        self.updateNum(upgradeNum)
        self.numLabel.set_alignment(0.0, 0.5)
        self.box.pack_start(self.numLabel, True, True, self.paddingX)
        self.box.pack_start(upgradeAlign, True, True, self.paddingX)
        self.eventbox.add(self.boxAlign)

    def updateNum(self, upgradeNum):
        '''Update number.'''
        self.numLabel.set_markup(
            ("<span size='%s'>有 </span>" % (LABEL_FONT_SIZE))
            + ("<span foreground='%s' size='%s'>%s</span>" % (self.numColor, LABEL_FONT_SIZE, str(upgradeNum)))
            + ("<span size='%s'> 个更新包可以升级</span>" % (LABEL_FONT_SIZE)))
                                 
    
