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

from lang import __, getDefaultLanguage
from utils import *
import gobject, gtk
import os

class DynamicTreeView(object):
    '''Dynamic tree view.'''
	
    def __init__(self, parent, liststore, backgroundDColor, selectDColor):
        '''Init dynamic tree view.'''
        self.treeView = gtk.TreeView(liststore)
        self.backgroundDColor = backgroundDColor
        self.selectDColor = selectDColor
        self.ticker = 0
        
        self.updateColor()
        self.treeView.connect("expose-event", self.exposeCallback)
        
        parent.connect("size-allocate", lambda w, e: self.treeView.realize())
        
    def updateColor(self):
        '''Update color.'''
        self.treeView.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.backgroundDColor.getColor()))
        self.treeView.modify_base(gtk.STATE_ACTIVE, gtk.gdk.color_parse(self.selectDColor.getColor()))
        
    def exposeCallback(self, widget, event):
        '''Expose callback.'''
        if self.ticker != appTheme.ticker:
            self.ticker = appTheme.ticker
            self.updateColor()
            
        return False

class DynamicTextView(object):
    '''Dynamic text view.'''
	
    def __init__(self, parent, backgroundDColor, foregroundDColor, backgroundDPixbuf=None):
        '''Init dynamic text view.'''
        self.textView = gtk.TextView()
        self.backgroundDColor = backgroundDColor
        self.foregroundDColor = foregroundDColor
        self.backgroundDPixbuf = backgroundDPixbuf
        self.ticker = 0

        self.updateColor()
        self.textView.connect("expose-event", self.exposeCallback)
        self.textView.connect("realize", lambda w: self.updateBackground())
        
        parent.connect("size-allocate", lambda w, e: self.textView.realize())
        
    def updateColor(self):
        '''Update color.'''
        self.textView.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.backgroundDColor.getColor()))
        self.textView.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(self.foregroundDColor.getColor()))
        self.updateBackground()
        
    def updateBackground(self):
        '''Update background.'''
        if self.backgroundDPixbuf != None and self.textView.get_realized():
            (pixmap, _) = self.backgroundDPixbuf.getPixbuf().render_pixmap_and_mask(127)
            self.textView.get_window(gtk.TEXT_WINDOW_TEXT).set_back_pixmap(pixmap, False)
        
    def exposeCallback(self, widget, event):
        '''Expose callback.'''
        if self.ticker != appTheme.ticker:
            self.ticker = appTheme.ticker
            self.updateColor()
            
        return False

class DynamicLabel(object):
    '''Dynamic label.'''
    
    LABEL_NORMAL = 1
    LABEL_HOVER = 2
    LABEL_PRESS = 3
	
    def __init__(self, parent, text, dColor, size=None, underline=None):
        '''Init dynamic label.'''
        self.status = self.LABEL_NORMAL
        self.text = text
        self.dColor = dColor
        self.ticker = 0
        
        if size == None:
            self.size = ""
        else:
            self.size = "size='%s'" % (size)
            
        if underline == None:
            self.underline = ""
        else:
            self.underline = "underline='%s'" % (underline)
            
        self.label = gtk.Label()
        self.draw()
        self.label.connect("expose-event", self.exposeCallback)
        
        parent.connect("size-allocate", lambda w, e: self.label.realize())
        
    def getLabel(self):
        '''Get label.'''
        return self.label
    
    def normalLabel(self):
        '''Normal label.'''
        self.status = self.LABEL_NORMAL
        self.draw()

    def hoverLabel(self):
        '''Hover label.'''
        self.status = self.LABEL_HOVER
        self.draw()
    
    def pressLabel(self):
        '''Press label.'''
        self.status = self.LABEL_PRESS
        self.draw()

    def draw(self):
        '''Draw.'''
        if self.status == self.LABEL_NORMAL:
            color = self.dColor.getNormalColor()
        elif self.status == self.LABEL_HOVER:
            color = self.dColor.getHoverColor()
        else:
            color = self.dColor.getPressColor()
        
        self.label.set_markup("<span foreground='%s' %s %s>%s</span>" % (color, self.size, self.underline, self.text))
        
    def exposeCallback(self, widget, event):
        '''Draw label.'''
        if self.ticker != appTheme.ticker:
            self.ticker = appTheme.ticker
            self.draw()
        
        return False
    
class DynamicLabelColor(object):
    '''Dynamic color.'''
    
    def __init__(self, (nColor, hColor, pColor)):
        '''Init.'''
        self.update((nColor, hColor, pColor))
        
    def update(self, (nColor, hColor, pColor)):
        '''Update path.'''
        self.normalColor = nColor
        self.hoverColor = hColor
        self.pressColor = pColor

    def getNormalColor(self):
        '''Get normal color.'''
        return self.normalColor

    def getHoverColor(self):
        '''Get hover color.'''
        return self.hoverColor

    def getPressColor(self):
        '''Get press color.'''
        return self.pressColor

class DynamicSimpleLabel(object):
    '''Dynamic label.'''
	
    def __init__(self, parent, text, dColor, size=None):
        '''Init dynamic label.'''
        self.text = text
        self.dColor = dColor
        self.ticker = 0
        
        if size == None:
            self.size = ""
        else:
            self.size = "size='%s'" % (size)
            
        self.label = gtk.Label()
        self.draw()
        self.label.connect("expose-event", self.exposeCallback)
        
        parent.connect("size-allocate", lambda w, e: self.label.realize())
        
    def getLabel(self):
        '''Get label.'''
        return self.label
    
    def draw(self):
        '''Draw.'''
        self.label.set_markup("<span foreground='%s' %s>%s</span>" % (self.dColor.getColor(), self.size, self.text))
        
    def exposeCallback(self, widget, event):
        '''Draw label.'''
        if self.ticker != appTheme.ticker:
            self.ticker = appTheme.ticker
            self.draw()
        
        return False
    
class DynamicColor(object):
    '''Dynamic color.'''
    
    def __init__(self, color):
        '''Init.'''
        self.update(color)
        
    def update(self, color):
        '''Update path.'''
        self.color = color

    def getColor(self):
        '''Get color.'''
        return self.color

class DynamicAlphaColor(object):
    '''Dynamic alpha color.'''
    
    def __init__(self, colorInfo):
        '''Init.'''
        self.update(colorInfo)
        
    def update(self, colorInfo):
        '''Update path.'''
        (self.color, self.alpha) = colorInfo
        
    def getColorInfo(self):
        '''Get color info.'''
        return (self.color, self.alpha)

    def getColor(self):
        '''Get color info.'''
        return self.color
    
    def getAlpha(self):
        '''Get alpha.'''
        return self.alpha
    
class DynamicPixbuf(object):
    '''Dynamic pixbuf.'''
    
    def __init__(self, filepath):
        '''Init.'''
        self.update(filepath)
        
    def update(self, filepath):
        '''Update path.'''
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(filepath)

    def getPixbuf(self):
        '''Get pixbuf.'''
        return self.pixbuf

class DynamicPixbufAnimation(object):
    '''Dynamic pixbuf animation.'''
    
    def __init__(self, filepath):
        '''Init.'''
        self.update(filepath)
        
    def update(self, filepath):
        '''Update path.'''
        self.pixbufAnimation = gtk.gdk.PixbufAnimation(filepath)

    def getPixbufAnimation(self):
        '''Get pixbuf animation.'''
        return self.pixbufAnimation
    
class DynamicImage(object):
    '''Dynamic image.'''
	
    def __init__(self, parent, dPixbufAnimation):
        '''Init dynamic image.'''
        self.dPixbufAnimation = dPixbufAnimation
        self.image = gtk.Image()
        self.ticker = 0

        self.updateAnimation()
        self.image.connect("expose-event", self.exposeCallback)
        
        parent.connect("size-allocate", lambda w, e: self.image.realize())
        
    def updateAnimation(self):
        '''Update animation.'''
        self.image.set_from_animation(self.dPixbufAnimation.getPixbufAnimation())    
        
    def exposeCallback(self, widget, event):
        '''Expose callback.'''
        if self.ticker != appTheme.ticker:
            self.ticker = appTheme.ticker
            self.updateAnimation()
            
        return False
    
class DynamicDrawType(object):
    '''Dynamic draw type.'''
	
    def __init__(self, dType):
        '''Init dynamic type.'''
        self.update(dType)
        
    def update(self, dType):
        '''Update dynamic type.'''
        self.type = dType

    def getType(self):
        '''Get dynamic type.'''
        return self.type    

class Theme(object):
    '''Theme.'''
    
    def __init__(self):
        '''Init theme.'''
        # Init.
        themes = os.listdir("../theme")
        themeName = readFile("./defaultTheme", True)
        if themeName == "" or not themeName in themes:
            if "default" in themes:
                self.themeName = "default"
            else:
                self.themeName = themes[0]
        else:
            self.themeName = themeName
        self.colorPath = "colors.txt"
        self.drawTypePath = "types.txt"
        self.ticker = 0
        self.pixbufDict = {}
        self.colorDict = {}
        self.labelColorDict = {}
        self.alphaColorDict = {}
        self.drawTypeDict = {}
        self.animationDict = {}
        
        # Scan theme files.
        themeDir = self.getImageDir()
        for root, dirs, files in os.walk(themeDir):
            for filepath in files:
                path = (os.path.join(root, filepath)).split(themeDir)[1]
                self.pixbufDict[path] = DynamicPixbuf(self.getImagePath(path))
                
        # Scan dynamic colors.
        colors = evalFile(self.getColorPath(self.colorPath))
        
        for (colorName, color) in colors["colors"].items():
            self.colorDict[colorName] = DynamicColor(color)

        for (colorName, colorTuple) in colors["labelColors"].items():
            self.labelColorDict[colorName] = DynamicLabelColor(colorTuple)

        for (colorName, colorInfo) in colors["alphaColors"].items():
            self.alphaColorDict[colorName] = DynamicAlphaColor(colorInfo)
            
        # Scan dynamic draw type.
        types = evalFile(self.getThemeDir() + self.drawTypePath)
        
        for (typeName, typeInfo) in types.items():
            self.drawTypeDict[typeName] = DynamicDrawType(typeInfo)
            
        # Scan animation.
        animationDir = self.getAnimationDir()
        for root, dirs, files in os.walk(animationDir):
            for filepath in files:
                path = (os.path.join(root, filepath)).split(animationDir)[1]
                self.animationDict[path] = DynamicPixbufAnimation(self.getAnimationPath(path))
                
    def getImageDir(self):
        '''Get theme directory.'''
        return "../theme/%s/image/" % (self.themeName)

    def getImagePath(self, path):
        '''Get pixbuf path.'''
        return os.path.join(self.getImageDir(), path)

    def getAnimationDir(self):
        '''Get theme directory.'''
        return "../theme/%s/animation/" % (self.themeName)

    def getAnimationPath(self, path):
        '''Get pixbuf path.'''
        return os.path.join(self.getAnimationDir(), path)
    
    def getThemeDir(self):
        '''Get theme directory.'''
        return "../theme/%s/" % (self.themeName)
                
    def getColorPath(self, path):
        '''Get pixbuf path.'''
        return os.path.join(self.getThemeDir(), path)
            
    def getDynamicPixbuf(self, path):
        '''Get dynamic pixbuf.'''
        return self.pixbufDict[path]

    def getDynamicPixbufAnimation(self, path):
        '''Get dynamic pixbuf animation.'''
        return self.animationDict[path]
    
    def getDynamicColor(self, colorName):
        '''Get dynamic color.'''
        return self.colorDict[colorName]
    
    def getDynamicLabelColor(self, colorName):
        '''Get dynamic label color.'''
        return self.labelColorDict[colorName]

    def getDynamicAlphaColor(self, colorName):
        '''Get dynamic label color.'''
        return self.alphaColorDict[colorName]
    
    def getDynamicDrawType(self, typeName):
        '''Get dynamic type name.'''
        return self.drawTypeDict[typeName]
    
    def changeTheme(self, newThemeName):
        '''Change theme.'''
        # Update ticker.
        self.ticker += 1
        
        # Change theme name.
        self.themeName = newThemeName

        # Update dynmaic pixbuf.
        for (path, pixbuf) in self.pixbufDict.items():
            pixbuf.update(self.getImagePath(path))
            
        # Update dynamic colors.
        colors = evalFile(self.getColorPath(self.colorPath))
            
        for (colorName, color) in colors["colors"].items():
            self.colorDict[colorName].update(color)
            
        # Update dynamic label colors.
        for (colorName, colorTuple) in colors["labelColors"].items():
            self.labelColorDict[colorName].update(colorTuple)

        # Update dynamic alpha colors.
        for (colorName, colorInfo) in colors["alphaColors"].items():
            self.alphaColorDict[colorName].update(colorInfo)
            
        # Scan dynamic draw type.
        types = evalFile(self.getThemeDir() + self.drawTypePath)
        
        for (typeName, typeInfo) in types.items():
            self.drawTypeDict[typeName].update(typeInfo)
            
        # Update animation.
        for (path, animation) in self.animationDict.items():
            animation.update(self.getAnimationPath(path))
            
        # Remeber theme.
        writeFile("./defaultTheme", newThemeName)
            
# Init.
appTheme = Theme()            
