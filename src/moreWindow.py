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

from utils import *
from draw import *
import gtk
import pygtk
import utils
pygtk.require('2.0')

class MoreWindow(object):
    '''More window.'''
    
    ALIGN_X = 10
    ALIGN_Y = 4
	
    def __init__(self, widget):
        '''Init more window.'''
        self.widget = widget
        self.index = 0
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(False)
        self.window.set_transient_for(widget.get_toplevel())
        self.window.connect(
            "expose-event", 
            lambda w, e: moreWindowOnExpose(
                w, e,
                appTheme.getDynamicPixbuf("skin/background.png"),
                appTheme.getDynamicAlphaColor("frameLigtht"),
                appTheme.getDynamicColor("frame"),
                ))
        
        self.mainBox = gtk.VBox()
        self.mainAlign = gtk.Alignment()
        self.mainAlign.set(0.5, 0.5, 0.0, 0.0)
        self.mainAlign.set_padding(self.ALIGN_Y, self.ALIGN_Y, self.ALIGN_X, self.ALIGN_X)
        self.mainAlign.add(self.mainBox)
        self.window.add(self.mainAlign)
        
        # Create list item.
        self.createListItem(1, "新版功能", self.newFeature)
        self.createListItem(2, "论坛求助", self.forumHelp)
        self.createListItem(3, "加入我们", self.joinUs)
        self.createListItem(4, "问题反馈", self.reportProblem)

        # Set shape.
        self.window.connect("size-allocate", lambda w, a: updateShape(w, a, POPUP_WINDOW_RADIUS))

        # Hide window if user click on main window.
        widget.connect("button-press-event", lambda w, e: self.hide())
        
    def newFeature(self):
        '''New feature.'''
        NewFeature(self.widget)
    
    def forumHelp(self):
        '''Forum help.'''
        runCommand("xdg-open http://www.linuxdeepin.com/forum")
    
    def joinUs(self):
        '''Join us.'''
        runCommand("xdg-open http://www.linuxdeepin.com/recruitment")
    
    def reportProblem(self,):
        '''Report problem.'''
        runCommand("xdg-open http://www.linuxdeepin.com/forum/17")
    
    def setIndex(self, index):
        '''Set index.'''
        self.index = index
        self.hide()
    
    def getIndex(self):
        '''Get index.'''
        return self.index
        
    def show(self, x, y):
        '''Show.'''
        # Show.
        self.window.show_all()
        self.window.move(x, y)
        
    def hide(self):
        '''Hide.'''
        self.window.hide_all()

    def createListItem(self, index, name, callback):
        '''Create list item.'''
        button = gtk.Button()
        button.connect("button-press-event", lambda w, e: self.setIndex(index))
        button.connect("button-press-event", lambda w, e: callback())
        menuItemSetBackground(
            button,
            "category/sidebar_normal.png",
            "category/sidebar_hover.png",
            "category/sidebar_press.png",
            index,
            self.getIndex,
            )
        label = DynamicSimpleLabel(
            button,
            name,
            appTheme.getDynamicColor("menuItem"),
            LABEL_FONT_SIZE,
            ).getLabel()
        button.add(label)
        self.mainBox.pack_start(button)
    
class NewFeature:
    '''New feature.'''
    
    WINDOW_WIDTH = 360
    WINDOW_HEIGHT = 270
	
    def __init__(self, widget):
        '''Init new feature.'''
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(True)
        self.window.set_transient_for(widget.get_toplevel())
        self.window.set_property("accept-focus", False)
        
        self.window.connect("size-allocate", lambda w, a: updateShape(w, a, RADIUS))
        
        # Draw.
        drawThemeSelectWindow(
            self.window,
            appTheme.getDynamicPixbuf("skin/background.png"),
            appTheme.getDynamicColor("frame"),
            appTheme.getDynamicAlphaColor("frameLigtht"),
            )
        
        self.mainBox = gtk.VBox()
        self.window.add(self.mainBox)
        
        self.titleEventBox = gtk.EventBox()
        self.titleEventBox.set_visible_window(False)
        self.mainBox.pack_start(self.titleEventBox, False, False)
        
        self.titleAlign = gtk.Alignment()
        dLabel = DynamicSimpleLabel(
            self.titleAlign,
            "软件中心2.0新功能",
            appTheme.getDynamicColor("themeSelectTitleText"),
            LABEL_FONT_LARGE_SIZE,
            )
        self.titleLabel = dLabel.getLabel()
        alignY = 10
        self.titleAlign.set(0.0, 0.0, 1.0, 1.0)
        self.titleAlign.set_padding(alignY, alignY, 0, 0)
        self.titleAlign.add(self.titleLabel)
        self.titleEventBox.add(self.titleAlign)
        
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        drawVScrollbar(self.scrolledwindow)
        self.textView = DynamicTextView(
            self.scrolledwindow,
            appTheme.getDynamicColor("background"),
            appTheme.getDynamicColor("foreground"),
            ).textView
        utils.addInScrolledWindow(self.scrolledwindow, self.textView)
        self.textViewAlign = gtk.Alignment()
        self.textViewAlign.set(0.5, 0.5, 1.0, 1.0)
        self.textViewAlign.set_padding(10, 10, 10, 10)
        self.textViewAlign.add(self.scrolledwindow)
        self.mainBox.pack_start(self.textViewAlign)
        self.textView.set_editable(False)
        self.textView.set_wrap_mode(gtk.WRAP_CHAR)
        lang = getDefaultLanguage()
        if lang == "zh_CN":
            news = readFile("../news/%s.txt" % (lang))
        elif lang == "zh_TW":
            news = readFile("../news/%s.txt" % (lang))
        else:
            news = readFile("../news/en.txt")
        self.textView.get_buffer().set_text(news)
        
        self.window.set_size_request(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        (wx, wy) = widget.window.get_origin()
        rect = widget.get_allocation()
        self.window.move(
            wx + rect.x + (rect.width - self.WINDOW_WIDTH) / 2,
            wy + rect.y + (rect.height - self.WINDOW_HEIGHT) / 2,
            )
        self.window.show_all()
        
        # Hide window if user click on main window.
        widget.connect("button-press-event", lambda w, e: self.exit())
        
    def exit(self):
        '''Exit'''
        self.window.destroy()
        
