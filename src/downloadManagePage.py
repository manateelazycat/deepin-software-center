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
import gtk
import pygtk
import downloadManageView
pygtk.require('2.0')

class DownloadManagePage(object):
    '''Interface for download page.'''
	
    def __init__(self, repoCache, getRunningNum, getRunningList, switchStatus, downloadQueue,
                 entryDetailCallback, sendVoteCallback, fetchVoteCallback, cleanDownloadCacheCallback):
        '''Init for download page.'''
        # Init.
        self.box = gtk.VBox()
        
        appNum = getRunningNum()
        self.topbar = Topbar(appNum, cleanDownloadCacheCallback)
        
        self.downloadManageView = downloadManageView.DownloadManageView(
            repoCache,
            getRunningNum,
            getRunningList,
            switchStatus,
            downloadQueue,
            entryDetailCallback,
            sendVoteCallback,
            fetchVoteCallback,
            )
        
        # Connect components.
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.pack_start(self.downloadManageView.scrolledwindow)
        self.box.show_all()

class Topbar(object):
    '''Top bar.'''
	
    def __init__(self, itemNum, cleanDownloadCacheCallback):
        '''Init for top bar.'''
        # Init.
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
        
        self.numLabel = gtk.Label()
        
        (self.openDirLabel, self.openDirEventBox) = setDefaultClickableDynamicLabel(
            "打开下载目录",
            "topbarButton",
            )
        self.openDirAlign = gtk.Alignment()
        self.openDirAlign.set(0.0, 0.5, 0.0, 0.0)
        self.openDirAlign.add(self.openDirEventBox)
        self.openDirEventBox.connect("button-press-event", lambda w, e: utils.runCommand("xdg-open /var/cache/apt/archives/"))
        
        (self.cleanLabel, self.cleanEventBox) = setDefaultClickableDynamicLabel(
            "智能清理下载缓存",
            "topbarButton",
            )
        self.cleanEventBox.connect("button-press-event", lambda w, e: cleanDownloadCacheCallback())
        self.cleanAlign = gtk.Alignment()
        self.cleanAlign.set(1.0, 0.5, 0.0, 0.0)
        self.cleanAlign.add(self.cleanEventBox)
        utils.setHelpTooltip(self.cleanEventBox, "清理下载缓存， 节省您的硬盘空间！")
        
        # Connect.
        self.updateNum(itemNum)
        self.numLabel.set_alignment(0.0, 0.5)
        self.box.pack_start(self.numLabel, False, False, self.paddingX)
        self.box.pack_start(self.openDirAlign, True, True, self.paddingX)
        self.box.pack_start(self.cleanAlign, True, True, self.paddingX)
        self.eventbox.add(self.boxAlign)
        
    def updateNum(self, upgradeNum):
        '''Update number.'''
        # Don't show label when nothing to download.
        if upgradeNum == 0:
            markup = ""
        else:
            markup = ("<span size='%s'>有 </span>" % (LABEL_FONT_SIZE)) + ("<span foreground='%s' size='%s'>%s</span>" % (self.numColor, LABEL_FONT_SIZE, str(upgradeNum))) + ("<span size='%s'> 个包正在下载</span>" % (LABEL_FONT_SIZE))
                   
        self.numLabel.set_markup(markup)
