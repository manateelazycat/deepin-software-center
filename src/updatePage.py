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
import gtk
import updateView
import utils

class UpdatePage(object):
    '''Interface for update page.'''
	
    def __init__(self, repoCache, switchStatus, downloadQueue, entryDetailCallback, 
                 sendVoteCallback, fetchVoteCallback, upgradeSelectedPkgsCallback,
                 addIgnorePkgCallback, showIgnorePageCallback):
        '''Init for update page.'''
        # Init.
        self.repoCache = repoCache
        self.box = gtk.VBox()
        self.updateView = updateView.UpdateView(
            repoCache,
            switchStatus, 
            downloadQueue,
            entryDetailCallback,
            sendVoteCallback,
            fetchVoteCallback,
            addIgnorePkgCallback,
            )
        self.topbar = Topbar(self.repoCache,
                             self.updateView.selectAllPkg,
                             self.updateView.unselectAllPkg,
                             self.updateView.getSelectList,
                             upgradeSelectedPkgsCallback,
                             showIgnorePageCallback)
        
        # Connect components.
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.pack_start(self.updateView.scrolledwindow)
        
        self.box.show_all()
        
class Topbar(object):
    '''Top bar.'''
	
    def __init__(self, repoCache, 
                 selectAllPkgCallback, unselectAllPkgCallback, 
                 getSelectListCallback, upgradeSelectedPkgsCallback,
                 showIgnorePageCallback):
        '''Init for top bar.'''
        # Init.
        self.repoCache = repoCache
        self.paddingX = 5
        self.selectAllPkgCallback = selectAllPkgCallback
        self.unselectAllPkgCallback = unselectAllPkgCallback
        self.showIgnorePageCallback = showIgnorePageCallback
        
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
        
        self.ignoreNumBox = gtk.HBox()
        self.ignoreNumAlign = gtk.Alignment()
        self.ignoreNumAlign.set(0.0, 0.5, 0.0, 0.0)
        self.ignoreNumAlign.add(self.ignoreNumBox)
        
        self.selectAllId = "selectAll"
        self.unselectAllId = "unselectAll"
        self.labelId = self.selectAllId
        
        (self.selectAllBox, self.selectAllEventBox) = setDefaultRadioButton(
            __("Select All"), self.selectAllId, self.setLabelId, self.getLabelId, self.selectAllPkgStatus
            )
        upgradeBox.pack_start(self.selectAllBox, False, False, self.paddingX)
        
        (self.unselectAllBox, self.unselectAllEventBox) = setDefaultRadioButton(
            __("Unselect All"), self.unselectAllId, self.setLabelId, self.getLabelId, self.unselectAllPkgStatus
            )
        upgradeBox.pack_start(self.unselectAllBox, False, False, self.paddingX)
        
        (self.upgradeButton, upgradeButtonAlign) = newActionButton(
             "search", 0.0, 0.5, "cell", False, __("Action Update"), BUTTON_FONT_SIZE_MEDIUM, "bigButtonFont")
        upgradeBox.pack_start(upgradeButtonAlign, False, False, 26)
        self.upgradeButton.connect("button-press-event", lambda w, e: upgradeSelectedPkgsCallback(getSelectListCallback()))
        
        # Connect.
        self.updateNum(self.repoCache.getUpgradableNum())
        self.numLabel.set_alignment(0.0, 0.5)
        self.box.pack_start(self.numLabel, False, False, self.paddingX)
        self.box.pack_start(self.ignoreNumAlign, True, True, self.paddingX)
        self.box.pack_start(upgradeAlign, True, True, self.paddingX)
        self.eventbox.add(self.boxAlign)
        
        self.updateIgnoreNum(self.repoCache.getIgnoreNum())
        
    def selectAllPkgStatus(self):
        '''Select all pkg status.'''
        self.selectAllEventBox.queue_draw()
        self.unselectAllEventBox.queue_draw()
    
        self.selectAllPkgCallback()

    def unselectAllPkgStatus(self):
        '''Select all pkg status.'''
        self.selectAllEventBox.queue_draw()
        self.unselectAllEventBox.queue_draw()
    
        self.unselectAllPkgCallback()
        
    def setLabelId(self, lId):
        '''Set label id.'''
        self.labelId = lId
        
    def getLabelId(self):
        '''Get label id.'''
        return self.labelId
    
    def updateIgnoreNum(self, ignoreNum):
        '''Update ignore number label.'''
        utils.containerRemoveAll(self.ignoreNumBox)
        
        if ignoreNum > 0:
            (ignoreLabel, ignoreEventBox) = setDefaultClickableDynamicLabel(
                __("No Notify UpdatePage") % (ignoreNum),
                "topbarButton",
                )
            ignoreEventBox.connect("button-press-event", lambda w, e: self.showIgnorePageCallback())
            self.ignoreNumBox.add(ignoreEventBox)
            self.ignoreNumBox.show_all()

    def updateNum(self, upgradeNum):
        '''Update number.'''
        if upgradeNum == 0:
            markup = ""
        else:
            markup = (__("Topbar UpdatePage") % (LABEL_FONT_SIZE, 
                                                 appTheme.getDynamicColor("topbarNum").getColor(),
                                                 LABEL_FONT_SIZE, 
                                                 str(upgradeNum), 
                                                 LABEL_FONT_SIZE))
        self.numLabel.set_markup(markup)

#  LocalWords:  efe
