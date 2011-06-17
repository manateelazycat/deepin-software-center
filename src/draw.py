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
from utils import *
import cairo
import gtk
import math
import os
import pango
import pangocairo
import progressbar as pb
import pygtk
pygtk.require('2.0')

def eventBoxSetBackground(widget, scaleX, scaleY, normalImg):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = image.get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = image.get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect_after("expose-event", lambda w, e: eventBoxOnExpose(
            w, e,
            scaleX, scaleY,
            normalImg))
        
def eventBoxOnExpose(widget, event, 
                     scaleX, scaleY,
                     normalImg):
    '''Expose function to replace event box's image.'''
    image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    if scaleX:
        imageWidth = widget.allocation.width
    else:
        imageWidth = image.get_width()
        
    if scaleY:
        imageHeight = widget.allocation.height
    else:
        imageHeight = image.get_height()
    
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def buttonSetBackground(widget, scaleX, scaleY, normalImg, hoverImg, pressImg, 
                        buttonLabel=None, fontSize=None, labelColor=None):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = image.get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = image.get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    # Add button label if buttonLabel is not None.
    if buttonLabel != None:
        if labelColor == None:
            color = "#000000"
        else:
            color = labelColor
            
        if fontSize == None:
            size = "medium"
        else:
            size = int (fontSize * 1000)

        label = gtk.Label()
        label.set_markup("<span foreground='%s' size='%s'>%s</span>" % (color, size, buttonLabel))
        widget.add(label)
    
    widget.connect("expose-event", lambda w, e: buttonOnExpose(
            w, e,
            scaleX, scaleY,
            normalImg, hoverImg, pressImg))
        
def buttonOnExpose(widget, event, 
                   scaleX, scaleY,
                   normalImg, hoverImg, pressImg):
    '''Expose function to replace event box's image.'''
    if widget.state == gtk.STATE_NORMAL:
        image = gtk.gdk.pixbuf_new_from_file(normalImg)
    elif widget.state == gtk.STATE_PRELIGHT:
        image = gtk.gdk.pixbuf_new_from_file(hoverImg)
    elif widget.state == gtk.STATE_ACTIVE:
        image = gtk.gdk.pixbuf_new_from_file(pressImg)
    
    if scaleX:
        imageWidth = widget.allocation.width
    else:
        imageWidth = image.get_width()
        
    if scaleY:
        imageHeight = widget.allocation.height
    else:
        imageHeight = image.get_height()
    
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def simpleButtonSetBackground(widget, scaleX, scaleY, normalImg):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = image.get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = image.get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: simpleButtonOnExpose(
            w, e,
            scaleX, scaleY,
            normalImg))
        
def simpleButtonOnExpose(widget, event, 
                         scaleX, scaleY,
                         normalImg):
    '''Expose function to replace event box's image.'''
    image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    if scaleX:
        imageWidth = widget.allocation.width
    else:
        imageWidth = image.get_width()
        
    if scaleY:
        imageHeight = widget.allocation.height
    else:
        imageHeight = image.get_height()
    
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf, 
               widget.allocation.x,
               widget.allocation.y)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def fontButtonSetBackground(widget, width, height, content, 
                            normalColor, hoverColor, selectColor):
    '''Set event box's background.'''
    widget.set_size_request(width, height)
    
    widget.connect("expose-event", lambda w, e: fontButtonOnExpose(
            w, e,
            content, width,
            normalColor, hoverColor, selectColor))
        
def fontButtonOnExpose(widget, event, 
                       content, width,
                       normalColor, hoverColor, selectColor):
    '''Expose function to replace event box's image.'''
    if widget.state == gtk.STATE_NORMAL:
        color = normalColor
    elif widget.state == gtk.STATE_PRELIGHT:
        color = hoverColor
    elif widget.state == gtk.STATE_ACTIVE:
        color = selectColor
    
    x, y, height = widget.allocation.x, widget.allocation.y, widget.allocation.height
    
    fontSize = 14
    
    cr = widget.window.cairo_create()
    drawFont(cr, content, fontSize, color,
             x, getFontYCoordinate(y, height, fontSize))

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def navButtonSetBackground(widget, 
                           navName, navImg,
                           hoverImg, pressImg,
                           pageId, getPageId):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(hoverImg)
    requestWidth = image.get_width()
    requestHeight = image.get_height()
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: navButtonOnExpose(
            w, e,
            navName, navImg,
            hoverImg, pressImg, 
            pageId, getPageId))
        
def navButtonOnExpose(widget, event, 
                      navName, navImg,
                      hoverImg, pressImg,
                      pageId, getPageId):
    '''Expose function to replace event box's image.'''
    # Init.
    selectPageId = getPageId()
    
    # Draw background.
    backgroundPixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
    backgroundWidth = backgroundPixbuf.get_width()
    backgroundHeight = backgroundPixbuf.get_height()
    
    if widget.state == gtk.STATE_NORMAL:
        if selectPageId == pageId:
            pixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
        else:
            pixbuf = None
    elif widget.state == gtk.STATE_PRELIGHT:
        if selectPageId == pageId:
            pixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(hoverImg)
    elif widget.state == gtk.STATE_ACTIVE:
        pixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
    
    x, y = widget.allocation.x, widget.allocation.y
    
    cr = widget.window.cairo_create()
    
    drawPixbuf(cr, pixbuf, x, y)

    navPixbuf = gtk.gdk.pixbuf_new_from_file(navImg)
    navWidth = navPixbuf.get_width()
    navHeight = navPixbuf.get_height()
    drawPixbuf(cr, navPixbuf, 
               x + (backgroundWidth - navWidth) / 2, 
               y)

    # Draw font.
    fontSize = 16
    
    drawFont(cr, navName, fontSize, "#FFFFFF",
             x + backgroundWidth / 2 - fontSize * 2, 
             y + (backgroundHeight + navHeight) / 2)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def updateButtonSetBackground(
    widget, 
    navName, navImg,
    hoverImg, pressImg,
    pageId, getPageId, getUpradableNum):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(hoverImg)
    requestWidth = image.get_width()
    requestHeight = image.get_height()
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: updateButtonOnExpose(
            w, e,
            navName, navImg,
            hoverImg, pressImg, 
            pageId, getPageId, getUpradableNum))
        
def updateButtonOnExpose(
    widget, event, 
    navName, navImg,
    hoverImg, pressImg,
    pageId, getPageId, getUpradableNum):
    '''Expose function to replace event box's image.'''
    # Init.
    selectPageId = getPageId()
    upgradableNum = getUpradableNum()
    
    # Draw background.
    backgroundPixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
    backgroundWidth = backgroundPixbuf.get_width()
    backgroundHeight = backgroundPixbuf.get_height()
    
    if widget.state == gtk.STATE_NORMAL:
        if selectPageId == pageId:
            pixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
        else:
            pixbuf = None
    elif widget.state == gtk.STATE_PRELIGHT:
        if selectPageId == pageId:
            pixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(hoverImg)
    elif widget.state == gtk.STATE_ACTIVE:
        pixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
    
    x, y = widget.allocation.x, widget.allocation.y
    
    cr = widget.window.cairo_create()
    
    drawPixbuf(cr, pixbuf, x, y)

    navPixbuf = gtk.gdk.pixbuf_new_from_file(navImg)
    navWidth = navPixbuf.get_width()
    navHeight = navPixbuf.get_height()
    drawPixbuf(cr, navPixbuf, 
               x + (backgroundWidth - navWidth) / 2, 
               y)
    
    # Draw upgradable number.
    if upgradableNum > 0 and upgradableNum < 100000:
        # Init.
        numBgLeftPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/navigate/notify_bg_left.png")
        numBgMiddlePixbuf = gtk.gdk.pixbuf_new_from_file("./icons/navigate/notify_bg_middle.png")
        numBgRightPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/navigate/notify_bg_right.png")
        numPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/navigate/0.png")
        numBgLeftWidth = numBgLeftPixbuf.get_width()      
        numBgLeftHeight = numBgLeftPixbuf.get_height()    
        numWidth = numPixbuf.get_width()                  
        numHeight = numPixbuf.get_height()                
        numLen = len(str(upgradableNum))        
        numX = x + backgroundWidth - numBgLeftWidth * 2 - numLen * numWidth - 10
        numY = y + 10
        
        # Draw number background.
        drawPixbuf(cr, numBgLeftPixbuf, numX, numY)
        drawPixbuf(cr, numBgMiddlePixbuf.scale_simple(numLen * numWidth, numBgLeftHeight, gtk.gdk.INTERP_BILINEAR),
                   numX + numBgLeftWidth, numY)
        drawPixbuf(cr, numBgRightPixbuf, 
                   numX + numBgLeftWidth + numLen * numWidth, numY)
        
        # Draw number.
        for (i, c) in enumerate(str(upgradableNum)):
            numPixbuf = gtk.gdk.pixbuf_new_from_file("./icons/navigate/%s.png" % c)
            drawPixbuf(cr, numPixbuf,
                       numX + numBgLeftWidth + i * numWidth,
                       numY + (numBgLeftHeight - numHeight) / 2)
    elif upgradableNum != 0:
        print "Upgradable number out of bound (1 ~ 100000): %s" % (upgradableNum)
    
    # Draw font.
    fontSize = 16

    drawFont(cr, navName, fontSize, "#FFFFFF",
             x + backgroundWidth / 2 - fontSize * 2, 
             y + (backgroundHeight + navHeight) / 2)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def sideButtonSetBackground(widget, 
                            navName, navImg,
                            normalImg, hoverImg, pressImg,
                            pageId, getPageId):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(hoverImg)
    widget.set_size_request(image.get_width(), image.get_height())
    
    widget.connect("expose-event", lambda w, e: sideButtonOnExpose(
            w, e,
            navName, navImg,
            normalImg, hoverImg, pressImg, 
            pageId, getPageId))
        
def sideButtonOnExpose(widget, event, 
                      navName, navImg,
                      normalImg, hoverImg, pressImg,
                      pageId, getPageId):
    '''Expose function to replace event box's image.'''
    selectPageId = getPageId()
    
    backgroundPixbuf = gtk.gdk.pixbuf_new_from_file(pressImg)
    backgroundWidth = backgroundPixbuf.get_width()
    backgroundHeight = widget.allocation.height
    
    if widget.state == gtk.STATE_NORMAL:
        if selectPageId == pageId:
            image = gtk.gdk.pixbuf_new_from_file(pressImg)
        else:
            image = gtk.gdk.pixbuf_new_from_file(normalImg)
    elif widget.state == gtk.STATE_PRELIGHT:
        if selectPageId == pageId:
            image = gtk.gdk.pixbuf_new_from_file(pressImg)
        else:
            image = gtk.gdk.pixbuf_new_from_file(hoverImg)
    elif widget.state == gtk.STATE_ACTIVE:
        image = gtk.gdk.pixbuf_new_from_file(pressImg)
        
    pixbuf = image.scale_simple(backgroundWidth, backgroundHeight, gtk.gdk.INTERP_BILINEAR)
    
    x, y = widget.allocation.x, widget.allocation.y
    fontSize = 14
    middlePadding = 14
    
    cr = widget.window.cairo_create()
    
    drawPixbuf(cr, pixbuf, x, y)
    offset = 20

    navPixbuf = gtk.gdk.pixbuf_new_from_file(navImg)
    navWidth = navPixbuf.get_width()
    navHeight = navPixbuf.get_height()
    drawPixbuf(cr,
               navPixbuf, 
               x + (backgroundWidth - navWidth - fontSize * 2 - middlePadding) / 2 - offset,
               y + (backgroundHeight - navHeight) / 2)
    
    drawFont(cr, navName, fontSize, "#505050",
             x + (backgroundWidth - navWidth - fontSize * 2 - middlePadding) / 2 + navWidth + middlePadding - offset,
             getFontYCoordinate(y, backgroundHeight, fontSize))

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawLine(widget, color,
             lineWidth, vertical=True, lineType=None):
    '''Draw line.'''
    if vertical:
        widget.set_size_request(lineWidth, -1)
    else:
        widget.set_size_request(-1, lineWidth)
    widget.connect("expose-event", lambda w, e: drawLineExpose(
            w, e, color, lineWidth, vertical, lineType))

def drawLineExpose(widget, event, color, lineWidth, vertical, lineType):
    '''Draw line.'''
    rect = widget.allocation
    
    cr = widget.window.cairo_create()
    cr.set_line_width(lineWidth)
    cr.set_source_rgb(*colorHexToCairo(color))
    
    if lineType in [LINE_TOP, LINE_BOTTOM]:
        xAdjust = 0
        yAdjust = 1
    elif lineType in [LINE_LEFT, LINE_RIGHT]:
        xAdjust = 1
        yAdjust = 0
    else:
        xAdjust = 0
        yAdjust = 0
    
    if vertical:
        cr.move_to(rect.x + xAdjust, rect.y)
        cr.rel_line_to(0, rect.height)
    else:
        cr.move_to(rect.x, rect.y + yAdjust)
        cr.rel_line_to(rect.width, 0)
        
    cr.stroke()
    
    return True

def listItemSetBackground(widget, normalImg, selectImg,
                          itemId, getSelectId):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    requestWidth = -1
    requestHeight = image.get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: listItemOnExpose(
            w, e,
            normalImg, selectImg,
            itemId, getSelectId))
        
def listItemOnExpose(widget, event, 
                     normalImg, selectImg,
                     itemId, getSelectId):
    '''Expose function to replace event box's image.'''
    currentId = getSelectId()
    if currentId == itemId:
        image = gtk.gdk.pixbuf_new_from_file(selectImg)
    else:
        image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    imageWidth = widget.allocation.width
    imageHeight = image.get_height()
    
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    rect = widget.allocation
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawBackground(widget, event, color, borderColor=None, borderWidth=3):
    '''Draw background.'''
    rect = widget.allocation

    cr = widget.window.cairo_create()
    cr.set_source_rgb(*colorHexToCairo(color))
    cr.rectangle(0, 0, rect.width, rect.height)
    cr.fill()
    
    if borderColor != None:
        cr.set_line_width(borderWidth)
        cr.set_source_rgb(*colorHexToCairo(borderColor))
        cr.rectangle(0, 0, rect.width, rect.height)
        cr.stroke()
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)
        
    return True

def drawRoundRectangle(cr, x, y, width, height, r):
    '''Draw round rectangle.'''
    cr.move_to(x + r, y);
    cr.line_to(x + width - r, y);

    cr.move_to(x + width, y + r);
    cr.line_to(x + width, y + height - r);

    cr.move_to(x + width - r, y + height);
    cr.line_to(x + r, y + height);

    cr.move_to(x, y + height - r);
    cr.line_to(x, y + r);

    cr.arc(x + r, y + r, r, pi, 3 * pi / 2.0);
    cr.arc(x + width - r, y + r, r, 3 * pi / 2, 2 * pi);
    cr.arc(x + width - r, y + height - r, r, 0, pi / 2);
    cr.arc(x + r, y + height - r, r, pi / 2, pi);
    
def checkButtonSetBackground(widget, scaleX, scaleY, normalImg, selectImg):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = image.get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = image.get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: checkButtonOnExpose(
            w, e,
            scaleX, scaleY,
            normalImg, selectImg))
        
def checkButtonOnExpose(widget, event, 
                        scaleX, scaleY,
                        normalImg, selectImg):
    '''Expose function to replace event box's image.'''
    if widget.get_active():
        image = gtk.gdk.pixbuf_new_from_file(selectImg)
    else:
        image = gtk.gdk.pixbuf_new_from_file(normalImg)
    
    if scaleX:
        imageWidth = widget.allocation.width
    else:
        imageWidth = image.get_width()
        
    if scaleY:
        imageHeight = widget.allocation.height
    else:
        imageHeight = image.get_height()
    
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def titlebarSetBackground(widget, leftImg, middleImg, rightImg):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(leftImg)
    
    requestHeight = image.get_height()
    
    widget.set_size_request(-1, requestHeight)
    
    widget.connect("expose-event", lambda w, e: titlebarOnExpose(
            w, e,
            leftImg, middleImg, rightImg))
        
def titlebarOnExpose(widget, event,
                     leftImg, middleImg, rightImg):
    '''Expose function to replace event box's image.'''
    x, y, width, height = widget.allocation.x, widget.allocation.y, widget.allocation.width, widget.allocation.height

    leftPixbuf = gtk.gdk.pixbuf_new_from_file(leftImg)
    rightPixbuf = gtk.gdk.pixbuf_new_from_file(rightImg)
    
    leftWidth = leftPixbuf.get_width()
    rightWidth = rightPixbuf.get_width()
    middleWidth = width - leftWidth - rightWidth
    
    middlePixbuf = gtk.gdk.pixbuf_new_from_file(middleImg).scale_simple(
        middleWidth,
        height,
        gtk.gdk.INTERP_BILINEAR)
    
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
    leftPixbuf.copy_area(0, 0, leftWidth, height, pixbuf, 0, 0)
    middlePixbuf.copy_area(0, 0, middleWidth, height, pixbuf, leftWidth, 0)
    rightPixbuf.copy_area(0, 0, rightWidth, height, pixbuf, width - rightWidth, 0)
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf, x, y)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def toggleTabSetBackground(widget, scaleX, scaleY, 
                           activeImg, inactiveImg,
                           activeContent, inactiveContent
                           ):
    '''Set event box's background.'''
    image = gtk.gdk.pixbuf_new_from_file(activeImg)
    
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = image.get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = image.get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: toggleTabOnExpose(
            w, e,
            scaleX, scaleY,
            activeImg, inactiveImg,
            activeContent, inactiveContent))
        
def toggleTabOnExpose(widget, event, 
                      scaleX, scaleY,
                      activeImg, inactiveImg,
                      activeContent, inactiveContent):
    '''Expose function to replace event box's image.'''
    if widget.get_active():
        image = gtk.gdk.pixbuf_new_from_file(activeImg)
        leftTabFontColor = "#FFFFFF"
        rightTabFontColor = "#333333"
    else:
        image = gtk.gdk.pixbuf_new_from_file(inactiveImg)
        leftTabFontColor = "#333333"
        rightTabFontColor = "#FFFFFF"
    
    if scaleX:
        imageWidth = widget.allocation.width
    else:
        imageWidth = image.get_width()
        
    if scaleY:
        imageHeight = widget.allocation.height
    else:
        imageHeight = image.get_height()
    
    x, y, width, height = widget.allocation.x, widget.allocation.y, widget.allocation.width, widget.allocation.height
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)
    
    fontSize = 14
    
    drawFont(cr, activeContent, fontSize, leftTabFontColor,
             x + (width / 2 - fontSize * 4) / 2, 
             getFontYCoordinate(y, height, fontSize))
    
    drawFont(cr, inactiveContent, fontSize, rightTabFontColor,
             x + width / 2 + (width / 2 - fontSize * 4) / 2, 
             getFontYCoordinate(y, height, fontSize))
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def colorHexToCairo(color):
    """ 
    Convert a html (hex) RGB value to cairo color. 
     
    @type color: html color string 
    @param color: The color to convert. 
    @return: A color in cairo format. 
    """ 
    if color[0] == '#': 
        color = color[1:] 
    (r, g, b) = (int(color[:2], 16), 
                    int(color[2:4], 16),  
                    int(color[4:], 16)) 
    return colorRGBToCairo((r, g, b)) 

def colorRGBToCairo(color): 
    """ 
    Convert a 8 bit RGB value to cairo color. 
     
    @type color: a triple of integers between 0 and 255 
    @param color: The color to convert. 
    @return: A color in cairo format. 
    """ 
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0) 

def drawTopbar(widget):
    '''Draw topbar.'''
    eventBoxSetBackground(
        widget,
        True, False,
        "./icons/topbar/background.png")

def drawButton(widget, iconPrefix, subDir="cell", scaleX=False, 
               buttonLabel=None, fontSize=None, labelColor=None):
    '''Draw button.'''
    buttonSetBackground(
        widget,
        scaleX, False,
        "./icons/%s/%s_normal.png" % (subDir, iconPrefix),
        "./icons/%s/%s_hover.png" % (subDir, iconPrefix),
        "./icons/%s/%s_press.png" % (subDir, iconPrefix),
        buttonLabel, fontSize, labelColor
        )
    
def drawSimpleButton(widget, img):
    '''Draw simple button.'''
    simpleButtonSetBackground(
        widget,
        False, False,
        "./icons/cell/%s.png" % (img)
        )
    
def drawListItem(widget, index, getSelectIndex, selectable=True):
    '''Draw list item.'''
    if selectable:
        selectImg = "./icons/cell/list_item_select.png"
    else:
        selectImg = "./icons/cell/list_item.png"
    try:
        listItemSetBackground(
            widget,
            "./icons/cell/list_item.png",
            selectImg,
            index, getSelectIndex
            )
    except Exception, e:
        print "Ignore exception in drawListItem."
    
def drawTitlebar(widget):
    '''Draw title bar.'''
    titlebarSetBackground(
        widget,
        "./icons/recommend/title_left.png",
        "./icons/recommend/title_middle.png",
        "./icons/recommend/title_right.png",
        )
    
def drawFont(cr, content, fontSize, fontColor, x, y):
    '''Draw font.'''
    if DEFAULT_FONT in getFontFamilies():
        cr.select_font_face(DEFAULT_FONT,
                            cairo.FONT_SLANT_NORMAL, 
                            cairo.FONT_WEIGHT_NORMAL)
    cr.set_source_rgb(*colorHexToCairo(fontColor))
    cr.set_font_size(fontSize)
    cr.move_to(x, y)
    cr.show_text(content)
    
def drawPixbuf(cr, pixbuf, x=0, y=0):
    '''Draw pixbuf.'''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint()

def drawProgressbar(width):
    '''Draw progressbar.'''
    return pb.Progressbar(
        width,
        "./icons/cell/download_bg_left.png",
        "./icons/cell/download_bg_middle.png",
        "./icons/cell/download_bg_right.png",
        "./icons/cell/download_fg_left.png",
        "./icons/cell/download_fg_middle.png",
        "./icons/cell/download_fg_right.png",
        )
    
