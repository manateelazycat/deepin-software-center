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

import apt_pkg
import apt
import urllib2

def test():
    '''Test'''
    cache = apt.Cache()

    # for pkg in cache:
    #     if pkg.is_upgradable:
    #         pkg.mark_upgrade()
    #         print "* Upgrade package: %s" % (pkg.name)
    #         print "Current version: %s" % (pkg.installed.version)
    #         for version in pkg.versions:
    #             print "Other version: %s" % (version.version)
    
    # for pkg in cache:
    #     if pkg.is_installed:
    #         if pkg.essential:
    #             print "* ", pkg.name
    #         else:
    #             print pkg.name
    
    # for pkg in cache:
    #     print pkg.name
    
    connection = urllib2.urlopen("http://test-linux.gteasy.com/getComment.php?n=3270-common", timeout=20)
    print connection.read()
                
if __name__ == "__main__":
    test()
