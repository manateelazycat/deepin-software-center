#!/usr/bin/env python
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

from constant import *
from draw import *
from utils import *
import apt
import apt_pkg
import glib
import gobject
import gtk
import os
import re
import signal
import socket
import stat
import subprocess
import sys
import threading as td
import urllib2
import urllib

def sendStatistics():
    '''Send statistics.'''
    # Send Mac address to server for statistics.
    try:
        userId = getUserID()
        args = {'a' : 'm', 'n' : userId}
        
        connection = urllib2.urlopen(
            "%s/softcenter/v1/analytics" % (SERVER_ADDRESS),
            data=urllib.urlencode(args),
            timeout=POST_TIMEOUT,
            )
        print connection.read()
        
        print "Send mac address %s success." % (userId)
    except Exception, e:
        print "Send mac address %s failed" % (userId)
        
class TrayIcon(object):
    '''Tray icon.'''
    
    TOOLTIP_WIDTH = 150
    TOOLTIP_HEIGHT = 50
    TOOLTIP_OFFSET_Y = 4
	
    def __init__(self):
        '''Init tray icon.'''
        self.trayIcon = None
        self.tooltipWindow = None
        self.times = 20
        self.ticker = 0
        self.interval = 100     # in milliseconds
        self.tooltipPixbuf = gtk.gdk.pixbuf_new_from_file("../icon/window.png")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # make sure socket port always work
        self.socket.bind(SOCKET_UPDATEMANAGER_ADDRESS)
        
        # Get updatable package number.
        self.updateNum = 0
        
    def redraw(self):
        '''Redraw.'''
        if self.ticker > 4:
            self.showTooltip()
        elif self.ticker > 0 and self.tooltipWindow != None:
            self.tooltipWindow.set_opacity(self.ticker * 0.2)
        elif self.tooltipWindow != None:
            self.tooltipWindow.hide_all()
            
        if self.ticker > 0 and not self.cursorInIcon():
            self.ticker -= 1
        
        return True
    
    def showTooltip(self):
        '''Show tooltip.'''
        # Clean widget first.
        containerRemoveAll(self.tooltipEventBox)
        
        # Draw.
        label = gtk.Label()
        label.set_markup("<span size='%s'>有%s个软件包可以升级</span>" % (LABEL_FONT_SIZE, self.updateNum))
        
        self.tooltipEventBox.add(label)
        self.tooltipWindow.show_all()
    
    def cursorInIcon(self):
        '''Whether cursor in area of icon.'''
        (iconScreen, rect, orientation) = self.trayIcon.get_geometry()
        (screen, cx, cy, mask) = gtk.gdk.display_get_default().get_pointer()
        
        return isInRect((cx, cy), (rect.x, rect.y, rect.width, rect.height))
    
    def showSoftwareCenter(self):
        '''Show software center.'''
        # Init.
        startup = False
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        
        try:
            # Software center is not running if address is not bind.
            s.bind(SOCKET_SOFTWARECENTER_ADDRESS)
            
            # Close socket.
            s.close()
            
            # Enable start flag.
            startup = True
        except Exception, e:
            print e
            
            # Just need send show update request if software center has running.
            s.sendto("showUpdate", SOCKET_SOFTWARECENTER_ADDRESS)  
            
            # Close socket.
            s.close()  
        
        # Exit update manager.
        self.exit()
        
        # Must startup software center after current loop exit.
        # Otherwise socket and other resources of current process will keep that 
        # make software center can't works correctly.
        if startup:
            subprocess.Popen(["gksu", "./deepin-software-center.py", "show-update"])
            
    def exit(self):
        '''Exit'''
        self.socket.close()
        
        gtk.main_quit()    
        
    def hoverIcon(self, *args):
        '''Hover icon.'''
        self.ticker = self.times
        if self.tooltipWindow == None:
            self.tooltipWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.tooltipWindow.set_decorated(False)
            self.tooltipWindow.set_default_size(self.TOOLTIP_WIDTH, self.TOOLTIP_HEIGHT)
            self.tooltipWindow.connect("size-allocate", lambda w, a: self.updateShape(w, a))
            
            self.tooltipEventBox = gtk.EventBox()
            self.tooltipEventBox.connect("button-press-event", lambda w, e: self.showSoftwareCenter())
            self.tooltipWindow.add(self.tooltipEventBox)
            
            glib.timeout_add(self.interval, self.redraw)

        (iconScreen, iconRect, orientation) = self.trayIcon.get_geometry()
        (screenWidth, screenHeight) = getScreenSize(self.trayIcon)
        tooltipX = iconRect.x - iconRect.width
        if iconRect.y + iconRect.height > screenHeight:
            tooltipY = iconRect.y - self.TOOLTIP_HEIGHT - self.TOOLTIP_OFFSET_Y 
        else:
            tooltipY = iconRect.y + iconRect.height + self.TOOLTIP_OFFSET_Y
        self.tooltipWindow.set_opacity(0.9)
        self.tooltipWindow.move(tooltipX, tooltipY)
        self.tooltipWindow.show_all()
        
    def updateShape(self, widget, allocation):
        '''Update shape.'''
        if allocation.width > 0 and allocation.height > 0:
            
            width, height = allocation.width, allocation.height
            
            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
            self.tooltipPixbuf.copy_area(0, 0, width, height, pixbuf, 0, 0)

            (_, mask) = pixbuf.render_pixmap_and_mask(255)
            if mask != None:
                self.tooltipWindow.shape_combine_mask(mask, 0, 0)
                
    @postGUI
    def finishCheck(self):
        '''Finish check.'''
        # Show detail information.
        self.hoverIcon()
        
    def handleRightClick(self, icon, button, time):
        menu = gtk.Menu()
        
        aboutIcon = gtk.Image()
        aboutIcon.set_from_file("../icon/about.png")
        aboutItem = gtk.ImageMenuItem()
        aboutItem.set_label("关于")
        aboutItem.set_image(aboutIcon)
        aboutItem.connect("activate", self.showAboutDialog)
        menu.append(aboutItem)
        
        quitIcon = gtk.Image()
        quitIcon.set_from_file("../icon/quit.png")
        quitItem = gtk.ImageMenuItem()
        quitItem.set_label("退出")
        quitItem.set_image(quitIcon)
        quitItem.connect("activate", lambda w: self.exit())
        menu.append(quitItem)
        
        menu.show_all()
        
        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.trayIcon)
        
    def showAboutDialog(self, widget):
        aboutDialog = gtk.AboutDialog()

        aboutDialog.set_destroy_with_parent(True)
        aboutDialog.set_name("深度Linux更新管理器")
        aboutDialog.set_version(VERSION)
        aboutDialog.set_authors(AUTHOR)
        aboutDialog.set_artists(ARTISTS)
        		
        aboutDialog.run()
        aboutDialog.destroy()        

    def calculateUpdateNumber(self):
        '''Calculate update number.'''
        apt_pkg.init()
        cache = apt.Cache()
        updateNum = 0
        ignorePkgs = evalFile("./ignorePkgs", True)
        for pkg in cache:
            if pkg.candidate != None and pkg.is_upgradable:
                if ignorePkgs == None or not pkg.name in ignorePkgs:
                    updateNum += 1
                
        return updateNum

    def main(self):
        '''Main.'''
        # Get input.
        if len(sys.argv) == 2 and sys.argv[1] == "--now":
            ignoreInterval = True
        else:
            ignoreInterval = False
        
        # Get last update hours.
        agoHours = getLastUpdateHours("./check-update-stamp")
        
        # Just update one day after.
        if ignoreInterval or (agoHours != None and agoHours >= UPDATE_INTERVAL):
            # Touch file to mark update stamp.
            touchFile("./check-update-stamp")
                
            # Send statistics information.
            AnonymityThread(sendStatistics).start()
            
            # Just show tray icon when have updatable packages.
            self.updateNum = self.calculateUpdateNumber()
            if self.updateNum > 0:
                print "Show tray icon."
                
                gtk.gdk.threads_init()        
                
                self.trayIcon = gtk.StatusIcon()
                self.trayIcon.set_from_file("../icon/icon.png")
                self.trayIcon.set_has_tooltip(True)
                self.trayIcon.set_visible(True)
                self.trayIcon.connect("activate", lambda w: self.showSoftwareCenter())
                self.trayIcon.connect("query-tooltip", self.hoverIcon)
                self.trayIcon.connect("popup-menu", self.handleRightClick)
                
                # Show tooltips.
                # Add timeout to make tooltip display at correct coordinate.
                glib.timeout_add_seconds(1, self.hoverIcon)
                
                gtk.main()
            else:
                print "No updatable packages, exit."
        else:
            print "Just check update %s hours ago" % (agoHours)
            
if __name__ == "__main__":
    TrayIcon().main()

#  LocalWords:  gksu polkit IP urllib urlopen postGUI finishCheck ip
#  LocalWords:  hoverIcon getLastUpdateHours mtime os agoHours
#  LocalWords:  handleRightClick aboutIcon aboutItem ImageMenuItem quitIcon
#  LocalWords:  showAboutDialog quitItem trayIcon aboutDialog AboutDialog
