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
from lang import __, getDefaultLanguage
from math import pi
from theme import *
from utils import *
import cairo
import gtk
import math
import os
import pango
import pangocairo
import progressbar as pb

def eventBoxSetBackground(widget, scaleX, scaleY, dPixbuf):
    '''Set event box's background.'''
    image = dPixbuf.getPixbuf()
    
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = image.get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = image.get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect_after(
        "expose-event", 
        lambda w, e: eventBoxOnExpose(
            w, e,
            scaleX, scaleY,
            dPixbuf))
        
def eventBoxOnExpose(widget, event, scaleX, scaleY, dPixbuf):
    '''Expose function to replace event box's image.'''
    image = dPixbuf.getPixbuf()
    
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

def buttonSetBackground(widget, scaleX, scaleY, normalDPixbuf, hoverDPixbuf, pressDPixbuf,
                        buttonLabel=None, fontSize=None, labelDColor=None):
    '''Set event box's background.'''
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = normalDPixbuf.getPixbuf().get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = normalDPixbuf.getPixbuf().get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    # Add button label if buttonLabel is not None.
    if buttonLabel != None and labelDColor != None:
        if fontSize == None:
            size = "medium"
        else:
            size = int (fontSize * 1000)
            
        dynamicSimpleLabel = DynamicSimpleLabel(
            widget,
            buttonLabel,
            appTheme.getDynamicColor(labelDColor),
            size,
            )
        label = dynamicSimpleLabel.getLabel()

        widget.add(label)
    
    widget.connect("expose-event", lambda w, e: buttonOnExpose(
            w, e,
            scaleX, scaleY,
            normalDPixbuf, hoverDPixbuf, pressDPixbuf))
        
def buttonOnExpose(widget, event, 
                   scaleX, scaleY,
                   normalDPixbuf, hoverDPixbuf, pressDPixbuf):
    '''Expose function to replace event box's image.'''
    if widget.state == gtk.STATE_NORMAL:
        image = normalDPixbuf.getPixbuf()
    elif widget.state == gtk.STATE_PRELIGHT:
        image = hoverDPixbuf.getPixbuf()
    elif widget.state == gtk.STATE_ACTIVE:
        image = pressDPixbuf.getPixbuf()
    
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

def simpleButtonSetBackground(widget, scaleX, scaleY, dPixbuf):
    '''Set event box's background.'''
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = dPixbuf.getPixbuf().get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = dPixbuf.getPixbuf().get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: simpleButtonOnExpose(
            w, e,
            scaleX, scaleY,
            dPixbuf))
        
def simpleButtonOnExpose(widget, event, 
                         scaleX, scaleY,
                         dPixbuf):
    '''Expose function to replace event box's image.'''
    image = dPixbuf.getPixbuf()
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
    hoverDPixbuf = appTheme.getDynamicPixbuf(hoverImg)
    
    requestWidth = hoverDPixbuf.getPixbuf().get_width()
    requestHeight = hoverDPixbuf.getPixbuf().get_height() 
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: navButtonOnExpose(
            w, e,
            navName, 
            appTheme.getDynamicPixbuf(navImg),
            appTheme.getDynamicPixbuf(hoverImg),
            appTheme.getDynamicPixbuf(pressImg),
            pageId, getPageId))
        
def navButtonOnExpose(widget, event, 
                      navName, 
                      navDPixbuf, hoverDPixbuf, pressDPixbuf,
                      pageId, getPageId):
    '''Expose function to replace event box's image.'''
    # Init.
    navPixbuf = navDPixbuf.getPixbuf()
    hoverPixbuf = hoverDPixbuf.getPixbuf()
    pressPixbuf = pressDPixbuf.getPixbuf()
    selectPageId = getPageId()
    
    # Draw background.
    backgroundWidth = pressPixbuf.get_width()
    backgroundHeight = pressPixbuf.get_height()
    
    if widget.state == gtk.STATE_NORMAL:
        if selectPageId == pageId:
            pixbuf = pressPixbuf
        else:
            pixbuf = None
    elif widget.state == gtk.STATE_PRELIGHT:
        if selectPageId == pageId:
            pixbuf = pressPixbuf
        else:
            pixbuf = hoverPixbuf
    elif widget.state == gtk.STATE_ACTIVE:
        pixbuf = pressPixbuf
    
    x, y = widget.allocation.x, widget.allocation.y
    
    cr = widget.window.cairo_create()
    
    drawPixbuf(cr, pixbuf, x, y)

    navWidth = navPixbuf.get_width()
    navHeight = navPixbuf.get_height()
    drawPixbuf(cr, navPixbuf, 
               x + (backgroundWidth - navWidth) / 2, 
               y)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawThemeIcon(widget, pixbuf, selectDPixbuf, hoverDColor, pressDColor, index, getIndex):
    '''Draw theme icon.'''
    widget.connect("expose-event", lambda w, e: themeIconOnExpose(
            w, e, pixbuf, selectDPixbuf,
            hoverDColor, pressDColor,
            index, getIndex))

def themeIconOnExpose(widget, event, pixbuf, selectDPixbuf, hoverDColor, pressDColor, index, getIndex):
    '''Expose function to theme icon.'''
    # Init.
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    # Draw pixbuf.
    drawPixbuf(cr, pixbuf, rect.x, rect.y)
    
    # Draw frame.
    if widget.state == gtk.STATE_ACTIVE or index == getIndex():
        # Draw select pixbuf.
        selectPixbuf = selectDPixbuf.getPixbuf()
        drawPixbuf(cr, selectPixbuf, rect.x + rect.width - selectPixbuf.get_width() - 3, rect.y + 3)
    if widget.state == gtk.STATE_PRELIGHT:
        # Draw Hover frame.
        cr.set_line_width(2)
        cr.set_source_rgb(*colorHexToCairo(hoverDColor.getColor()))
        cr.rectangle(rect.x + 1, rect.y + 1, rect.width - 2, rect.height - 2)
        cr.stroke()
    else:
        # Draw frame.
        cr.set_line_width(1)
        cr.set_source_rgb(*colorHexToCairo(pressDColor.getColor()))
        cr.rectangle(rect.x + 1, rect.y + 1, rect.width - 2, rect.height - 2)
        cr.stroke()

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def updateButtonSetBackground(
    widget, 
    navName, navImg,
    hoverImg, pressImg,
    pageId, getPageId, getUpradableNum):
    '''Set event box's background.'''
    requestWidth = appTheme.getDynamicPixbuf(hoverImg).getPixbuf().get_width()
    requestHeight = appTheme.getDynamicPixbuf(hoverImg).getPixbuf().get_height()
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: updateButtonOnExpose(
            w, e,
            navName, 
            appTheme.getDynamicPixbuf(navImg),
            appTheme.getDynamicPixbuf(hoverImg),
            appTheme.getDynamicPixbuf(pressImg),
            appTheme.getDynamicPixbuf("navigate/notify_bg_left.png"),
            appTheme.getDynamicPixbuf("navigate/notify_bg_middle.png"),
            appTheme.getDynamicPixbuf("navigate/notify_bg_right.png"),
            pageId, getPageId, getUpradableNum))
        
def updateButtonOnExpose(
    widget, event, 
    navName,
    navDPixbuf, hoverDPixbuf, pressDPixbuf,
    numBgLeftDPixbuf, numBgMiddleDPixbuf, numBgRightDPixbuf,
    pageId, getPageId, getUpradableNum):
    '''Expose function to replace event box's image.'''
    # Init.
    navPixbuf = navDPixbuf.getPixbuf()
    hoverPixbuf = hoverDPixbuf.getPixbuf()
    pressPixbuf = pressDPixbuf.getPixbuf()
    numBgLeftPixbuf = numBgLeftDPixbuf.getPixbuf()
    numBgMiddlePixbuf = numBgMiddleDPixbuf.getPixbuf()
    numBgRightPixbuf = numBgRightDPixbuf.getPixbuf()
    selectPageId = getPageId()
    upgradableNum = getUpradableNum()
    
    # Draw background.
    backgroundWidth = pressPixbuf.get_width()
    backgroundHeight = pressPixbuf.get_height()
    
    if widget.state == gtk.STATE_NORMAL:
        if selectPageId == pageId:
            pixbuf = pressPixbuf
        else:
            pixbuf = None
    elif widget.state == gtk.STATE_PRELIGHT:
        if selectPageId == pageId:
            pixbuf = pressPixbuf
        else:
            pixbuf = hoverPixbuf
    elif widget.state == gtk.STATE_ACTIVE:
        pixbuf = pressPixbuf
    
    x, y = widget.allocation.x, widget.allocation.y
    
    cr = widget.window.cairo_create()
    
    drawPixbuf(cr, pixbuf, x, y)

    navWidth = navPixbuf.get_width()
    navHeight = navPixbuf.get_height()
    drawPixbuf(cr, navPixbuf, 
               x + (backgroundWidth - navWidth) / 2, 
               y)
    
    # Draw upgradable number.
    if upgradableNum > 0 and upgradableNum < 100000:
        # Init.
        numPixbuf = appTheme.getDynamicPixbuf("navigate/0.png").getPixbuf()
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
            numPixbuf = appTheme.getDynamicPixbuf("navigate/%s.png" % c).getPixbuf()
            drawPixbuf(cr, numPixbuf,
                       numX + numBgLeftWidth + i * numWidth,
                       numY + (numBgLeftHeight - numHeight) / 2)
    elif upgradableNum != 0:
        print "Upgradable number out of bound (1 ~ 100000): %s" % (upgradableNum)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def sideButtonSetBackground(widget, 
                            navName, navImg,
                            normalImg, hoverImg, pressImg,
                            getCategoryNumCallback, pageId, getPageId):
    '''Set event box's background.'''
    (navTextWidth, _) = gtk.Label(navName).get_layout().get_pixel_size()
    middlePadding = 14
    navPixbufWidth = appTheme.getDynamicPixbuf(navImg).getPixbuf().get_width()
    widget.set_size_request(
        navTextWidth + middlePadding * 4 + navPixbufWidth,
        appTheme.getDynamicPixbuf(hoverImg).getPixbuf().get_height())
    
    widget.connect("expose-event", lambda w, e: sideButtonOnExpose(
            w, e,
            navName, 
            navTextWidth,
            appTheme.getDynamicColor("sideButton"),
            appTheme.getDynamicPixbuf(navImg),
            appTheme.getDynamicPixbuf(normalImg),
            appTheme.getDynamicPixbuf(hoverImg),
            appTheme.getDynamicPixbuf(pressImg),
            getCategoryNumCallback,
            pageId, getPageId))
        
def sideButtonOnExpose(widget, event, 
                       navName, navTextWidth, dColor,
                       navDPixbuf, normalDPixbuf, hoverDPixbuf, pressDPixbuf,
                       getCategoryNumCallback,
                       pageId, getPageId):
    '''Expose function to replace event box's image.'''
    # Init.
    fontSize = 14
    middlePadding = 14
    
    navPixbuf = navDPixbuf.getPixbuf()
    normalPixbuf = normalDPixbuf.getPixbuf()
    hoverPixbuf = hoverDPixbuf.getPixbuf()
    pressPixbuf = pressDPixbuf.getPixbuf()
    
    selectPageId = getPageId()
    
    backgroundWidth = widget.allocation.width
    backgroundHeight = widget.allocation.height
    
    if widget.state == gtk.STATE_NORMAL:
        if selectPageId == pageId:
            image = pressPixbuf
        else:
            image = normalPixbuf
    elif widget.state == gtk.STATE_PRELIGHT:
        if selectPageId == pageId:
            image = pressPixbuf
        else:
            image = hoverPixbuf
    elif widget.state == gtk.STATE_ACTIVE:
        image = pressPixbuf
        
    pixbuf = image.scale_simple(backgroundWidth, backgroundHeight, gtk.gdk.INTERP_BILINEAR)
    
    x, y = widget.allocation.x, widget.allocation.y
    
    cr = widget.window.cairo_create()
    
    # Draw background.
    drawPixbuf(cr, pixbuf, x, y)
    offset = 20

    # Draw nav icon.
    navWidth = navPixbuf.get_width()
    navHeight = navPixbuf.get_height()
    drawPixbuf(cr,
               navPixbuf, 
               x + middlePadding,
               y + (backgroundHeight - navHeight) / 2)
    
    
    # Init.
    if selectPageId == pageId:
        offsetX = 1
        upgradableNum = getCategoryNumCallback(navName)
        numPixbuf = appTheme.getDynamicPixbuf("navigate/0.png").getPixbuf()
        numbarPixbuf = appTheme.getDynamicPixbuf("category/numbar.png").getPixbuf()
        numBgLeftHeight = numbarPixbuf.get_height()    
        numWidth = numPixbuf.get_width()                  
        numHeight = numPixbuf.get_height()                
        numLen = len(str(upgradableNum))        
        numX = x + middlePadding + offsetX
        numY = y + (backgroundHeight + navHeight) / 2 - numBgLeftHeight
        
        # Draw number background.
        drawPixbuf(cr, numbarPixbuf, numX, numY)
        
        # Draw number.
        for (i, c) in enumerate(str(upgradableNum)):
            numPixbuf = appTheme.getDynamicPixbuf("navigate/%s.png" % c).getPixbuf()
            drawPixbuf(cr, numPixbuf,
                       numX + (navWidth - numLen * numWidth) / 2 + i * numWidth,
                       numY + (numBgLeftHeight - numHeight) / 2)

    # Draw font.
    color = dColor.getColor()
    drawFont(cr, navName, fontSize, color,
             x + navWidth + middlePadding * 2,
             getFontYCoordinate(y, backgroundHeight, fontSize))

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawAlphaLine(widget, daColor, lineWidth, vertical=True):
    '''Draw line.'''
    if vertical:
        widget.set_size_request(lineWidth, -1)
    else:
        widget.set_size_request(-1, lineWidth)
        
    widget.connect("expose-event", lambda w, e: drawAlphaLineExpose(
            w, e, daColor, lineWidth, vertical))

def drawAlphaLineExpose(widget, event, daColor, lineWidth, vertical):
    '''Draw line.'''
    rect = widget.allocation
    
    cr = widget.window.cairo_create()
    cr.set_line_width(lineWidth)
    cr.set_source_rgba(*alphaColorHexToCairo(daColor.getColorInfo()))
    
    if vertical:
        cr.move_to(rect.x, rect.y)
        cr.rel_line_to(0, rect.height)
    else:
        cr.move_to(rect.x, rect.y)
        cr.rel_line_to(rect.width, 0)
        
    cr.stroke()
    
    return True

def drawVerticalLine(widget, width):
    '''Draw vertical line.'''
    widget.set_size_request(width, -1)
    
    widget.connect(
        "expose-event", 
        lambda w, e: drawVerticalLineExpose(w, e))
    
def drawVerticalLineExpose(widget, event):
    '''Draw vertical line expose.'''
    pixbuf = appTheme.getDynamicPixbuf("skin/frame.png").getPixbuf()
    rect = widget.allocation
    cr = widget.window.cairo_create()
    
    drawPixbuf(
        cr, 
        pixbuf.scale_simple(rect.width, rect.height, gtk.gdk.INTERP_BILINEAR),
        rect.x,
        rect.y)
    
    return True

def drawHLine(widget, dColor):
    '''Draw horizontal line.'''
    widget.connect("expose-event", 
                   lambda w, e: drawHLineExpose(w, e, dColor))
    
def drawHLineExpose(widget, event, dColor):
    '''Draw horizontal line expose.'''
    color = dColor.getColor()
    rect = widget.allocation
    
    cr = widget.window.cairo_create()
    pixbuf = appTheme.getDynamicPixbuf("detail/pix.png").getPixbuf().scale_simple(rect.width, 1, gtk.gdk.INTERP_BILINEAR)
    drawPixbuf(cr, pixbuf, rect.x, rect.y)
    
    cr.stroke()

    return True

def drawLine(widget, dColor,
             lineWidth, vertical=True, lineType=None):
    '''Draw line.'''
    if vertical:
        widget.set_size_request(lineWidth, -1)
    else:
        widget.set_size_request(-1, lineWidth)
    widget.connect("expose-event", lambda w, e: drawLineExpose(
            w, e, dColor, lineWidth, vertical, lineType))

def drawLineExpose(widget, event, dColor, lineWidth, vertical, lineType):
    '''Draw line.'''
    color = dColor.getColor()
    rect = widget.allocation
    
    cr = widget.window.cairo_create()
    cr.set_line_width(lineWidth)
    cr.set_source_rgb(*colorHexToCairo(color))

    if lineType == LINE_LEFT:
        xAdjust = 1
        yAdjust = 0
    elif lineType == LINE_RIGHT:
        xAdjust = 0
        yAdjust = 0
    else:
        xAdjust = 0
        yAdjust = -1
    
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
    requestWidth = -1
    requestHeight = appTheme.getDynamicPixbuf(normalImg).getPixbuf().get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: listItemOnExpose(
            w, e,
            appTheme.getDynamicPixbuf(normalImg),
            appTheme.getDynamicPixbuf(selectImg),
            itemId, getSelectId))
        
def listItemOnExpose(widget, event, 
                     normalDPixbuf, selectDPixbuf,
                     itemId, getSelectId):
    '''Expose function to replace event box's image.'''
    normalPixbuf = normalDPixbuf.getPixbuf()
    selectPixbuf = selectDPixbuf.getPixbuf()
    
    currentId = getSelectId()
    if currentId == itemId:
        image = selectPixbuf
    else:
        image = normalPixbuf
    
    imageWidth = widget.allocation.width
    imageHeight = image.get_height()
    
    pixbuf = image.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_BILINEAR)
    rect = widget.allocation
    
    cr = widget.window.cairo_create()
    drawPixbuf(cr, pixbuf)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawSmallScreenshotBackground(widget, width, height, dPixbuf):
    '''Draw small screenshot background.'''
    widget.set_size_request(width, height)
    
    widget.connect("expose-event", lambda w, e: exposeSmallScreenshotBackground(w, e, dPixbuf))

def exposeSmallScreenshotBackground(widget, event, dPixbuf):
    '''Expose small screenshot background.'''
    cr = widget.window.cairo_create()
    rect = widget.allocation
    pixbuf = dPixbuf.getPixbuf()
    
    drawPixbuf(
        cr, pixbuf, 
        rect.x + (rect.width - pixbuf.get_width()) / 2, 
        rect.y + (rect.height - pixbuf.get_height()) / 2,
        )
        
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)
        
    return True

def drawBackground(widget, event, dColor, borderColor=None, borderWidth=3):
    '''Draw background.'''
    color = dColor.getColor()
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

def drawDetailItemBackground(widget):
    '''Draw detail item background.'''
    widget.connect(
        "expose-event", 
        lambda w, e: drawDetailItemBackgroundOnExpose(
            w, e,
            appTheme.getDynamicPixbuf("detail/left.png"),
            appTheme.getDynamicPixbuf("detail/middle.png"),
            appTheme.getDynamicPixbuf("detail/right.png"),
            ))

def drawDetailItemBackgroundOnExpose(
    widget, event,
    leftDPixbuf, middleDPixbuf, rightDPixbuf
    ):
    '''Draw detail item background.'''
    leftPixbuf = leftDPixbuf.getPixbuf()
    middlePixbuf = middleDPixbuf.getPixbuf()
    rightPixbuf = rightDPixbuf.getPixbuf()
    
    rect = widget.allocation
    x, y = rect.x, rect.y
    borderWidth, borderHeight = leftPixbuf.get_width(), leftPixbuf.get_height()
    middlePixbuf = middlePixbuf.scale_simple(rect.width - borderWidth * 2, borderHeight, gtk.gdk.INTERP_BILINEAR)

    cr = widget.window.cairo_create()
    drawPixbuf(cr, leftPixbuf, x, y)
    drawPixbuf(cr, middlePixbuf, x + borderWidth, y)
    drawPixbuf(cr, rightPixbuf, x + rect.width - borderWidth, y)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)
        
    return True

def drawRoundRectangle(cr, x, y, width, height, r):
    '''Draw round rectangle.'''
    cr.move_to(x + r, y)
    cr.line_to(x + width - r, y)

    cr.move_to(x + width, y + r)
    cr.line_to(x + width, y + height - r)

    cr.move_to(x + width - r, y + height)
    cr.line_to(x + r, y + height)

    cr.move_to(x, y + height - r)
    cr.line_to(x, y + r)

    cr.arc(x + r, y + r, r, pi, 3 * pi / 2.0)
    cr.arc(x + width - r, y + r, r, 3 * pi / 2, 2 * pi)
    cr.arc(x + width - r, y + height - r, r, 0, pi / 2)
    cr.arc(x + r, y + height - r, r, pi / 2, pi)

def drawFrame(cr, x, y, width, height):
    '''Draw frame.'''
    r = 4
    pixbuf = appTheme.getDynamicPixbuf("skin/frame.png").getPixbuf()
    
    drawPixbuf(cr, pixbuf.scale_simple(width - 2 * r, 1, gtk.gdk.INTERP_BILINEAR), x + r, y)
    
    drawPixbuf(cr, pixbuf.scale_simple(1, height - r, gtk.gdk.INTERP_BILINEAR), x + width - 1, y + r)
    
    drawPixbuf(cr, pixbuf.scale_simple(width - 2 * r, 1, gtk.gdk.INTERP_BILINEAR), x + r, y + height - 1)
    
    drawPixbuf(cr, pixbuf.scale_simple(1, height - r, gtk.gdk.INTERP_BILINEAR), x, y + r)
    
    drawPixbuf(cr, pixbuf, x + 2, y + 1)
    drawPixbuf(cr, pixbuf, x + 1, y + 2)

    drawPixbuf(cr, pixbuf, x + width - 2 - 1, y + 1)
    drawPixbuf(cr, pixbuf, x + width - 1 - 1, y + 2)
    
    drawPixbuf(cr, pixbuf, x + 2, y + height - 2)
    drawPixbuf(cr, pixbuf, x + 1, y + height - 3)

    drawPixbuf(cr, pixbuf, x + width - 3, y + height - 2)
    drawPixbuf(cr, pixbuf, x + width - 2, y + height - 3)
    
def drawNavigateFrame(cr, x, y, width, height):
    '''Draw round rectangle.'''
    r = 4
    pixbuf = appTheme.getDynamicPixbuf("skin/frame.png").getPixbuf()

    drawPixbuf(cr, pixbuf.scale_simple(width - 2 * r, 1, gtk.gdk.INTERP_BILINEAR), x + r, y)
    
    drawPixbuf(cr, pixbuf.scale_simple(1, height - r, gtk.gdk.INTERP_BILINEAR), x + width - 1, y + r)
    
    drawPixbuf(cr, pixbuf.scale_simple(width, 1, gtk.gdk.INTERP_BILINEAR), x, y + height - 1, 0.2)
    
    drawPixbuf(cr, pixbuf.scale_simple(1, height - r, gtk.gdk.INTERP_BILINEAR), x, y + r)
    
    drawPixbuf(cr, pixbuf, x + 2, y + 1)
    drawPixbuf(cr, pixbuf, x + 1, y + 2)

    drawPixbuf(cr, pixbuf, x + width - 2 - 1, y + 1)
    drawPixbuf(cr, pixbuf, x + width - 1 - 1, y + 2)

def drawStatusbarFrame(cr, x, y, width, height):
    '''Draw round rectangle.'''
    r = 4
    pixbuf = appTheme.getDynamicPixbuf("skin/frame.png").getPixbuf()
    
    drawPixbuf(cr, pixbuf.scale_simple(width, 1, gtk.gdk.INTERP_BILINEAR), x, y, 0.5)
    
    drawPixbuf(cr, pixbuf.scale_simple(1, height - r, gtk.gdk.INTERP_BILINEAR), x + width - 1, y)
    
    drawPixbuf(cr, pixbuf.scale_simple(width - 2 * r, 1, gtk.gdk.INTERP_BILINEAR), x + r, y + height - 1)
    
    drawPixbuf(cr, pixbuf.scale_simple(1, height - r, gtk.gdk.INTERP_BILINEAR), x, y)
    
    drawPixbuf(cr, pixbuf, x + 2, y + height - 2)
    drawPixbuf(cr, pixbuf, x + 1, y + height - 3)

    drawPixbuf(cr, pixbuf, x + width - 3, y + height - 2)
    drawPixbuf(cr, pixbuf, x + width - 2, y + height - 3)

def drawNavigateFrameLight(cr, x, y, width, height, r):
    '''Draw round rectangle.'''
    cr.move_to(x + r, y);
    cr.line_to(x + width - r, y);

    cr.move_to(x + width, y + r);
    cr.line_to(x + width, y + height);

    cr.move_to(x + width, y + height);
    cr.line_to(x, y + height);
    
    cr.move_to(x, y + height);
    cr.line_to(x, y + r);

    cr.arc(x + r, y + r, r, pi, 3 * pi / 2.0);
    cr.arc(x + width - r, y + r, r, 3 * pi / 2, 2 * pi);

def drawStatusbarFrameLight(cr, x, y, width, height, r):
    '''Draw round rectangle.'''
    cr.move_to(x, y);
    cr.line_to(x + width, y);
    
    cr.move_to(x + width, y);
    cr.line_to(x + width, y + height - r);

    cr.arc(x + width - r, y + height - r, r, 0, pi / 2);
    
    cr.move_to(x + width - r, y + height);
    cr.line_to(x + r, y + height);

    cr.arc(x + r, y + height - r, r, pi / 2, pi);
    
    cr.move_to(x, y + height - r);
    cr.line_to(x, y);
    
def checkButtonSetBackground(widget, scaleX, scaleY, normalImg, selectImg):
    '''Set event box's background.'''
    if scaleX:
        requestWidth = -1
    else:
        requestWidth = appTheme.getDynamicPixbuf(normalImg).getPixbuf().get_width()
        
    if scaleY:
        requestHeight = -1
    else:
        requestHeight = appTheme.getDynamicPixbuf(normalImg).getPixbuf().get_height()
    
    widget.set_size_request(requestWidth, requestHeight)
    
    widget.connect("expose-event", lambda w, e: checkButtonOnExpose(
            w, e,
            scaleX, scaleY,
            appTheme.getDynamicPixbuf(normalImg),
            appTheme.getDynamicPixbuf(selectImg)))
        
def checkButtonOnExpose(widget, event, 
                        scaleX, scaleY,
                        normalDPixbuf, selectDPixbuf):
    '''Expose function to replace event box's image.'''
    if widget.get_active():
        image = selectDPixbuf.getPixbuf()
    else:
        image = normalDPixbuf.getPixbuf()
    
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
    widget.set_size_request(
        -1, 
         appTheme.getDynamicPixbuf(leftImg).getPixbuf().get_height())
    
    widget.connect("expose-event", lambda w, e: titlebarOnExpose(
            w, e,
            appTheme.getDynamicPixbuf(leftImg),
            appTheme.getDynamicPixbuf(middleImg),
            appTheme.getDynamicPixbuf(rightImg),
            ))
        
def titlebarOnExpose(widget, event,
                     leftDPixbuf, middleDPixbuf, rightDPixbuf):
    '''Expose function to replace event box's image.'''
    leftPixbuf = leftDPixbuf.getPixbuf()
    middlePixbuf = middleDPixbuf.getPixbuf()
    rightPixbuf = rightDPixbuf.getPixbuf()
    
    x, y, width, height = widget.allocation.x, widget.allocation.y, widget.allocation.width, widget.allocation.height

    leftWidth = leftPixbuf.get_width()
    rightWidth = rightPixbuf.get_width()
    middleWidth = width - leftWidth - rightWidth
    
    middlePixbuf = middlePixbuf.scale_simple(
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

def alphaColorHexToCairo((color, alpha)):
    '''Alpha color hext to cairo color.'''
    (r, g, b) = colorHexToCairo(color)
    return (r, g, b, alpha)

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
        appTheme.getDynamicPixbuf("topbar/background.png"))

def drawButton(widget, iconPrefix, subDir="cell", scaleX=False,
               buttonLabel=None, fontSize=None, labelDColor=None):
    '''Draw button.'''
    buttonSetBackground(
        widget,
        scaleX, False,
        appTheme.getDynamicPixbuf("%s/%s_normal.png" % (subDir, iconPrefix)),
        appTheme.getDynamicPixbuf("%s/%s_hover.png" % (subDir, iconPrefix)),
        appTheme.getDynamicPixbuf("%s/%s_press.png" % (subDir, iconPrefix)),
        buttonLabel, fontSize, labelDColor
        )
    
def drawSimpleButton(widget, img):
    '''Draw simple button.'''
    simpleButtonSetBackground(
        widget,
        False, False,
        appTheme.getDynamicPixbuf("cell/%s.png" % (img))
        )
    
def drawListItem(widget, index, getSelectIndex, selectable=True):
    '''Draw list item.'''
    if selectable:
        selectImg = "cell/list_item_select.png"
    else:
        selectImg = "cell/list_item.png"
    try:
        listItemSetBackground(
            widget,
            "cell/list_item.png",
            selectImg,
            index, getSelectIndex
            )
    except Exception, e:
        print "Ignore exception in drawListItem."

def drawRecommendItem(widget, index, getSelectIndex):
    '''Draw list item.'''
    try:
        listItemSetBackground(
            widget,
            "recommend/list_item.png",
            "recommend/list_item.png",
            index, getSelectIndex
            )
    except Exception, e:
        print "Ignore exception in drawListItem."
    
def drawTitlebar(widget):
    '''Draw title bar.'''
    titlebarSetBackground(
        widget,
        "recommend/title_left.png",
        "recommend/title_middle.png",
        "recommend/title_right.png",
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
    
def drawPixbuf(cr, pixbuf, x=0, y=0, alpha=1.0):
    '''Draw pixbuf.'''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint_with_alpha(alpha)

def drawProgressbar(width):
    '''Draw progressbar.'''
    return pb.Progressbar(
        width,
        "cell/download_bg_left.png",
        "cell/download_bg_middle.png",
        "cell/download_bg_right.png",
        "cell/download_fg_left.png",
        "cell/download_fg_middle.png",
        "cell/download_fg_right.png",
        )
    
def drawProgressbarWithoutBorder(width):
    '''Draw progressbar without border.'''
    return pb.Progressbar(
        width,
        "cell/progress_bg_left.png",
        "cell/progress_bg_middle.png",
        "cell/progress_bg_right.png",
        "cell/progress_fg_left.png",
        "cell/progress_fg_middle.png",
        "cell/progress_fg_right.png",
        True
        )
    
def drawVScrollbar(scrolledWindow):
    '''Draw vertical scrollbar.'''
    vScrollbar = scrolledWindow.get_vscrollbar()
    vAdjust = scrolledWindow.get_vadjustment()
    vScrollbar.set_size_request(
        appTheme.getDynamicPixbuf("scrollbar/vscrollbar_bg.png").getPixbuf().get_width(), 
        -1)
    vScrollbar.connect(
        "expose-event", 
        lambda w, e: drawVScrollbarOnExpose(
            w, e, vAdjust,
            appTheme.getDynamicPixbuf("scrollbar/vscrollbar_bg.png"),
            appTheme.getDynamicPixbuf("scrollbar/vscrollbar_fg_top.png"),
            appTheme.getDynamicPixbuf("scrollbar/vscrollbar_fg_middle.png"),
            appTheme.getDynamicPixbuf("scrollbar/vscrollbar_fg_bottom.png"),
            ))
    
def drawVScrollbarOnExpose(
    widget, event, adjust,
    bgDPixbuf,
    fgTopDPixbuf,
    fgMiddleDPixbuf,
    fgBottomDPixbuf
    ):
    '''Draw vertical scrollbar.'''
    # Init.
    bgPixbuf = bgDPixbuf.getPixbuf()
    fgTopPixbuf = fgTopDPixbuf.getPixbuf()
    fgMiddlePixbuf = fgMiddleDPixbuf.getPixbuf()
    fgBottomPixbuf = fgBottomDPixbuf.getPixbuf()
    
    rect = widget.allocation
    lower = adjust.get_lower()
    upper = adjust.get_upper()
    value = adjust.get_value()
    pageSize = adjust.get_page_size()
    minHeight = fgTopPixbuf.get_height() + fgMiddlePixbuf.get_height() + fgBottomPixbuf.get_height()
    progressHeight = max(int(rect.height / (upper - lower) * rect.height), minHeight)    
    
    # Get cairo.
    cr = widget.window.cairo_create()
    
    # Draw background.
    bPixbuf = bgPixbuf.scale_simple(rect.width, rect.height, gtk.gdk.INTERP_BILINEAR)
    drawPixbuf(cr, bPixbuf, rect.x, rect.y)
    
    # Draw foreground.
    ftHeight = fgTopPixbuf.get_height()
    
    offsetY = rect.y + value * (rect.height - progressHeight) / (upper - lower - pageSize)
    drawPixbuf(cr, fgTopPixbuf, rect.x, offsetY)
    
    fmPixbuf = fgMiddlePixbuf.scale_simple(rect.width, progressHeight - ftHeight * 2 + 2, gtk.gdk.INTERP_BILINEAR)
    drawPixbuf(cr, fmPixbuf, rect.x, offsetY + ftHeight - 1)
    
    drawPixbuf(cr, fgBottomPixbuf, rect.x, offsetY + progressHeight - ftHeight)
    
    cr.fill()
    
    return True

def setDefaultClickableDynamicLabel(content, colorName, size=LABEL_FONT_SIZE, resetAfterClick=True):
    '''Set default clickable dynamic label.'''
    eventbox = gtk.EventBox()
    dLabel = DynamicLabel(
        eventbox,
        content,
        appTheme.getDynamicLabelColor(colorName),
        size,
        )
    label = dLabel.getLabel()
    eventbox.set_visible_window(False)
    eventbox.add(label)
    
    setClickableDynamicLabel(eventbox, dLabel, resetAfterClick)
    
    return (label, eventbox)

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
                
        textColor = appTheme.getDynamicColor("completionText").getColor()
        keywordColor = appTheme.getDynamicColor("completionKeyword").getColor()
                
        return map(lambda (preStr, matchStr, restStr, pkg): 
                   # Highlight keyword.
                   ["<span foreground='%s'>%s</span>" % (textColor, preStr) + "<span foreground='%s'><b>%s</b></span>" % (keywordColor, matchStr) + "<span foreground='%s'>%s</span>" % (textColor, restStr), pkg],
                   # Sorted candidates.
                   sorted(candidates, cmp=compareCandidates))
    
def updateShape(widget, allocation, radius):
    '''Update shape.'''
    if allocation.width > 0 and allocation.height > 0:
        # Init.
        w, h = allocation.width, allocation.height
        bitmap = gtk.gdk.Pixmap(None, w, h, 1)
        cr = bitmap.cairo_create()
        
        # Clear the bitmap
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        
        # Draw our shape into the bitmap using cairo
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        drawRoundRectangle(cr, 0, 0, w, h, radius)
        cr.fill()
        
        widget.shape_combine_mask(bitmap, 0, 0)

def drawNavigateBackground(widget, dPixbuf, dType, frameLightColor, bottomColor):
    '''Draw extend background.'''
    widget.set_size_request(-1, dPixbuf.getPixbuf().get_height())
    
    widget.connect_after(
        "expose-event", 
        lambda w, e: exposeNavigateBackground(w, e, dPixbuf, dType, frameLightColor, bottomColor))
    
def exposeNavigateBackground(widget, event, dPixbuf, dType, frameLightColor, bottomColor):
    '''Expose extend background.'''
    # Init.
    rect = widget.allocation
    w, h = widget.allocation.width, widget.allocation.height
    cr = widget.window.cairo_create()
    pixbuf = dPixbuf.getPixbuf()
    pixbufWidth = pixbuf.get_width()

    # Draw background.
    drawType = dType.getType()
    drawBarBackground(cr, pixbuf, drawType, rect)
    
    # Draw frame light.
    cr.set_line_width(1)
    cr.set_source_rgba(*alphaColorHexToCairo(frameLightColor.getColorInfo()))
    cr.set_operator(cairo.OPERATOR_OVER)
    drawNavigateFrameLight(cr, 1, 1, w - 2, h - 2, RADIUS)
    cr.stroke()
    
    # Draw frame.
    drawNavigateFrame(cr, 0, 0, w, h)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True
    
def drawStatusbarBackground(widget, dPixbuf, dType, frameLightColor, topColor):
    '''Draw extend background.'''
    widget.set_size_request(-1, dPixbuf.getPixbuf().get_height())
    
    widget.connect_after(
        "expose-event", 
        lambda w, e: exposeStatusbarBackground(w, e, dPixbuf, dType, frameLightColor, topColor))
    
def exposeStatusbarBackground(widget, event, dPixbuf, dType, frameLightColor, topColor):
    '''Expose extend background.'''
    # Init.
    rect = widget.allocation
    w, h = widget.allocation.width, widget.allocation.height
    cr = widget.window.cairo_create()
    pixbuf = dPixbuf.getPixbuf()
    pixbufWidth = pixbuf.get_width()

    # Draw background.
    drawType = dType.getType()
    drawBarBackground(cr, pixbuf, drawType, rect)
            
    # Draw frame light.
    cr.set_line_width(1)
    cr.set_source_rgba(*alphaColorHexToCairo(frameLightColor.getColorInfo()))
    cr.set_operator(cairo.OPERATOR_OVER)
    drawStatusbarFrameLight(cr, 1, 1, w - 2, h - 2, RADIUS)
    cr.stroke()
    
    # Draw frame.
    drawStatusbarFrame(cr, 0, 0, w, h)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawThemeSelectWindow(widget, backgroundPixbuf, frameLightColor):
    '''Draw theme select window.'''
    widget.connect("expose-event", 
                   lambda w, e: exposeDrawThemeSelectWindow(w, e, backgroundPixbuf, frameLightColor))
    
def exposeDrawThemeSelectWindow(widget, event, backgroundPixbuf, frameLightColor):
    '''Expose draw theme select window.'''
    # Init.
    rect = widget.allocation
    w, h = widget.allocation.width, widget.allocation.height
    cr = widget.window.cairo_create()
    pixbuf = backgroundPixbuf.getPixbuf()

    # Draw background.
    cr.set_source_pixbuf(pixbuf, 0, 0)
    cr.paint()
    
    # Draw frame light.
    cr.set_line_width(1)
    cr.set_source_rgba(*alphaColorHexToCairo(frameLightColor.getColorInfo()))
    cr.set_operator(cairo.OPERATOR_OVER)
    drawRoundRectangle(cr, 1, 1, w - 2, h - 2, RADIUS)
    cr.stroke()

    # Draw frame.
    drawFrame(cr, 0, 0, w, h)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True


def menuItemSetBackground(widget, 
                          hoverImg,
                          pageId, getPageId):
    '''Set event box's background.'''
    widget.connect("expose-event", lambda w, e: menuItemOnExpose(
            w, e,
            appTheme.getDynamicPixbuf(hoverImg),
            pageId, getPageId))
        
def menuItemOnExpose(widget, event, 
                     hoverDPixbuf,
                     pageId, getPageId):
    '''Expose function to replace event box's image.'''
    hoverPixbuf = hoverDPixbuf.getPixbuf()
    
    selectPageId = getPageId()
    
    image = None
    if widget.state in [gtk.STATE_PRELIGHT, gtk.STATE_ACTIVE]:
        image = hoverPixbuf
        
    if image != None:
        rect = widget.allocation
        pixbuf = image.scale_simple(rect.width, rect.height, gtk.gdk.INTERP_BILINEAR)
        cr = widget.window.cairo_create()
        drawPixbuf(cr, pixbuf, rect.x, rect.y)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawBarBackground(cr, pixbuf, drawType, rect):
    '''Draw bar background.'''
    w, h = rect.width, rect.height
    pixbufWidth = pixbuf.get_width()
    if drawType == DRAW_EXTEND:
        # Draw pixbuf.
        cr.set_source_pixbuf(pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR), 0, 0)
        cr.paint()
    # Loop.
    elif drawType == DRAW_LOOP:
        times = int(math.ceil(w / float(pixbufWidth)))
        for index in range(0, times):
            cr.set_source_pixbuf(pixbuf, pixbufWidth * index, 0)
            cr.paint()
    # Split from middle.
    else:
        # Get split data.
        (fillType, fillColor) = drawType        
        if fillType == DRAW_LEFT:
            # Draw extend color.
            cr.set_source_rgb(*colorHexToCairo(fillColor))
            cr.rectangle(0, 0, w - pixbufWidth, h)
            cr.fill()
            
            # Draw pixbuf.
            cr.set_source_pixbuf(pixbuf, w - pixbufWidth, 0)
            cr.paint()
        elif fillType == DRAW_RIGHT:
            # Draw extend color.
            cr.set_source_rgb(*colorHexToCairo(fillColor))
            cr.rectangle(pixbufWidth, 0, w - pixbufWidth, h)
            cr.fill()
            
            # Draw pixbuf.
            cr.set_source_pixbuf(pixbuf, 0, 0)
            cr.paint()
        else:
            splitWidth = fillType
            leftWidth = splitWidth
            rightWidth = pixbufWidth - splitWidth
            
            # Draw left pixbuf.
            leftPixbuf = pixbuf.subpixbuf(0, 0, leftWidth, h)
            cr.set_source_pixbuf(leftPixbuf, 0, 0)
            cr.paint()
            
            # Draw middle color.
            cr.set_source_rgb(*colorHexToCairo(fillColor))
            cr.rectangle(splitWidth, 0, w - pixbufWidth, h)
            cr.fill()
            
            # Draw right pixbuf.
            rightPixbuf = pixbuf.subpixbuf(splitWidth, 0, rightWidth, h)
            cr.set_source_pixbuf(rightPixbuf, w - rightWidth, 0)
            cr.paint()
            
def moreWindowOnExpose(widget, event, dPixbuf, frameLightColor):
    '''More window expose event callback.'''
    # Init.
    w, h = widget.allocation.width, widget.allocation.height
    cr = widget.window.cairo_create()
    
    # Draw background.
    drawPixbuf(cr, dPixbuf.getPixbuf(), 0, 0)
    
    # Draw frame light.
    cr.set_line_width(1)
    cr.set_source_rgba(*alphaColorHexToCairo(frameLightColor.getColorInfo()))
    cr.set_operator(cairo.OPERATOR_OVER)
    drawRoundRectangle(cr, 1, 1, w - 2, h - 2, POPUP_WINDOW_RADIUS)
    cr.stroke()
    
    # Draw frame.
    drawFrame(cr, 0, 0, w, h)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def exposeSmallScreenshot(widget, event, pixbuf, index, getIndex):
    '''Expose small screenshot.'''
    # Init.
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    # Draw pixbuf.
    if index == getIndex():
        alpha = 1.0
    else:
        alpha = 0.5
    drawPixbuf(
        cr, 
        pixbuf, 
        rect.x + (rect.width - pixbuf.get_width()) / 2, 
        rect.y + (rect.height - pixbuf.get_height()) / 2,
        alpha,
        )
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True
    
def setClickableCursor(widget):
    '''Set click-able cursor.'''
    # Use widget in lambda, and not widget pass in function.
    # Otherwise, if widget free before callback, you will got error:
    # free variable referenced before assignment in enclosing scope, 
    widget.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    widget.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
        
def setCursor(widget, cursorType):
    '''Set cursor.'''
    widget.window.set_cursor(gtk.gdk.Cursor(cursorType))
    
    return False

def setDefaultCursor(widget):
    '''Set default cursor.'''
    widget.window.set_cursor(None)
    
    return False

def setLabelEntryMarkup(label, hoverMarkup, selectMarkup, labelId, getCurrentId):
    '''Set label markup color.'''
    if labelId == getCurrentId():
        setMarkup(label, selectMarkup)
    else:
        setMarkup(label, hoverMarkup)    
        
def setLabelLeaveMarkup(label, normalMarkup, selectMarkup, labelId, getCurrentId):
    '''Set label markup color.'''
    if labelId == getCurrentId():
        setMarkup(label, selectMarkup)
    else:
        setMarkup(label, normalMarkup)    

def setClickableDynamicLabel(widget, dLabel, resetAfterClick=True):
    '''Set click-able label.'''
    # Set label markup.
    widget.connect("enter-notify-event", lambda w, e: dLabel.hoverLabel())
    widget.connect("leave-notify-event", lambda w, e: dLabel.normalLabel())
    
    # Set label cursor.
    widget.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    widget.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
    
    # Reset color when click widget.
    if resetAfterClick:
        widget.connect("button-press-event", lambda w, e: dLabel.normalLabel())
        
def setCustomizeClickableCursor(eventbox, widget, cursorDPixbuf):
    '''Set click-able cursor.'''
    eventbox.connect("enter-notify-event", lambda w, e: setCustomizeCursor(widget, cursorDPixbuf))
    eventbox.connect("leave-notify-event", lambda w, e: setDefaultCursor(widget))
        
def setCustomizeCursor(widget, cursorDPixbuf, x=0, y=0):
    '''Set cursor.'''
    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.display_get_default(),
                                            cursorDPixbuf.getPixbuf(),
                                            x, y))
    return False
    
def setMarkup(label, markup):
    '''Set markup.'''
    label.set_markup(markup)
    
    return False

def setDefaultRadioButton(content, status, setStatus, getStatus, updateRadioStatus):
    '''Set default toggle button.'''
    box = gtk.HBox()
    
    padding = 5
    radioEventBox = gtk.EventBox()
    radioEventBox.set_visible_window(False)
    selectDPixbuf = appTheme.getDynamicPixbuf("topbar/select.png")
    unselectDPixbuf = appTheme.getDynamicPixbuf("topbar/unselect.png")
    radioEventBox.set_size_request(selectDPixbuf.getPixbuf().get_width(), selectDPixbuf.getPixbuf().get_height())
    radioEventBox.connect("expose-event", lambda w, e: radioButtonOnExpose(
            w, e,
            selectDPixbuf, unselectDPixbuf,
            status, getStatus))
    radioEventBoxAlign = gtk.Alignment()
    radioEventBoxAlign.set(0.5, 0.5, 0.0, 0.0)
    radioEventBoxAlign.set_padding(padding, padding, padding, padding)
    radioEventBoxAlign.add(radioEventBox)
    box.pack_start(radioEventBoxAlign, True, True)
    
    label = gtk.Label()
    label.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, content))
    label.set_alignment(0.0, 0.5)
    box.pack_start(label, False, False)

    eventbox = gtk.EventBox()
    eventbox.add(box)
    eventbox.set_visible_window(False)
    eventbox.connect("button-press-event", lambda w, e: setStatus(status))
    eventbox.connect("button-press-event", lambda w, e: updateRadioStatus())
    eventbox.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    eventbox.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))

    return (eventbox, radioEventBox)

def radioButtonOnExpose(widget, event, selectDPixbuf, unselectDPixbuf, status, getStatus):
    '''Expose toggle button.'''
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    if (status == getStatus()):
        pixbuf = selectDPixbuf.getPixbuf()
    else:
        pixbuf = unselectDPixbuf.getPixbuf()
        
    drawPixbuf(cr, pixbuf, rect.x, rect.y)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def setIconLabelButton(content, normalDPixbuf, hoverDPixbuf, iconPadding):
    '''Set icon label button.'''
    iconBox = gtk.Button()
    pixbuf = normalDPixbuf.getPixbuf()
    (textWidth, _) = gtk.Label(content).get_layout().get_pixel_size()
    iconBox.set_size_request(pixbuf.get_width() + textWidth + iconPadding * 2, pixbuf.get_height())
    iconBox.connect("expose-event", 
                    lambda w, e: iconLabelButtonOnExpose(w, e, content, textWidth, normalDPixbuf, hoverDPixbuf, iconPadding))
    iconBox.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    iconBox.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
    
    return iconBox

def iconLabelButtonOnExpose(widget, event, content, textWidth, normalDPixbuf, hoverDPixbuf, iconPadding):
    '''Icon label button on expose.'''
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    if widget.state == gtk.STATE_NORMAL:
        pixbuf = normalDPixbuf.getPixbuf()
    elif widget.state == gtk.STATE_PRELIGHT:
        pixbuf = hoverDPixbuf.getPixbuf()
    elif widget.state == gtk.STATE_ACTIVE:
        pixbuf = hoverDPixbuf.getPixbuf()
    drawPixbuf(cr, pixbuf, rect.x + iconPadding, rect.y)
    
    fontSize = 14
    drawFont(cr, content, fontSize, appTheme.getDynamicColor("foreground").getColor(),
             rect.x + pixbuf.get_width() + iconPadding * 2, getFontYCoordinate(rect.y, rect.height, fontSize))
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def setNumButton(pageIndex, index, hoverDPixbuf, pressDPixbuf):
    '''Set num icon.'''
    numButton = gtk.Button()
    pixbuf = hoverDPixbuf.getPixbuf()
    numButton.connect("expose-event", lambda w, e: numButtonOnExpose(w, e, pageIndex, index, hoverDPixbuf, pressDPixbuf))
    numButton.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    numButton.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
    
    numLabel = gtk.Label()
    numLabel.set_markup("<span foreground='%s' size='%s'>%s</span>" % (
                        appTheme.getDynamicColor("index").getColor(),
                        LABEL_FONT_MEDIUM_SIZE, index))
    numButton.add(numLabel)

    return numButton

def numButtonOnExpose(widget, event, pageIndex, index, hoverDPixbuf, pressDPixbuf):
    '''Num button on expose.'''
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    if widget.state == gtk.STATE_NORMAL:
        if pageIndex == index:
            image = pressDPixbuf.getPixbuf()
        else:
            image = None
    elif widget.state == gtk.STATE_PRELIGHT:
        image = hoverDPixbuf.getPixbuf()
    elif widget.state == gtk.STATE_ACTIVE:
        image = pressDPixbuf.getPixbuf()
        
    if (image):
        if (index >= 10):
            drawPixbuf(cr, image, rect.x + 3, rect.y + 5)
        else:
            drawPixbuf(cr, image, rect.x, rect.y + 5)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def setHoverButton(normalDPixbuf, hoverDPixbuf):
    '''Set hover icon.'''
    hoverButton = gtk.Button()
    pixbuf = hoverDPixbuf.getPixbuf()
    hoverButton.connect("expose-event", lambda w, e: hoverButtonOnExpose(w, e, normalDPixbuf, hoverDPixbuf))
    hoverButton.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    hoverButton.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
    
    return hoverButton

def hoverButtonOnExpose(widget, event, normalDPixbuf, hoverDPixbuf):
    '''Hover button on expose.'''
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    if widget.state == gtk.STATE_NORMAL:
        image = normalDPixbuf.getPixbuf()
    elif widget.state == gtk.STATE_PRELIGHT:
        image = hoverDPixbuf.getPixbuf()
    elif widget.state == gtk.STATE_ACTIVE:
        image = normalDPixbuf.getPixbuf()
        
    drawPixbuf(cr, image, rect.x, rect.y)
    
    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

#  LocalWords:  scaleX imageWidth scaleY imageHeight pixbuf cr drawPixbuf
#  LocalWords:  buttonSetBackground normalImg hoverImg pressImg buttonLabel
#  LocalWords:  fontSize labelColor normalPixbuf hoverPixbuf pressPixbuf
#  LocalWords:  requestWidth requestHeight buttonOnExpose PRELIGHT normalColor
#  LocalWords:  simpleButtonSetBackground simpleButtonOnExpose hoverColor
#  LocalWords:  fontButtonSetBackground selectColor fontButtonOnExpose
