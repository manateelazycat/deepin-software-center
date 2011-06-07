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

def pickCategory():
    '''Pick category.'''
    # Get input file.
    inputPkgs = sys.argv[1]

    # Get local packages list.
    cache = apt.Cache()
    pkgs = []
    for pkg in cache:
        pkgs.append(pkg.name)
        
    # Category dictionary.
    cateDict = {}
    
    # Pick packages.
    for line in open(inputPkgs).readlines():
        pkgName = line.rstrip("\n")
        if pkgName in pkgs:
            pkg = cache[pkgName]
            if pkg.candidate != None:
                pkgSection = pkg.candidate.section
                splitResult = pkgSection.split('/')
                if len (splitResult) == 2:
                    section = splitResult[1]
                else:
                    section = pkgSection
                    
                if cateDict.has_key(section):
                    cateDict[section].append(pkgName)
                else:
                    cateDict[section] = []
            else:
                if cateDict.has_key("unknown"):
                    cateDict["unknown"].append(pkgName)
                else:
                    cateDict["unknown"] = []
        else:
            if cateDict.has_key("unknown"):
                cateDict["unknown"].append(pkgName)
            else:
                cateDict["unknown"] = []
                
    # Print result.
    for category in cateDict.keys():
        print "*** ", category
        for pkgName in cateDict[category]:
            print pkgName
        print "\n"
    
if __name__ == "__main__":
    pickCategory()
    
