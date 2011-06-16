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

from constant import *
from math import pi
import cairo
import gtk
import math
import os
import pango
import pangocairo
import pygtk
import subprocess
import time
pygtk.require('2.0')

def isDoubleClick(event):
    '''Whether an event is double click?'''
    return event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS

def getStarImg(starIndex, starLevel, starSize):
    '''Get start pixbuf.'''
    pixbuf = getStarPixbuf(starIndex, starLevel, starSize)
    return gtk.image_new_from_pixbuf(pixbuf)        
    
def getStarPixbuf(starIndex, starLevel, starSize):
    '''Get star pixbuf.'''
    imgPath = getStarPath(starIndex, starLevel)
    
    if starSize == None:
        return gtk.gdk.pixbuf_new_from_file(imgPath)        
    else:
        return gtk.gdk.pixbuf_new_from_file_at_size(imgPath, starSize, starSize)        
    
def getStarPath(starIndex, starLevel):
    '''Get star path.'''
    if starIndex == 1:
        if starLevel > 8:
            imgPath = "star_green.png"
        elif starLevel > 2:
            imgPath = "star_yellow.png"
        elif starLevel == 2:
            imgPath = "star_red.png"
        else:
            imgPath = "halfstar_red.png"
    elif starIndex in [2, 3, 4]:
        if starLevel > 8:
            imgPath = "star_green.png"
        elif starLevel >= starIndex * 2:
            imgPath = "star_yellow.png"
        elif starLevel == starIndex * 2 - 1:
            imgPath = "halfstar_yellow.png"
        else:
            imgPath = "star_gray.png"
    elif starIndex == 5:
        if starLevel >= starIndex * 2:
            imgPath = "star_green.png"
        elif starLevel == starIndex * 2 - 1:
            imgPath = "halfstar_green.png"
        else:
            imgPath = "star_gray.png"
            
    imgDir = "./icons/cell/"
    return imgDir + imgPath

def getFontFamilies():
    '''Get all font families in system.'''
    fontmap = pangocairo.cairo_font_map_get_default()
    return map (lambda f: f.get_name(), fontmap.list_families())

def getScreenSize(widget):
    '''Get widget's screen size.'''
    screen = widget.get_screen()
    width = screen.get_width()
    height = screen.get_height()
    return (width, height)

def getPkgIcon(pkg, iconWidth=32, iconHeight=32):
    '''Get package icon.'''
    iconPath = "./AppIcon/" + pkg.name + ".png"
    if os.path.exists (iconPath):
        return gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(iconPath, iconWidth, iconHeight))
    else:
        return gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size("./icons/icon/appIcon.ico", 
                                                                              iconWidth, iconHeight))
def getPkgName(pkg):
    '''Get package name.'''
    return pkg.name

def evalFile(filepath):
    '''Eval file content.'''
    readFile = open(filepath, "r")
    content = eval(readFile.read())
    readFile.close()
    
    return content

def getPkgShortDesc(pkg):
    '''Get package's short description.'''
    pkgPath = "./pkgInfo/" + pkg.name
    if os.path.exists(pkgPath):
        return ((evalFile(pkgPath))["zh-CN"])["shortDesc"]
    else:
        return pkg.candidate.summary

def getPkgLongDesc(pkg):
    '''Get package's long description.'''
    pkgPath = "./pkgInfo/" + pkg.name
    if os.path.exists(pkgPath):
        return ((evalFile(pkgPath))["zh-CN"])["longDesc"]
    else:
        return pkg.candidate.description

def getPkgVersion(pkg):
    '''Get package's version.'''
    # Return current version if package has installed. 
    if pkg.is_installed:
        return pkg.installed.version    
    # Otherwise return newest version.
    else:
        return pkg.candidate.version

def getPkgNewestVersion(pkg):
    '''Get package's newest version.'''
    return pkg.candidate.version

def getPkgSection(pkg):
    '''Get package's section.'''
    return pkg.candidate.section

def getPkgSize(pkg):
    '''Get package's  size.'''
    return pkg.candidate.size

def getPkgInstalledSize(pkg):
    '''Get package's installed size.'''
    return pkg.candidate.installed_size

def getPkgDependSize(cache, pkg, action):
    '''Get package's dependent size.'''
    try:
        # Clear first.
        cache.clear()
        
        # Mark package.
        if action == ACTION_INSTALL:
            pkg.mark_install()
        elif action == ACTION_UPGRADE:
            pkg.mark_upgrade()
        else:
            pkg.mark_delete()
            
        # Get change size.
        cache.get_changes()
        downloadSize = cache.required_download
        useSize = abs(cache.required_space)
        
        # Clear last.
        cache.clear()
        
        return (downloadSize, useSize)
    except Exception, e:
        # Just return package's size if exception throwed.
        print "Calculate `%s` dependent used size failed, instead package's used size." % (getPkgName(pkg))
        return (pkg.candidate.size, pkg.candidate.installed_size)

def runCommand(commands):
    '''Run command and return result.'''
    process = subprocess.Popen(commands, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.readline()
    
def getKernelPackages():
    '''Get running kernel packages.'''
    kernelVersion = (runCommand(["uname", "-r"]).split("-generic"))
    
    return ["linux-image-generic", 
            "linux-image-%s-generic" % (kernelVersion),
            "linux-headers-generic", 
            "linux-headers-%s" % (kernelVersion),
            "linux-headers-%s-generic" % (kernelVersion),
            "linux-generic"
            ]

KERNEL_PACKAGES = getKernelPackages()    
    
def isPkgUninstallable(pkg, checkInstalled=True):
    '''Is pkg is uninstallable?'''
    inFilterSection = pkg.candidate.section in ["libs", "libdevel", "oldlibs"]
    isKernelPackages = pkg.name in KERNEL_PACKAGES
    
    # When first use cache need check installed.
    if checkInstalled:
        return pkg.is_installed and not pkg.essential and not inFilterSection and not isKernelPackages
    # Don't need check installed status when running.
    # Because package's is_installed not update sometimes.
    else:
        return not pkg.essential and not inFilterSection and not isKernelPackages

def containerRemoveAll(container):
    '''Remove all child widgets from container.'''
    container.foreach(lambda widget: container.remove(widget))

def formatFileSize(bytes, precision=2):
    '''Returns a humanized string for a given amount of bytes'''
    bytes = int(bytes)
    if bytes is 0:
        return '0B'
    else:
        log = math.floor(math.log(bytes, 1024))
        quotient = 1024 ** log
        size = bytes / quotient
        remainder = bytes % quotient
        if remainder < 10 ** (-precision): 
            prec = 0
        else:
            prec = precision
        return "%.*f%s" % (prec,
                           size,
                           ['B', 'KB', 'MB', 'GB', 'TB','PB', 'EB', 'ZB', 'YB']
                           [int(log)])

def pixbufNewFromIcon(stockId, size):
    '''Create pixbuf from given id and size.'''
    iconTheme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())
    return iconTheme.load_icon(stockId, size, gtk.ICON_LOOKUP_USE_BUILTIN)

def isInRect((cx, cy), (x, y, w, h)):
    '''Whether coordinate in rectangle.'''
    return (cx >= x and cx <= x + w and cy >= y and cy <= y + h)

def scrollToTop(scrolledWindow):
    '''Scroll scrolled window to top.'''
    scrolledWindow.get_vadjustment().set_value(0)
    
def runGUI(fun):
    '''Run gui code in main thread.'''
    gtk.gdk.threads_enter()
    fun
    gtk.gdk.threads_leave()

def postGUI(func):
    '''Post GUI code in main thread.'''
    def wrap(*a, **kw):
        gtk.gdk.threads_enter()
        ret = func(*a, **kw)
        gtk.gdk.threads_leave()
        return ret
    return wrap

def setProgress(progressbar, progress):
    '''Set progress.'''
    progressbar.set_fraction(progress / 100.0)
    if progress == 0:
        progressbar.set_text("")
    else:
        progressbar.set_text(str(progress) + "%")

def resizeWindow(widget, event, window):
    '''Resize window.'''
    # If a shift key is pressed, start resizing
    if event.state & gtk.gdk.SHIFT_MASK:
        window.begin_resize_drag(
            gtk.gdk.WINDOW_EDGE_SOUTH_EAST, 
            event.button, 
            int(event.x_root), 
            int(event.y_root), 
            event.time)
    
def moveWindow(widget, event, window):
    '''Move window.'''
    window.begin_move_drag(
        event.button, 
        int(event.x_root), 
        int(event.y_root), 
        event.time)

def addInScrolledWindow(scrolledWindow, widget, shadowType=gtk.SHADOW_NONE):
    '''Like add_with_viewport in ScrolledWindow, with shadow type.'''
    scrolledWindow.add_with_viewport(widget)
    viewport = scrolledWindow.get_child()
    if viewport != None:
        viewport.set_shadow_type(shadowType)
    else:
        print "addInScrolledWindow: Impossible, no viewport widget in ScrolledWindow!"
    
def newButtonWithoutPadding(content=None):
    '''Create button without padding.'''
    button = gtk.Button(content)
    button.set_property("can-focus", False)
    return button

def getFontYCoordinate(y, height, fontSize):
    '''Get font y coordinate.'''
    return y + (height + fontSize) / 2 - 1

# This is a hacking way, 
# Author recommend use xmlrpclib.ServerProxy('http://localhost:6800/rpc').getVersion() get version number.
# But above solution easy to failed when connect is unavailable.
# So i pick version information from output of command "aria2c --version".
def getAria2Version():
    '''Get aria2 version.'''
    versionList = runCommand(["aria2c", "--version"]).split().pop().split('.')
    
    return (int(versionList[0]), int(versionList[1]), int(versionList[2]))

def getCandidates(pkgs, text):
    '''Get candidates.'''
    if len(text) == 0:
        return []
    else:
        # Filter match candidates.
        candidates = []
        for pkg in pkgs:
            if text in pkg:
                (preStr, matchStr, restStr) = pkg.partition(text)
                candidates.append((preStr, matchStr, restStr, pkg))
                
        return map(lambda (preStr, matchStr, restStr, pkg): 
                   # Highlight keyword.
                   [preStr + "<span foreground='#00BBBB'><b>" + matchStr + "</b></span>" + restStr, pkg],
                   # Sorted candidates.
                   sorted(candidates, cmp=compareCandidates))
    
def compareCandidates((preA, matchA, restA, pkgA), (preB, matchB, restB, pkgB)):
    '''Compare candidates.'''
    lenA = len(preA)
    lenB = len(preB)
    # Candidate's order at front if pre string's length shorter.
    if lenA < lenB:
        return -1
    # Compare package name if pre string's length is same.
    elif lenA == lenB:
        return cmp(pkgA, pkgB)
    else:
        return 1        

def getCurrentTime():
    '''Get current time.'''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def setClickableCursor(widget):
    '''Set clickable cursor.'''
    # Use widget in lambda, and not widget pass in function.
    # Otherwise, if widget free before callback, you will got error:
    # free variable referenced before assignment in enclosing scope, 
    widget.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    widget.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
        
def setCursor(widget, cursorType):
    '''Set cursor.'''
    widget.window.set_cursor(gtk.gdk.Cursor(cursorType))

def setDefaultCursor(widget):
    '''Set default cursor.'''
    widget.window.set_cursor(None)

def setLabelMarkup(widget, label, normalMarkup, activeMarkup):
    '''Set label markup.'''
    widget.connect("enter-notify-event", lambda w, e: setMarkup(label, activeMarkup))
    widget.connect("leave-notify-event", lambda w, e: setMarkup(label, normalMarkup))
    
def setMarkup(label, markup):
    '''Set markup.'''
    label.set_markup(markup)

def setClickableLabel(widget, label, normalMarkup, activeMarkup):
    '''Set clickable label.'''
    # Set label markup.
    widget.connect("enter-notify-event", lambda w, e: setMarkup(label, activeMarkup))
    widget.connect("leave-notify-event", lambda w, e: setMarkup(label, normalMarkup))
    
    # Set label cursor.
    widget.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    widget.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))

def setCustomizeClickableCursor(eventbox, widget, cursorPath):
    '''Set clickable cursor.'''
    eventbox.connect("enter-notify-event", lambda w, e: setCustomizeCursor(widget, cursorPath))
    eventbox.connect("leave-notify-event", lambda w, e: setDefaultCursor(widget))
        
def setCustomizeCursor(widget, cursorPath):
    '''Set cursor.'''
    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.display_get_default(),
                                            gtk.gdk.pixbuf_new_from_file_at_size(cursorPath, 32, 32),
                                            0, 0))
