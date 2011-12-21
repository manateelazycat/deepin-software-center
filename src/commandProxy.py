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
from utils import *
import socket
import subprocess
import sys

class CommandProxy:
    '''Command proxy.'''
	
    def __init__(self):
        '''Init command proxy.'''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # make sure socket port always work
        self.socket.bind(SOCKET_COMMANDPROXY_ADDRESS)
        
        self.noExit = len(sys.argv) == 2 and sys.argv[1] == "--daemon"
        
        self.run()
        
    def run(self):
        '''Run.'''
        print "* Command proxy listen ..."
        cmd, addr = self.socket.recvfrom(2048)
        print "* Command proxy received: '%s' from %s" % (cmd, addr)
        if cmd != "exit":
            try:
                runCommand(cmd)
            except Exception, e:
                print "Got error `%s` when execute `%s`." % (e, cmd)    
            finally:
                self.run()
        elif self.noExit:
            self.run()
                
        print "* Command proxy exit."
    
if __name__ == "__main__":
    CommandProxy()
