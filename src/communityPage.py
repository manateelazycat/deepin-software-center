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

import gtk
import pygtk
import webkit
pygtk.require('2.0')

class CommunityPage:
    '''Interface for community page.'''
	
    def __init__(self):
        '''Init for community page.'''
        # Init.
        self.box = gtk.VBox()
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_shadow_type(gtk.SHADOW_NONE)
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        # Open linux deepin bbs.
        self.view = webkit.WebView()
        self.view.open("http://www.linuxdeepin.com/forum/recent")
        
        # Make all link open in current window.
        self.view.connect("create-web-view", self.createWebViewCallback)
        
        # Connect components.
        self.scrolledwindow.add(self.view)
        self.box.add(self.scrolledwindow)
        self.box.show_all()

    def createWebViewCallback(self, webView, webFrame):
        '''Call back for signal `create-web-view`.'''
        self.view.load_uri(webFrame.get_uri())
        return self.view
        
    
