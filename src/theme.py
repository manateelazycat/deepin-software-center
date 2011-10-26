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
import gobject, gtk
import os

class DynamicLabel(object):
    '''Dynamic label.'''
    
    LABEL_NORMAL = 1
    LABEL_HOVER = 2
    LABEL_PRESS = 3
	
    def __init__(self, text, dColor, size=None, underline=None):
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
        
        print "__init__:\n %s" % (dir(self))
        
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
        print "exposeCallback:\n %s" % (dir(self))
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

class Theme(object):
    '''Theme.'''
    
    def __init__(self):
        '''Init theme.'''
        # Init.
        self.themeName = "default"
        self.colorPath = "colors.txt"
        self.labelColorPath = "labelColors.txt"
        self.pixbufDict = {}
        self.ticker = 0
        
        # Scan theme files.
        themeDir = self.getImageDir()
        for root, dirs, files in os.walk(themeDir):
            for filepath in files:
                path = (os.path.join(root, filepath)).split(themeDir)[1]
                self.pixbufDict[path] = DynamicPixbuf(self.getImagePath(path))
                
        # Scan dynamic colors.
        self.colorDict = {}
        for (colorName, color) in evalFile(self.getColorPath(self.colorPath)).items():
            self.colorDict[colorName] = DynamicColor(color)
        
        # Scan dynamic label colors.
        self.labelColorDict = {}
        for (colorName, colorTuple) in evalFile(self.getColorPath(self.labelColorPath)).items():
            self.labelColorDict[colorName] = DynamicLabelColor(colorTuple)
                
    def getImageDir(self):
        '''Get theme directory.'''
        return "../theme/%s/image/" % (self.themeName)
                
    def getImagePath(self, path):
        '''Get pixbuf path.'''
        return os.path.join(self.getImageDir(), path)

    def getColorDir(self):
        '''Get theme directory.'''
        return "../theme/%s/" % (self.themeName)
                
    def getColorPath(self, path):
        '''Get pixbuf path.'''
        return os.path.join(self.getColorDir(), path)
            
    def getDynamicPixbuf(self, path):
        '''Get dynamic pixbuf.'''
        return self.pixbufDict[path]
    
    def getDynamicColor(self, colorName):
        '''Get dynamic color.'''
        return self.colorDict[colorName]
    
    def getDynamicLabelColor(self, colorName):
        '''Get dynamic label color.'''
        return self.labelColorDict[colorName]
    
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
        for (colorName, color) in evalFile(self.getColorPath(self.colorPath)).items():
            self.colorDict[colorName].update(color)
            
        # Update dynamic label colors.
        for (colorName, colorTuple) in evalFile(self.getColorPath(self.labelColorPath)).items():
            self.labelColorDict[colorName].update(colorTuple)
            
# Init.
appTheme = Theme()            
