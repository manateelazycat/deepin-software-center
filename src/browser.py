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

from constant import *
from ctypes import *
from lang import __
from utils import *
import gobject
import gtk
import os, webkit, webbrowser
import utils

libgobject = cdll.LoadLibrary('libgobject-2.0.so.0')
libwebkit = cdll.LoadLibrary('libwebkitgtk-1.0.so.0')
libsoup = cdll.LoadLibrary('libsoup-2.4.so.1')

class Browser(webkit.WebView):
    '''Browser.'''
	
    def __init__(self, uri):
        '''Init browser.'''
        # Init.
        webkit.WebView.__init__(self)
        
        try:
            # Init cookie.
            self.initCookie()
        
            # Init proxy.
            self.initProxy()

            # Load uri.
            self.load_uri(uri)
        except Exception, e:
            print "Got error when loading %s: %s" % (uri, e)
            
    def initCookie(self):
        '''Init cookie.'''
    	if not os.path.exists(COOKIE_FILE):
    		os.mknod(COOKIE_FILE)
    	session = libwebkit.webkit_get_default_session()
    	libgobject.g_object_set(session, 'add-feature', libsoup.soup_cookie_jar_text_new(COOKIE_FILE, False), None)
        
    def initProxy(self):
        '''Init proxy.'''
        proxyString = utils.parseProxyString()
        if proxyString != None:
            session = libwebkit.webkit_get_default_session()
            libgobject.g_object_set(session, 'proxy-uri', libsoup.soup_uri_new(proxyString), None)

