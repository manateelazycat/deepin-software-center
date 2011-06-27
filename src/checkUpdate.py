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
from traceback import print_exc
from utils import *
import apt
import apt_pkg
import aptdaemon.client as client
import aptdaemon.enums as enums
import aptdaemon.errors as errors
import glib
import gobject
import gtk
import re
import signal
import socket
import stat
import sys
import threading as td
import urllib2

# Must init thread before any thread code running.
# Otherwise you will got segmentation fault about dbus_connection_get_dispatch_status, 
# because dbus.glib is not lock thread.
from dbus.mainloop.glib import threads_init
threads_init()

class CheckUpdate(td.Thread):
    """Check update."""
    def __init__(self, finishCallback, allowUnauthenticated=False, details=False):
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        
        self.finishCallback = finishCallback
        self.client = client.AptClient()
        signal.signal(signal.SIGINT, self.onCancelSignal)
        signal.signal(signal.SIGQUIT, self.onCancelSignal)
        self.status = ""
        self.percent = 0
        self.allowUnauthenticated = allowUnauthenticated
        self.transaction = None
        self.finish = False
        self.updateNum = 0
        
    def run(self):
        """Update cache"""
        self.client.update_cache(reply_handler=self.runTransaction, error_handler=self.onException)

    def onCancelSignal(self, signum, frame):
        """Callback for a cancel signal."""
        if self.transaction and self.transaction.status != enums.STATUS_SETTING_UP:
            self.transaction.cancel()

    def runTransaction(self, trans):
        """Callback which runs a requested transaction."""
        self.transaction = trans
        self.transaction.connect("status-changed", self.onStatusChanged)
        self.transaction.connect("progress-changed", self.onProgressChanged)
        self.transaction.connect("finished", self.onFinish)
        self.transaction.set_allow_unauthenticated(self.allowUnauthenticated)
        self.transaction.run()
        
    def onStatusChanged(self, trans, status):
        """Callback for the Status signal of the transaction"""
        self.status = enums.get_status_string_from_enum(status)

    def onProgressChanged(self, trans, percent):
        """Callback for the Progress signal of the transaction"""
        if percent < 100:
            self.percent = percent

    def onFinish(self, trans, enum):
        """Callback for the exit state of the transaction"""
        # Print error but don't stop.
        if enum == enums.EXIT_FAILED:
            msg = "%s: %s\n%s\n\n%s" % (
                   ("ERROR"),
                   enums.get_error_string_from_enum(trans.error_code),
                   enums.get_error_description_from_enum(trans.error_code),
                   trans.error_details)
            print msg
        
        # Calculate update number.
        self.percent = 99
        self.status = "计算可以升级的包"
        self.calculateUpdateNumber()
        
        # Finish callback.
        self.finish = True
        self.finishCallback()
            
    def onException(self, error):
        """Error callback."""
        sys.exit(error)

    def calculateUpdateNumber(self):
        '''Calculate update number.'''
        apt_pkg.init()
        cache = apt.Cache()
        for pkg in cache:
            if pkg.candidate != None and pkg.is_upgradable:
                self.updateNum += 1

class TrayIcon:
    '''Tray icon.'''
    
    TOOLTIP_WIDTH = 320
    TOOLTIP_HEIGHT = 70
    TOOLTIP_OFFSET_X = 10
    TOOLTIP_OFFSET_Y = 30
    PROGRESS_WIDTH = 200
	
    def __init__(self):
        '''Init tray icon.'''
        self.trayIcon = None
        self.tooltipWindow = None
        self.times = 20
        self.ticker = 0
        self.interval = 100     # in milliseconds
        self.tooltipPixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
            "./trayIcon/window.png", 
            self.TOOLTIP_WIDTH, 
            self.TOOLTIP_HEIGHT)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        self.socket.bind(SOCKET_UPDATEMANAGER_ADDRESS)
        
    def redraw(self):
        '''Redraw.'''
        if self.ticker > 4:
            if self.checker.finish:
                self.drawFinish()
            else:
                self.drawUpdating()
        elif self.ticker > 0 and self.tooltipWindow != None:
            self.tooltipWindow.set_opacity(self.ticker * 0.2)
        elif self.tooltipWindow != None:
            if self.checker.finish and self.checker.updateNum == 0:
                self.exit()
            else:
                self.tooltipWindow.hide_all()
            
        if self.ticker > 0 and not self.cursorInIcon():
            self.ticker -= 1
        
        return True
    
    def cursorInIcon(self):
        '''Whether cursor in area of icon.'''
        (iconScreen, rect, orientation) = self.trayIcon.get_geometry()
        (screen, cx, cy, mask) = gtk.gdk.display_get_default().get_pointer()
        
        return isInRect((cx, cy), (rect.x, rect.y, rect.width, rect.height))
        
    def drawFinish(self):
        '''Draw finish.'''
        # Clean widget first.
        containerRemoveAll(self.tooltipEventBox)
        
        # Draw.
        label = gtk.Label()
        if self.checker.updateNum == 0:
            label.set_markup("<span size='%s'>%s</span>" % (LABEL_FONT_SIZE, "你的系统已经是最新的了！ :)"))
        else:
            label.set_markup("<span size='%s'>有%s个软件包可以升级。</span>" % (LABEL_FONT_SIZE, self.checker.updateNum))
        
        self.tooltipEventBox.add(label)
        self.tooltipWindow.show_all()
    
    def drawUpdating(self):
        '''Draw updating.'''
        # Draw.
        self.progressbar.setProgress(self.checker.percent)
        self.progressStatus.set_markup(
            "<span size='%s'>(%s) %s</span>"
            % (LABEL_FONT_SIZE, str(self.checker.percent) + "%", self.checker.status))
        
        self.tooltipWindow.show_all()
        
    def showSoftwareCenter(self):
        '''Show software center.'''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        
        try:
            # Software center is not running if address is not bind.
            s.bind(SOCKET_SOFTWARECENTER_ADDRESS)
            
            # Close socket.
            s.close()
            
            # Create file showUpdate.
            if self.checker.finish and self.checker.updateNum > 0:
                runCommand("gksu ./deepin-show-update.py")
            else:
                runCommand("gksu ./deepin-software-center.py")
        except Exception, e:
            print e
            
            # Just need send show update request if software center has running.
            if self.checker.finish and self.checker.updateNum > 0:
                s.sendto("show update request", SOCKET_SOFTWARECENTER_ADDRESS)  
            
            # Close socket.
            s.close()  
        
        # Quit.
        if self.checker.finish:
            self.exit()
            
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
            
            self.progressbarBox = gtk.VBox()
            self.progressbarAlign = gtk.Alignment()
            self.progressbarAlign.set(0.5, 0.5, 0.0, 0.0)
            self.progressbarAlign.add(self.progressbarBox)
            self.tooltipEventBox.add(self.progressbarAlign)
            
            self.progressbar = drawProgressbar(self.PROGRESS_WIDTH)
            self.progressbarBox.pack_start(self.progressbar.box)
            
            self.progressStatus = gtk.Label()
            self.progressStatus.set_alignment(0.0, 0.5)
            self.progressbarBox.pack_start(self.progressStatus)
            
            glib.timeout_add(self.interval, self.redraw)
            
        self.tooltipWindow.set_opacity(0.9)
        self.tooltipWindow.move(gtk.gdk.screen_width() - self.TOOLTIP_WIDTH - self.TOOLTIP_OFFSET_X, self.TOOLTIP_OFFSET_Y)
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
                
    def getMyIP(self):
        '''Get my IP.'''
        return re.search('\d+\.\d+\.\d+\.\d+',urllib2.urlopen("http://www.whereismyip.com").read()).group(0)
        
    @postGUI
    def finishCheck(self):
        '''Finish check.'''
        # Show detail information.
        self.hoverIcon()
        
        # Send IP information to server for statistics.
        try:
            myIP = self.getMyIP()
            connection = urllib2.urlopen("http://test-linux.gteasy.com/record.php?i=" + str(myIP), timeout=POST_TIMEOUT)
            print "Send ip %s success." % (myIP)
        except Exception, e:
            print "Send ip %s failed" % (myIP)
        
    def getLastUpdateHours(self):
        """
        Return the number of hours since the last successful apt-get update
        
        If the date is unknown, return "None"
        """
        if not os.path.exists("/var/lib/apt/periodic/update-success-stamp"):
            return None
        # calculate when the last apt-get update (or similar operation) was performed.
        mtime = os.stat("/var/lib/apt/periodic/update-success-stamp")[stat.ST_MTIME]
        agoHours = int((time.time() - mtime) / (60 * 60))
        return agoHours
  
    def main(self):
        '''Main.'''
        # Get last update hours.
        agoHours = self.getLastUpdateHours()
        
        # Just update one day after.
        if agoHours != None and agoHours >= UPDATE_INTERVAL:
            print "Update package list..."
            
            gtk.gdk.threads_init()        
            
            self.trayIcon = gtk.StatusIcon()
            self.trayIcon.set_from_file("./icons/icon/icon.ico")
            self.trayIcon.set_has_tooltip(True)
            self.trayIcon.set_visible(True)
            self.trayIcon.connect("activate", lambda w: self.showSoftwareCenter())
            self.trayIcon.connect("query-tooltip", self.hoverIcon)
            
            self.checker = CheckUpdate(self.finishCheck)
            self.checker.start()
            
            gtk.main()
        else:
            print "Just update system %s hours ago" % (agoHours)

if __name__ == "__main__":
    TrayIcon().main()

