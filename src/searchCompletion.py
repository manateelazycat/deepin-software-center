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

from draw import *
from lang import __, getDefaultLanguage
from utils import *
import appView
import glib
import gtk
import pango
import time
import utils

class SearchCompletion(object):
    '''Search completion.'''
    
    MARKUP_COLUMN = 0
    TEXT_COLUMN = 1
    CELL_HEIGHT = 22
    SINGLE_CELL_HEIGHT = 28
    FONT_SIZE = 10
    MAX_CELL_NUMBER = 10
    INPUT_DELAY = 200           # in millisecond 
    WAIT_SEARCH_DELAY = 500     # in millisecond
	
    def __init__(self, entry,
                 getCandidatesCallback,
                 searchCallback,
                 clickCandidateCallback):
        '''Init for search completion.'''
        self.entry = entry
        self.getCandidatesCallback = getCandidatesCallback
        self.searchCallback = searchCallback
        self.clickCandidateCallback = clickCandidateCallback
        self.showCompletion = True
        self.propagateLock = False
        self.lastChangeTimestamp = 0
        self.searchEventId = None
        
        self.window = gtk.Window()
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.set_decorated(False)
        self.window.set_resizable(True)
        self.window.set_transient_for(entry.get_window())
        self.window.set_property("accept-focus", False)
        self.window.set_opacity(0.9)
        self.listStore = gtk.ListStore(str, str)
        self.scrolledwindow = gtk.ScrolledWindow()
        dTreeView = DynamicTreeView(
            self.scrolledwindow,
            self.listStore,
            appTheme.getDynamicColor("completionBackground"),
            appTheme.getDynamicColor("completionSelect"),
            )
        self.treeView = dTreeView.treeView
        self.treeView.set_headers_visible(False)
        self.cell = gtk.CellRendererText()
        self.cell.set_property("size-points", self.FONT_SIZE)
        self.cell.set_fixed_size(-1, self.CELL_HEIGHT)
        self.treeViewColumn = gtk.TreeViewColumn(None, self.cell, markup=self.MARKUP_COLUMN)
        self.treeViewColumn.set_sort_column_id(self.MARKUP_COLUMN)
        self.treeView.append_column(self.treeViewColumn)
        self.scrolledwindow.set_property("shadow-type", gtk.SHADOW_NONE)
        self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        drawVScrollbar(self.scrolledwindow)
        self.frame = gtk.Frame()
        
        self.treeView.connect("row-activated", self.click)
        self.treeView.connect("button-press-event", self.clickCandiate)
        self.entry.connect("focus-out-event", lambda w, e: self.hide())
        self.entry.connect("size-allocate", lambda widget, allocation: self.hide())
        self.entry.connect("changed", lambda w: self.show())
        self.entry.connect("key-press-event", lambda w, e: self.handleKeyPress(w, e))
        
        self.scrolledwindow.add(self.treeView)
        self.frame.add(self.scrolledwindow)
        self.window.add(self.frame)
        
    def show(self):
        '''Show search completion.'''
        # Remove search delay event if searchEventId not None.
        if self.searchEventId != None:
            glib.source_remove(self.searchEventId)
            self.searchEventId = None
        
        if self.showCompletion:
            # Search time bound: 80ms ~ 500ms, most time under INPUT_DELAY.
            # So user won't feeling *delay* if input delay more than INPUT_DELAY.
            # Input delay bound: 50ms ~ 200ms
            currentTime = time.time()
            delay = (currentTime - self.lastChangeTimestamp) * 1000
            
            if delay > self.INPUT_DELAY:
                # Record last change time stamp.
                self.lastChangeTimestamp = currentTime
                
                # Show completion.
                self.showCompletionWindow()
            else:
                # Add delay search if input delay less than INPUT_DELAY.
                # This step to avoid last input character input too fast that can't show completion correctly.
                if self.searchEventId == None:
                    self.searchEventId = glib.timeout_add(self.WAIT_SEARCH_DELAY, self.showCompletionWindow)
                
                self.window.hide_all()
        else:
            self.window.hide_all()
            
    def showCompletionWindow(self):
        '''Show completion.'''
        # Move window to match entry's position.
        (wx, wy) = self.entry.window.get_origin()
        rect = self.entry.get_allocation()
        
        text = self.entry.get_chars(0, -1)
        candidates = self.getCandidatesCallback(text)
        self.listStore.clear()
        
        content = self.entry.get_chars(0, -1)
        textColor = appTheme.getDynamicColor("completionText").getColor()
        keywordColor = appTheme.getDynamicColor("completionKeyword").getColor()
        self.listStore.append(
            ["<span foreground='%s'>%s</span>" % (textColor, __("Global Search")) + " <span foreground='%s'>%s</span>" % (keywordColor, content), content])
            
        for candidate in candidates:
            self.listStore.append(candidate)
            
        # Scroll to top first.
        utils.scrollToTop(self.scrolledwindow)
        
        if len(candidates) == 0:
            w, h = rect.width, self.SINGLE_CELL_HEIGHT
        else:
            w, h = rect.width, (min (len(candidates) + 1, self.MAX_CELL_NUMBER)) * (self.CELL_HEIGHT + 2)
        # FIXME, i don't know why entry'height is bigger than i need, so i decrease 8 pixel here.
        self.window.move(wx, wy + rect.height - 8)
        self.window.set_size_request(w, h)
        self.window.resize(w, h)
        self.window.show_all()    
        
        # Focus first candidate.
        self.treeView.set_cursor((0))
        gtk.Widget.grab_focus(self.treeView)
                
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
                if selectedPath != None:
                    self.click(self.treeView, (selectedPath), None)
            elif eventName == "Page_Up":
                utils.treeViewScrollVertical(self.treeView, True)
            elif eventName == "Page_Down":
                utils.treeViewScrollVertical(self.treeView, False)
            elif eventName == "Escape":
                self.hide()
            else:
                self.entry.event(keyPressEvent)
            self.propagateLock = False
            
            return True
        else:
            return False
        
    def clickCandiate(self, widget, event):
        '''Enter candidate.'''
        ex = int(event.x)
        ey = int(event.y)
        (selectedPath, _, cx, cy) = self.treeView.get_path_at_pos(ex, ey)
        self.click(self.treeView, selectedPath, None)
        
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
        
        if path == 0:
            self.searchCallback(self.entry)
        else:
            self.clickCandidateCallback(candidate)

#  LocalWords:  entry'height
