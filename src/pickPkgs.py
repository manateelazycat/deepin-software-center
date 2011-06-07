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

import apt
import sys

def pickPkgs():
    '''Pick packages that available in local system.'''
    # Get input file.
    inputPkgs = sys.argv[1]

    # Get local packages list.
    cache = apt.Cache()
    pkgs = []
    for pkg in cache:
        pkgs.append(pkg.name)
    
    # Print available packages.
    print "*** Available packages:\n"
    for line in open(inputPkgs).readlines():
        pkgName = line.rstrip("\n")
        if pkgName in pkgs:
            print pkgName
    
    # Print Unknown packages.
    print "\n*** Unknown packages:\n"
    for line in open(inputPkgs).readlines():
        pkgName = line.rstrip("\n")
        if not pkgName in pkgs:
            print pkgName
    
if __name__ == "__main__":
    pickPkgs()
    
