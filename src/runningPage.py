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

from constant import *
from draw import *
import gtk
import pygtk
import utils
pygtk.require('2.0')

class RunningPage:
    '''Page for running process.'''
	
    def __init__(self):
        '''Init for running page.'''
        # Init.
        self.box = gtk.VBox()
        
        self.topbar = Topbar()
        
        # Connect components.
        self.box.pack_start(self.topbar.eventbox, False, False)
        self.box.show_all()
        
class Topbar:
    '''Top bar.'''
	
    def __init__(self):
        '''Init for top bar.'''
        # Init.
        self.eventbox = gtk.EventBox()
        drawTopbar(self.eventbox)
        self.box = gtk.HBox()
        self.boxAlign = gtk.Alignment()
        self.boxAlign.set(0.0, 0.5, 1.0, 1.0)
        self.boxAlign.set_padding(0, 0, TOPBAR_PADDING_LEFT, TOPBAR_PADDING_RIGHT)
        self.boxAlign.add(self.box)
        self.eventbox.add(self.boxAlign)
        self.normalColor = '#1A3E88'
        self.hoverColor = '#0084FF'
        self.selectColor = '#000000'
        self.statusInstalling = "statusInstalling"
        self.statusUpdating = "statusUpdating"
        self.statusUninstalling = "statusUninstalling"
        self.status = self.statusInstalling
        
        # Add status switch buttons.
        self.statusPaddingX = 5
        self.statusBox = gtk.HBox()
        self.statusBoxAlign = gtk.Alignment()
        self.statusBoxAlign.set(0.0, 0.0, 1.0, 1.0)
        self.statusBoxAlign.add(self.statusBox)
        self.box.pack_start(self.statusBoxAlign)
        
        self.installingLabel = gtk.Label()
        self.installingEventBox = gtk.EventBox()
        utils.setToggleLabel(
            self.installingEventBox,
            self.installingLabel,
            "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "正在安装"),
            "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在安装"),
            "<span foreground='%s' size='%s' >%s</span>" % (self.hoverColor, LABEL_FONT_SIZE, "正在安装"),
            "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "正在安装"),
            self.statusInstalling,
            self.setStatus,
            self.getStatus
            )
        self.statusBox.pack_start(self.installingEventBox, False, False, self.statusPaddingX)

        self.updatingLabel = gtk.Label()
        self.updatingEventBox = gtk.EventBox()
        utils.setToggleLabel(
            self.updatingEventBox,
            self.updatingLabel,
            "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在升级"),
            "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在升级"),
            "<span foreground='%s' size='%s' >%s</span>" % (self.hoverColor, LABEL_FONT_SIZE, "正在升级"),
            "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "正在升级"),
            self.statusUpdating,
            self.setStatus,
            self.getStatus
            )
        self.statusBox.pack_start(self.updatingEventBox, False, False, self.statusPaddingX)

        self.uninstallingLabel = gtk.Label()
        self.uninstallingEventBox = gtk.EventBox()
        utils.setToggleLabel(
            self.uninstallingEventBox,
            self.uninstallingLabel,
            "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在卸载"),
            "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在卸载"),
            "<span foreground='%s' size='%s' >%s</span>" % (self.hoverColor, LABEL_FONT_SIZE, "正在卸载"),
            "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "正在卸载"),
            self.statusUninstalling,
            self.setStatus,
            self.getStatus
            )
        self.statusBox.pack_start(self.uninstallingEventBox, False, False, self.statusPaddingX)
        
        # Add download directory button.
        self.openDirectoryLabel = gtk.Label()
        self.openDirectoryLabel.set_markup(
            "<span foreground='%s' size='%s'>%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "打开下载目录"))
        self.openDirectoryEventBox = gtk.EventBox()
        self.openDirectoryEventBox.set_visible_window(False)
        self.openDirectoryEventBox.add(self.openDirectoryLabel)
        self.openDirectoryEventBox.connect("button-press-event", lambda w, e: utils.runCommand("xdg-open /var/cache/apt/archives"))
        utils.setClickableLabel(
            self.openDirectoryEventBox,
            self.openDirectoryLabel,
            "<span foreground='%s' size='%s'>%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "打开下载目录"),
            "<span foreground='%s' size='%s'>%s</span>" % (self.hoverColor, LABEL_FONT_SIZE, "打开下载目录"),
            True
            )
        self.box.pack_start(self.openDirectoryEventBox, False, False)

    def setStatus(self, status):
        '''Set status.'''
        self.status = status
        
        if self.status == self.statusInstalling:
           self.installingLabel.set_markup(
               "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "正在安装"),
               )
           self.updatingLabel.set_markup(
               "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在升级"),
               )
           self.uninstallingLabel.set_markup(
               "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在卸载"),
               )
        elif self.status == self.statusUpdating:
           self.installingLabel.set_markup(
               "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在安装"),
               )
           self.updatingLabel.set_markup(
               "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "正在升级"),
               )
           self.uninstallingLabel.set_markup(
               "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在卸载"),
               )
        else:
           self.installingLabel.set_markup(
               "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在安装"),
               )
           self.updatingLabel.set_markup(
               "<span foreground='%s' size='%s' >%s</span>" % (self.normalColor, LABEL_FONT_SIZE, "正在升级"),
               )
           self.uninstallingLabel.set_markup(
               "<span foreground='%s' size='%s' underline='single'>%s</span>" % (self.selectColor, LABEL_FONT_SIZE, "正在卸载"),
               )
        
    def getStatus(self):
        '''Get status.'''
        return self.status
