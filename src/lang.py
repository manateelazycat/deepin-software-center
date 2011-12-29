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

import gettext
import locale

DEFAULT_LANG = None             # automatically
# DEFAULT_LANG = "default"        # english
# DEFAULT_LANG = "zh_CN"          # simple chinese
# DEFAULT_LANG = "zh_TW"          # transitional chinese

if DEFAULT_LANG == None:
    (lang, _) = locale.getdefaultlocale()
    if lang in ["zh_CN", "zh_TW", "zh_HK"]:
        if lang == "zh_HK":
            __ = gettext.translation('deepin-software-center', '../locale', languages=["zh_TW"]).gettext
        else:
            __ = gettext.translation('deepin-software-center', '../locale', languages=[lang]).gettext
    else:
        __ = gettext.translation('deepin-software-center', '../locale', languages=["default"]).gettext
else:    
    __ = gettext.translation('deepin-software-center', '../locale', languages=[DEFAULT_LANG]).gettext

def getDefaultLanguage():
    '''Get default language.'''
    (lang, _) = locale.getdefaultlocale()
    if lang in ["zh_CN", "zh_TW", "zh_HK"]:
        if DEFAULT_LANG == None:
            if lang == "zh_HK":
                return "zh_TW"
            else:
                return lang
        else:
            return DEFAULT_LANG
    else:
        return "default"

