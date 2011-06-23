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
import signal
import sys
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

class CheckUpdate:
    """Check update."""
    def __init__(self, allowUnauthenticated=False, details=False):
        self.client = client.AptClient()
        self.signals = []
        signal.signal(signal.SIGINT, self.onCancelSignal)
        signal.signal(signal.SIGQUIT, self.onCancelSignal)
        self.status = ""
        self.percent = 0
        self.allowUnauthenticated = allowUnauthenticated
        self.transaction = None
        self.loop = gobject.MainLoop()

    def updateCache(self):
        """Update cache"""
        self.client.update_cache(reply_handler=self.runTransaction, error_handler=self.onException)

    def run(self):
        """Start the console client application."""
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
        print "Finish"
        if enum == enums.EXIT_FAILED:
            msg = "%s: %s\n%s\n\n%s" % (
                   _("ERROR"),
                   enums.get_error_string_from_enum(trans.error_code),
                   enums.get_error_description_from_enum(trans.error_code),
                   trans.error_details)
            print msg
        self.loop.quit()

    def onStatus(self, transaction, status):
        """Callback for the Status signal of the transaction"""
        self.status = enums.get_status_string_from_enum(status)
        print self.status

    def onProgress(self, transaction, percent):
        """Callback for the Progress signal of the transaction"""
        self.percent = percent
        if self.percent < 100:
            print self.percent

    def stopCustomProgress(self):
        """Stop the spinner which shows non trans status messages."""
        print "Stop customize progress."

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

def main():
    """Run a command line client for aptdaemon"""
    checker = CheckUpdate()
    checker.updateCache()
    checker.run()

if __name__ == "__main__":
    main()
