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

import aptdaemon.client as client
import aptdaemon.enums as enums
import aptdaemon.errors as errors
import dbus.glib
import dbus.mainloop.glib
import gobject
import gtk
import signal
import sys
from utils import *
import threading as td
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

class CheckUpdate(td.Thread):
    """Check update."""
    def __init__(self, updateProgressCallback, finishCallback, allowUnauthenticated=False, details=False):
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        
        self.updateProgressCallback = updateProgressCallback
        self.finishCallback = finishCallback
        self.client = client.AptClient()
        self.signals = []
        signal.signal(signal.SIGINT, self.onCancelSignal)
        signal.signal(signal.SIGQUIT, self.onCancelSignal)
        self.status = ""
        self.percent = 0
        self.allowUnauthenticated = allowUnauthenticated
        self.transaction = None
        self.loop = gobject.MainLoop()

    def run(self):
        """Update cache"""
        self.client.update_cache(reply_handler=self.runTransaction, error_handler=self.onException)
        self.loop.run()

    def setTransaction(self, transaction):
        """Monitor the given transaction"""
        for handler in self.signals:
            gobject.source_remove(handler)
        self.transaction = transaction
        self.signals = []
        self.signals.append(transaction.connect("status-changed", self.onStatus))
        self.signals.append(transaction.connect("progress-changed", self.onProgress))
        self.signals.append(transaction.connect("finished", self.onExit))
        transaction.set_allow_unauthenticated(self.allowUnauthenticated)

    def onExit(self, trans, enum):
        """Callback for the exit state of the transaction"""
        if enum == enums.EXIT_FAILED:
            msg = "%s: %s\n%s\n\n%s" % (
                   _("ERROR"),
                   enums.get_error_string_from_enum(trans.error_code),
                   enums.get_error_description_from_enum(trans.error_code),
                   trans.error_details)
            print msg
        self.loop.quit()
        
        self.finishCallback()

    def onStatus(self, transaction, status):
        """Callback for the Status signal of the transaction"""
        self.status = enums.get_status_string_from_enum(status)
        self.updateProgressCallback(self.status, self.percent)

    def onProgress(self, transaction, percent):
        """Callback for the Progress signal of the transaction"""
        self.percent = percent
        if self.percent < 100:
            self.updateProgressCallback(self.status, self.percent)

    def stopCustomProgress(self):
        """Stop the spinner which shows non trans status messages."""
        pass

    def onCancelSignal(self, signum, frame):
        """Callback for a cancel signal."""
        if self.transaction and \
           self.transaction.status != enums.STATUS_SETTING_UP:
            self.transaction.cancel()
        else:
            self.loop.quit()

    def onException(self, error):
        """Error callback."""
        try:
            raise error
        except errors.PolicyKitError:
            msg = "%s %s\n\n%s" % (_("ERROR:"),
                                   _("You are not allowed to perform "
                                     "this action."),
                                   error.get_dbus_message())
        except dbus.DBusException:
            msg = "%s %s - %s" % (_("ERROR:"), error.get_dbus_name(),
                                  error.get_dbus_message())
        except:
            msg = str(error)
        self.loop.quit()
        sys.exit(msg)

    def runTransaction(self, trans):
        """Callback which runs a requested transaction."""
        self.setTransaction(trans)
        self.transaction.run(error_handler=self.onException, reply_handler=lambda: self.stopCustomProgress())
        
class TrayIcon:
    '''Tray icon.'''
	
    def __init__(self):
        '''Init tray icon.'''
        self.checker = None
        self.tooltipWindow = None
        self.tooltipPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("./trayIcon/window.png", 320, 70)
        
    def clickIcon(self):
        '''Click icon.'''
        pass
    
    def hoverIcon(self, *args):
        '''Hover icon.'''
        if self.tooltipWindow == None:
            self.tooltipWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.tooltipWindow.set_decorated(False)
            self.tooltipWindow.set_default_size(320, 70)
            self.tooltipWindow.set_opacity(0.8)
            self.tooltipWindow.connect("size-allocate", lambda w, a: self.updateShape(w, a))
            
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
        
    def updateProgress(self, status, percent):
        '''Update progress.'''
        print "%s %s" % (status, percent)
                
    def finishCheck(self):
        '''Finish check.'''
    	# gtk.main_quit()
        print "Finish"
    
    def main(self):
        '''Main.'''
        gtk.gdk.threads_init()        
        tryIcon = gtk.StatusIcon()
        tryIcon.set_from_file("./icons/icon/icon.ico")
        tryIcon.set_has_tooltip(True)
        tryIcon.set_visible(True)
        tryIcon.connect("activate", lambda w: self.clickIcon())
        tryIcon.connect("query-tooltip", self.hoverIcon)
        
        self.checker = CheckUpdate(self.updateProgress, self.finishCheck)
        self.checker.start()
        
        gtk.main()

if __name__ == "__main__":
    TrayIcon().main()
