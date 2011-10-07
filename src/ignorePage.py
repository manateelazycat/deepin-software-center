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
import utils
import ignoreView
pygtk.require('2.0')

class IgnorePage:
    '''Ignore page.'''
	
    def __init__(self, repoCache, 
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback,
                 removeIgnorePkgsCallback, exitIgnorePageCallback):
        '''Init for ignore page.'''
        # Init.
        self.repoCache = repoCache
        self.box = gtk.VBox()
        
        self.ignoreView = ignoreView.IgnoreView(
            repoCache,
            entryDetailCallback,
            sendVoteCallback,
            fetchVoteCallback,
            removeIgnorePkgsCallback,
            )        
        self.topbar = Topbar(repoCache,
                             self.ignoreView.selectAllPkg,
                             self.ignoreView.unselectAllPkg,
                             self.ignoreView.getSelectList,
                             removeIgnorePkgsCallback,
                             exitIgnorePageCallback)
        
        # Connect components.
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.pack_start(self.ignoreView.scrolledwindow)
        self.box.show_all()

class Topbar:
    '''Top bar.'''
	
    def __init__(self, repoCache, 
                 selectAllPkgCallback, unselectAllPkgCallback, 
                 getSelectListCallback,
                 removeIgnorePkgsCallback,
                 exitIgnorePageCallback):
        '''Init for top bar.'''
        # Init.
        self.repoCache = repoCache
        self.paddingX = 5
        self.numColor = '#006efe'
        self.normalColor = '#1A3E88'
        self.hoverColor = '#0084FF'
        self.selectColor = '#000000'
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
        
        self.selectAllId = "selectAll"
        self.unselectAllId = "unselectAll"
        self.labelId = self.selectAllId
        
        (self.selectAllLabel, self.selectAllEventBox) = utils.setDefaultToggleLabel(
            "全选", self.selectAllId, self.setLabelId, self.getLabelId, True)
        self.selectAllEventBox.connect("button-press-event", lambda w, e: selectAllPkgCallback())
        upgradeBox.pack_start(self.selectAllEventBox, False, False, self.paddingX)
        
        (self.unselectAllLabel, self.unselectAllEventBox) = utils.setDefaultToggleLabel(
            "全不选", self.unselectAllId, self.setLabelId, self.getLabelId, False)
        self.unselectAllEventBox.connect("button-press-event", lambda w, e: unselectAllPkgCallback())
        upgradeBox.pack_start(self.unselectAllEventBox, False, False, self.paddingX)
        
        (self.upgradeButton, upgradeButtonAlign) = newActionButton(
             "update_selected", 0.0, 0.5, "cell", True, "提示选中的软件", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF")
        upgradeBox.pack_start(upgradeButtonAlign, False, False, self.paddingX)
        self.upgradeButton.connect("button-press-event", lambda w, e: removeIgnorePkgsCallback(getSelectListCallback()))
        
        # Add return button.
        (returnButton, returnButtonAlign) = newActionButton(
            "search", 1.0, 0.5, "cell", False, "返回", BUTTON_FONT_SIZE_MEDIUM, "#FFFFFF",
            0, 10)
        returnButton.connect("button-release-event", lambda w, e: exitIgnorePageCallback())
        
        self.updateNum(self.repoCache.getIgnoreNum())
        self.numLabel.set_alignment(0.0, 0.5)
        self.box.pack_start(self.numLabel, False, False)
        self.box.pack_start(upgradeAlign, True, True)
        self.box.pack_start(returnButtonAlign, False, False)
        self.eventbox.add(self.boxAlign)
        
    def setLabelId(self, lId):
        '''Set label id.'''
        self.labelId = lId
        
        if self.labelId == self.selectAllId:
            self.selectAllLabel.set_markup(
                "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "全选"))
            self.unselectAllLabel.set_markup(
                "<span foreground='%s' size='%s'>%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "全不选"))
        else:
            self.selectAllLabel.set_markup(
                "<span foreground='%s' size='%s'>%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "全选"))
            self.unselectAllLabel.set_markup(
                "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "全不选"))
        
    def getLabelId(self):
        '''Get label id.'''
        return self.labelId
    
    def updateNum(self, upgradeNum):
        '''Update number.'''
        self.numLabel.set_markup(
            ("<span size='%s'>有 </span>" % (LABEL_FONT_SIZE))
            + ("<span foreground='%s' size='%s'>%s</span>" % (self.numColor, LABEL_FONT_SIZE, str(upgradeNum)))
            + ("<span size='%s'> 款软件不再提醒升级</span>" % (LABEL_FONT_SIZE)))

