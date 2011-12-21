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
import apt
import apt.progress.base as apb
import os
import subprocess
import threading as td
import utils

class InstallProgress(apb.InstallProgress):
    '''Install progress.'''

    def __init__(self, pkgName, actionType, pkgList,
                 updateCallback):
        '''Init for install progress.'''
        apb.InstallProgress.__init__(self)

        # Init.
        self.pkgName = pkgName
        self.actionType = actionType
        self.pkgList = pkgList

        # Init callback.
        self.updateCallback = updateCallback
        
    def conffile(self, current, new):
        print "conffile prompt: %s %s" % (current, new)

    def error(self, errorstr):
        print "got dpkg error: '%s'" % errorstr

    def start_update(self):
        '''Start update.'''
        if self.actionType == ACTION_INSTALL:
            self.updateCallback(self.actionType, self.pkgName, 0, __("Action Install Start"))
        elif self.actionType == ACTION_UPGRADE:
            self.updateCallback(self.actionType, self.pkgName, 0, __("Action Update Start"))
        elif self.actionType == ACTION_UNINSTALL:
            self.updateCallback(self.actionType, self.pkgName, 0, __("Action Uninstall Start"))

    def status_change(self, pkg, percent, status):
        '''Progress status change.'''
        self.updateCallback(self.actionType, self.pkgName, int(percent), status)

class Action(td.Thread):
    '''Action.'''

    def __init__(self, pkgName, actionType, updateCallback, 
                 finishCallback, failedCallback, scanCallback,
                 messageCallback):
        '''Init for action.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 

        # Init cache and un-mark all packages.
        self.cache = apt.Cache()
        self.cache.clear()
        self.pkgName = pkgName
        self.actionType = actionType
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback
        self.failedCallback = failedCallback
        self.scanCallback = scanCallback
        self.messageCallback = messageCallback

        # Analysis dependent packages.
        if actionType == ACTION_INSTALL:
            self.cache[pkgName].mark_install()
        elif actionType == ACTION_UPGRADE:
            self.cache[pkgName].mark_upgrade()
        elif actionType == ACTION_UNINSTALL:
            self.cache[pkgName].mark_delete()

        pkgs = sorted(self.cache.get_changes(), key=lambda p: p.name)
        self.pkgList = map (lambda pkg: (pkg.name, pkg.marked_delete), pkgs)

        # Init progress.
        self.progress = InstallProgress(pkgName, actionType, self.pkgList, updateCallback)

    def run(self):
        '''Run'''
        
        try:
            # Commit apt changes.
            self.cache.commit(None, self.progress)
            
            # Call finish callback if action commit successfully.
            self.finish()
        except Exception, e:
            print "Got error `%s` when commit apt action." % (str(e))
            
            self.messageCallback("%s: %s" % (self.pkgName, __("Action Install Failed")))
            
            # Call failed callback.
            self.failed()
        
        # Debug, just for emulate install.
        # self.finish()
            
    # NOTE: Don't use interface `finish_update` in apt.progress.base.InstallProgress.
    # Because interface `finish_update` got finish signal *BEFORE* function `cache.commit`,
    # so interface `finish_update` can't handle error when exception throw.
    # Right way should follow this function after `cache.commit` then wrap in try...except block.
    def finish(self):
        '''Progress finish update.'''
        if self.actionType == ACTION_INSTALL:
            self.updateCallback(self.actionType, self.pkgName, 100, __("Action Install Finish"))
        elif self.actionType == ACTION_UPGRADE:
            self.updateCallback(self.actionType, self.pkgName, 100, __("Action Update Finish"))
        elif self.actionType == ACTION_UNINSTALL:
            self.updateCallback(self.actionType, self.pkgName, 100, __("Action Uninstall Finish"))
        
        self.scanCallback(self.pkgName, self.actionType)
        self.finishCallback(self.actionType, self.pkgList)
        
    def failed(self):
        '''Action failed.'''
        if self.actionType == ACTION_INSTALL:
            self.updateCallback(self.actionType, self.pkgName, 100, __("Action Install Failed"))
        elif self.actionType == ACTION_UPGRADE:
            self.updateCallback(self.actionType, self.pkgName, 100, __("Action Update Failed"))
        elif self.actionType == ACTION_UNINSTALL:
            self.updateCallback(self.actionType, self.pkgName, 100, __("Action Uninstall Failed"))
        
        self.scanCallback(self.pkgName, self.actionType)
        self.failedCallback(self.actionType, self.pkgName)
        
class ActionQueue(object):
    '''Action queue.'''

    def __init__(self, updateCallback, finishCallback, failedCallback, messageCallback):
        '''Init for action queue.'''
        # Init.
        self.lock = False
        self.queue = []
        self.pkgName = None
        self.actionType = None
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback
        self.failedCallback = failedCallback
        self.messageCallback = messageCallback

    def startActionThread(self, pkgName, actionType):
        '''Start action thread.'''
        # Lock first.
        self.lock = True
        
        # Init.
        self.pkgName = pkgName
        self.actionType = actionType

        # Start action.
        action = Action(pkgName, actionType,
                        self.updateCallback,
                        self.finishCallback,
                        self.failedCallback,
                        self.finishAction,
                        self.messageCallback)
        action.start()

    def addAction(self, pkgName, actionType):
        '''Add new action.'''
        # Add to queue if action is lock.
        if self.lock:
            self.queue.append((pkgName, actionType))
        # Otherwise start action thread.
        else:
            self.startActionThread(pkgName, actionType)

    def finishAction(self, pkgName, actionType):
        '''Finish action, start new action if have action in queue.'''
        # Remove finish action.
        utils.removeFromList(self.queue, (pkgName, actionType))

        # Start new action if queue has other request.
        if len(self.queue) > 0:
            (newPkgName, newActionType) = self.queue.pop(0)

            self.startActionThread(newPkgName, newActionType)
        # Otherwise release lock.
        else:
            self.lock = False
            self.pkgName = None
            self.actionType = None

    def getActionPkgs(self):
        '''Get action packages.'''
        if self.pkgName == None:
            return map (lambda (pn, _): pn, self.queue)
        else:
            return [self.pkgName] + (map (lambda (pn, _): pn, self.queue))

    def getActionQueue(self):
        '''Get action queue.'''
        if self.pkgName == None:
            return map (lambda action: action, self.queue)
        else:
            return [(self.pkgName, self.actionType)] + (map (lambda action: action, self.queue))
