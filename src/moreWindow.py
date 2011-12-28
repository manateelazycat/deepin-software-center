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
from searchEntry import *
from utils import *
import gtk
import utils

class MoreWindow(object):
    '''More window.'''
    
    ALIGN_X = 10
    ALIGN_Y = 4
	
    def __init__(self, widget, messageCallback):
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
                ))
        self.newFeatureWindow = NewFeature(widget)
        self.proxySetupWindow = ProxySetup(widget, messageCallback)
        
        self.mainBox = gtk.VBox()
        self.mainAlign = gtk.Alignment()
        self.mainAlign.set(0.5, 0.5, 0.0, 0.0)
        self.mainAlign.set_padding(self.ALIGN_Y, self.ALIGN_Y, self.ALIGN_X, self.ALIGN_X)
        self.mainAlign.add(self.mainBox)
        self.window.add(self.mainAlign)
        
        # Create list item.
        self.createListItem(1, __("New Feature"), self.newFeature)
        # self.createListItem(2, __("Proxy Setup"), self.setProxy)
        self.createListItem(3, __("Forum Help"), self.forumHelp)
        self.createListItem(4, __("Report Problem"), self.reportProblem)

        # Set shape.
        self.window.connect("size-allocate", lambda w, a: updateShape(w, a, POPUP_WINDOW_RADIUS))

        # Hide window if user click on main window.
        widget.connect("button-press-event", lambda w, e: self.hide())
        
    def newFeature(self):
        '''New feature.'''
        self.newFeatureWindow.show()
        
    def setProxy(self):
        '''Set proxy.'''
        self.proxySetupWindow.show()
            
    def forumHelp(self):
        '''Forum help.'''
        sendCommand("xdg-open http://www.linuxdeepin.com/forum")
    
    def reportProblem(self,):
        '''Report problem.'''
        sendCommand("xdg-open http://www.linuxdeepin.com/forum/17")
    
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
            "menu/item_hover.png",
            index,
            self.getIndex,
            )
        label = DynamicSimpleLabel(
            button,
            name,
            appTheme.getDynamicColor("menuItem"),
            LABEL_FONT_SIZE,
            ).getLabel()
        label.set_alignment(0.0, 0.0)
        button.add(label)
        self.mainBox.pack_start(button)
    
class NewFeature(object):
    '''New feature.'''
    
    WINDOW_WIDTH = 380
    WINDOW_HEIGHT = 270
	
    def __init__(self, widget):
        '''Init new feature.'''
        self.widget = widget
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(False)
        self.window.set_transient_for(widget.get_toplevel())
        self.window.set_property("accept-focus", False)
        
        self.window.connect("size-allocate", lambda w, a: updateShape(w, a, RADIUS))
        
        # Draw.
        drawThemeSelectWindow(
            self.window,
            appTheme.getDynamicPixbuf("skin/background.png"),
            appTheme.getDynamicAlphaColor("frameLigtht"),
            )
        
        self.mainBox = gtk.VBox()
        self.mainEventBox = gtk.EventBox()
        self.mainEventBox.set_visible_window(False)
        self.mainEventBox.add(self.mainBox)
        self.window.add(self.mainEventBox)
        self.mainEventBox.connect("button-press-event", lambda w, e: utils.moveWindow(w, e, self.window))
        
        self.titleBox = gtk.HBox()
        self.mainBox.pack_start(self.titleBox, False, False)
        
        self.titleAlign = gtk.Alignment()
        dLabel = DynamicSimpleLabel(
            self.titleAlign,
            __("Software Center 2.0 New Feature"),
            appTheme.getDynamicColor("themeSelectTitleText"),
            LABEL_FONT_LARGE_SIZE,
            )
        self.titleLabel = dLabel.getLabel()
        alignY = 4
        alignX = 20
        self.titleAlign.set(0.0, 0.0, 0.0, 0.0)
        self.titleAlign.set_padding(alignY, alignY, alignX, alignX)
        self.titleAlign.add(self.titleLabel)
        self.titleBox.pack_start(self.titleAlign, True, True)
        
        self.closeButton = gtk.Button()
        self.closeButton.connect("button-release-event", lambda w, e: self.hide())
        drawButton(self.closeButton, "close", "navigate")
        self.titleBox.pack_start(self.closeButton, False, False)
        
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        drawVScrollbar(self.scrolledwindow)
        
        self.textView = DynamicTextView(
            self.scrolledwindow,
            appTheme.getDynamicColor("background"),
            appTheme.getDynamicColor("newFeatureText"),
            None
            ).textView
        utils.addInScrolledWindow(self.scrolledwindow, self.textView)
        self.textViewAlign = gtk.Alignment()
        self.textViewAlign.set(0.5, 0.5, 1.0, 1.0)
        self.textViewAlign.set_padding(10, 20, 20, 20)
        self.textViewAlign.add(self.scrolledwindow)
        self.textView.set_editable(False)
        self.textView.set_wrap_mode(gtk.WRAP_CHAR)
        self.mainBox.pack_start(self.textViewAlign, True, True)
        self.textView.get_buffer().set_text(__("News\n"))
        
        self.window.set_size_request(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Hide window if user click on main window.
        widget.connect("button-press-event", lambda w, e: self.hide())
        
    def show(self):
        '''Show.'''
        (wx, wy) = self.widget.window.get_origin()
        rect = self.widget.get_allocation()
        self.window.move(
            wx + rect.x + (rect.width - self.WINDOW_WIDTH) / 2,
            wy + rect.y + (rect.height - self.WINDOW_HEIGHT) / 2,
            )
        self.window.show_all()
        
    def hide(self):
        '''Hide.'''
        self.window.hide_all()

class ProxySetup(object):
    '''Proxy setup..'''
    
    WINDOW_WIDTH = 360
    WINDOW_HEIGHT = 193
    ALIGN_X = 20
    ALIGN_Y = 10
    ACTION_ALIGN_Y = 10
    SETUP_BUTTON_PADDING_X = 5
	
    def __init__(self, widget, messageCallback):
        '''Init proxy setup.'''
        self.widget = widget
        self.messageCallback = messageCallback
        self.window = gtk.Window()
        self.window.set_decorated(False)
        self.window.set_resizable(False)
        self.window.set_transient_for(widget.get_toplevel())
        self.window.connect("size-allocate", lambda w, a: updateShape(w, a, RADIUS))
        self.window.set_size_request(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Draw.
        drawThemeSelectWindow(
            self.window,
            appTheme.getDynamicPixbuf("skin/background.png"),
            appTheme.getDynamicAlphaColor("frameLigtht"),
            )
        
        self.mainBox = gtk.VBox()
        self.mainEventBox = gtk.EventBox()
        self.mainEventBox.set_visible_window(False)
        self.mainEventBox.add(self.mainBox)
        self.window.add(self.mainEventBox)
        self.mainEventBox.connect("button-press-event", lambda w, e: utils.moveWindow(w, e, self.window))
        
        self.titleBox = gtk.HBox()
        self.mainBox.pack_start(self.titleBox, False, False)
        
        self.titleAlign = gtk.Alignment()
        dLabel = DynamicSimpleLabel(
            self.titleAlign,
            __("Proxy Setup"),
            appTheme.getDynamicColor("themeSelectTitleText"),
            LABEL_FONT_LARGE_SIZE,
            )
        self.titleLabel = dLabel.getLabel()
        alignY = 4
        alignX = 20
        self.titleAlign.set(0.0, 0.0, 0.0, 0.0)
        self.titleAlign.set_padding(alignY, alignY, alignX, alignX)
        self.titleAlign.add(self.titleLabel)
        self.titleBox.pack_start(self.titleAlign, True, True)
        
        self.closeButton = gtk.Button()
        self.closeButton.connect("button-release-event", lambda w, e: self.hide())
        drawButton(self.closeButton, "close", "navigate")
        self.titleBox.pack_start(self.closeButton, False, False)
        
        self.setupBox = gtk.VBox()
        self.setupAlign = gtk.Alignment()
        self.setupAlign.set(0.0, 0.0, 1.0, 1.0)
        self.setupAlign.set_padding(self.ALIGN_Y, self.ALIGN_Y, self.ALIGN_X, self.ALIGN_X + 10)
        self.setupAlign.add(self.setupBox)
        self.mainBox.pack_start(self.setupAlign, False, False)
        
        self.itemLabelWidth = 8
        
        (self.addressBox, self.addressLabel, self.addressEntry) = self.createInputItem(__("Proxy Address"))
        (self.portBox, self.portLabel, self.portEntry) = self.createInputItem(__("Proxy Port"))
        (self.userBox, self.userLabel, self.userEntry) = self.createInputItem(__("Proxy User"))
        (self.passwordBox, self.passwordLabel, self.passwordEntry) = self.createInputItem(__("Proxy Password"), True)
        
        self.setupBox.pack_start(self.addressBox)
        self.setupBox.pack_start(self.portBox)
        self.setupBox.pack_start(self.userBox)
        self.setupBox.pack_start(self.passwordBox)
        
        self.actionBox = gtk.HBox()
        self.actionAlign = gtk.Alignment()
        self.actionAlign.set(1.0, 0.5, 0.0, 0.0)
        self.actionAlign.set_padding(self.ACTION_ALIGN_Y, self.ACTION_ALIGN_Y, 0, 0)
        self.actionAlign.add(self.actionBox)
        self.setupBox.pack_start(self.actionAlign, True, True)
        
        buttonPaddingX = 10
        self.setupButton = utils.newButtonWithoutPadding()
        self.setupButton.connect("button-press-event", lambda w, e: self.setProxy())
        drawButton(self.setupButton, "button", "proxySetup", True, __("Proxy OK"), BUTTON_FONT_SIZE_SMALL, "buttonFont")
        self.actionBox.pack_start(self.setupButton, False, False, buttonPaddingX)

        self.cancelButton = utils.newButtonWithoutPadding()
        self.cancelButton.connect("button-press-event", lambda w, e: self.cancelProxy())
        drawButton(self.cancelButton, "button", "proxySetup", True, __("Proxy Cancel"), BUTTON_FONT_SIZE_SMALL, "buttonFont")
        self.actionBox.pack_start(self.cancelButton, False, False)
        
        # Read proxy setup.
        self.readProxySetup()
            
        # Hide window if user click on main window.
        widget.connect("button-press-event", lambda w, e: self.hide())
        
    def readProxySetup(self):
        '''Read proxy setup.'''
        proxyString = evalFile("./proxy", True)
        if proxyString != None:
            proxyDict = proxyString
        else:
            proxyDict = {}
            
        if proxyDict.has_key("address"):
            self.addressEntry.set_text(proxyDict["address"])
        else:
            self.addressEntry.set_text("")
        if proxyDict.has_key("port"):
            self.portEntry.set_text(proxyDict["port"])
        else:
            self.portEntry.set_text("")
        if proxyDict.has_key("user"):
            self.userEntry.set_text(proxyDict["user"])
        else:
            self.userEntry.set_text("")
        if proxyDict.has_key("password"):
            self.passwordEntry.set_text(proxyDict["password"])
        else:
            self.passwordEntry.set_text("")
        
    def createInputItem(self, labelName, isPassword=False):
        '''Create input item.'''
        itemBox = gtk.HBox()
        itemLabel = DynamicSimpleLabel(
            itemBox,
            labelName,
            appTheme.getDynamicColor("background"),
            ).getLabel()
        
        itemLabel.set_alignment(0.0, 0.5)
        itemLabel.set_width_chars(self.itemLabelWidth)
        
        itemBox.pack_start(itemLabel, False, False)
        itemEntry = SearchEntry(
            itemBox,
            "",
            appTheme.getDynamicColor("entryHint"),
            appTheme.getDynamicColor("entryBackground"),
            appTheme.getDynamicColor("entryForeground"),
            True,
            )
        if isPassword:
            itemEntry.set_visibility(False)
            
        itemBox.pack_start(itemEntry, True, True)
        
        return (itemBox, itemLabel, itemEntry)
        
    def setProxy(self):
        '''Set proxy.'''
        # Read proxy string.
        address = utils.getEntryText(self.addressEntry)
        port = utils.getEntryText(self.portEntry)
        user = utils.getEntryText(self.userEntry)
        password = utils.getEntryText(self.passwordEntry)
        
        # Save proxy setup.
        writeFile(
            "./proxy", 
            str({"address" : address,
                 "port" : port,
                 "user" : user,
                 "password" : password}))
        
        # Hide window.
        self.hide()
        
        # Display message.
        self.messageCallback(__("Setup proxy!"))
            
    def cancelProxy(self):
        '''Cancel proxy.'''
        # Save proxy setup.
        writeFile("./proxy", "{}")
        
        # Hide window.
        self.hide()
        
        # Display message.
        self.messageCallback(__("Cancel proxy!"))
        
    def show(self):
        '''Show.'''
        (wx, wy) = self.widget.window.get_origin()
        rect = self.widget.get_allocation()
        self.window.move(
            wx + rect.x + (rect.width - self.WINDOW_WIDTH) / 2,
            wy + rect.y + (rect.height - self.WINDOW_HEIGHT) / 2,
            )
        self.window.show_all()
        
        self.readProxySetup()
        
    def hide(self):
        '''Hide.'''
        self.window.hide_all()
