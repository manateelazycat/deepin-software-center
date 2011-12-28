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
from draw import *
import threading as td
import utils
import zipfile

(ARIA2_MAJOR_VERSION, ARIA2_MINOR_VERSION, _) = utils.getAria2Version()

class DownloadUpdateData(td.Thread):
    '''Download update data.'''
	
    def __init__(self):
        '''Init update data.'''
        td.Thread.__init__(self)
        self.setDaemon(True)

        self.autoSaveInterval = 10       # time to auto save progress, in seconds
        
    def run(self):
        '''Run'''
        self.downloadUpdateData()

    def downloadUpdateData(self):
        '''Download update data.'''
        cmdline = [
            'aria2c',
            "%s/softcenter/v1/soft?a=top&r=package" % (SERVER_ADDRESS),
            "--dir=" + UPDATE_DATA_DOWNLOAD_DIR,
            '--file-allocation=none',
            '--auto-file-renaming=false',
            '--summary-interval=0',
            '--remote-time=true',
            '--auto-save-interval=%s' % (self.autoSaveInterval),
            '--check-integrity=true',
            '--disable-ipv6=true',
            # '--max-overall-download-limit=10K', # for debug
            ]
        
        # Make software center can work with aria2c 1.9.x.
        if ARIA2_MAJOR_VERSION >= 1 and ARIA2_MINOR_VERSION <= 9:
            cmdline.append("--no-conf")
            cmdline.append("--continue")
        else:
            cmdline.append("--no-conf=true")
            cmdline.append("--continue=true")
            
        # Append proxy configuration.
        # proxyString = utils.parseProxyString()
        # if proxyString != None:
        #     cmdline.append("=".join(["--all-proxy", proxyString]))
        
        self.proc = subprocess.Popen(cmdline)
        self.proc.wait()
        
        # Remove directory if it exists.
        if os.path.exists(UPDATE_DATA_DIR):
            removeDirectory(UPDATE_DATA_DIR)
        
        # Extract zip file after download finish.
        if self.proc.returncode == 0:
            # Extract zip file.
            f = zipfile.ZipFile(os.path.join(UPDATE_DATA_DOWNLOAD_DIR, "updateData.zip"))
            f.extractall(UPDATE_DATA_DOWNLOAD_DIR)
            f.close()
            
        # Delete zip file.
        removeFile(os.path.join(UPDATE_DATA_DOWNLOAD_DIR, "updateData.zip"))
