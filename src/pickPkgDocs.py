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

from utils import *
import os

def pickPkgDocs(saveDir):
    '''Pick package docs.'''
    pkgDir = "../pkgData/pkgInfo/"
    for pkgFile in os.listdir(pkgDir):
        pkgPath = os.path.join(pkgDir, pkgFile)
        if os.path.exists(pkgPath):
            pkgInfo = ((evalFile(pkgPath))["zh_CN"])
            writeFile(os.path.join(saveDir, pkgFile), str(pkgInfo))
        print "Process %s done." % (pkgFile)
            
if __name__ == "__main__":
    pickPkgDocs(os.path.expanduser("~/pkgInfo"))
        
