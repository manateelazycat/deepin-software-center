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

from draw import *
import appView
import gtk
import pango
import pygtk
import utils
pygtk.require('2.0')

class SearchCompletion:
    '''Search completion.'''
    
    MARKUP_COLUMN = 0
    TEXT_COLUMN = 1
    CELL_HEIGHT = 20
    FONT_SIZE = 10
    MAX_CELL_NUMBER = 10
	
    def __init__(self, entry,
                 getCandidatesCallback,
                 clickCandidateCallback):
        '''Init for search completion.'''
        self.entry = entry
        self.getCandidatesCallback = getCandidatesCallback
        self.clickCandidateCallback = clickCandidateCallback
        self.showCompletion = True
        self.propagateLock = False
        
        self.window = gtk.Window()
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.set_decorated(False)
        self.window.set_resizable(True)
        self.window.set_transient_for(entry.get_window())
        self.window.set_property("accept-focus", False)
        self.window.set_opacity(0.9)
        self.listStore = gtk.ListStore(str, str)
        self.treeView = gtk.TreeView(self.listStore)
        self.treeView.set_headers_visible(False)
        self.cell = gtk.CellRendererText()
        self.cell.set_property("size-points", self.FONT_SIZE)
        self.cell.set_fixed_size(-1, self.CELL_HEIGHT)
        self.treeViewColumn = gtk.TreeViewColumn(None, self.cell, markup=self.MARKUP_COLUMN)
        self.treeViewColumn.set_sort_column_id(self.MARKUP_COLUMN)
        self.treeView.append_column(self.treeViewColumn)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_property("shadow-type", gtk.SHADOW_NONE)
        self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.frame = gtk.Frame()
        
        self.treeView.connect("row-activated", self.click)
        self.entry.connect("focus-out-event", lambda w, e: self.hide())
        self.entry.connect("size-allocate", lambda widget, allocation: self.hide())
        self.entry.connect("changed", self.show)
        self.entry.connect("key-press-event", lambda w, e: self.handleKeyPress(w, e))
        
        self.scrolledwindow.add(self.treeView)
        self.frame.add(self.scrolledwindow)
        self.window.add(self.frame)
        
    def show(self, editable):
        '''Show search completion.'''
        if self.showCompletion:
            # Move window to match entry's position.
            (wx, wy) = editable.window.get_origin()
            rect = editable.get_allocation()
            
            text = editable.get_chars(0, -1)
            candidates = self.getCandidatesCallback(text)
            if len(candidates) != 0:
                self.listStore.clear()
                for candidate in candidates:
                    self.listStore.append(candidate)
                    
                # Scroll to top first.
                utils.scrollToTop(self.scrolledwindow)
                
                w, h = rect.width, (min (len(candidates), self.MAX_CELL_NUMBER)) * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
                # FIXME, i don't know why entry'height is bigger than i need, so i decrease 8 pixel here.
                self.window.move(wx, wy + rect.height - 12)
                self.window.set_size_request(w, h)
                self.window.resize(w, h)
                self.window.show_all()    

                # Focus first candidate.
                self.treeView.set_cursor((0))
                gtk.Widget.grab_focus(self.treeView)
            else:
                self.window.hide_all()
                
    def handleKeyPress(self, entry, keyPressEvent):
        '''Handle key press.'''
        if not self.propagateLock:
            self.propagateLock = True
            eventName = gtk.gdk.keyval_name(keyPressEvent.keyval)
            if eventName == "Home":
                utils.treeViewFocusFirstToplevelNode(self.treeView)
            elif eventName == "End":
                utils.treeViewFocusLastToplevelNode(self.treeView)
            elif eventName == "Up":
                utils.treeViewFocusPrevToplevelNode(self.treeView)
            elif eventName == "Down":
                utils.treeViewFocusNextToplevelNode(self.treeView)
            elif eventName == "Return":
                selectedPath = utils.treeViewGetSelectedPath(self.treeView)
                self.click(self.treeView, selectedPath, None)
            else:
                self.entry.event(keyPressEvent)
            self.propagateLock = False
        
            return True
        else:
            return False
        
    def hide(self):
        '''Hide search completion.'''
        self.window.hide_all()
    
    def click(self, treeView, path, _):
        '''Click search completion.'''
        pathIter = self.listStore.get_iter(path)
        candidate = self.listStore.get_value(pathIter, self.TEXT_COLUMN)
        
        self.window.hide_all()
        self.showCompletion = False
        self.entry.set_text(candidate)
        self.showCompletion = True
        self.clickCandidateCallback(candidate)
        
