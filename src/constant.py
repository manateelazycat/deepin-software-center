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

import sortedDict

CATE_ALL = "全部"
CATE_WEB = "网络"
CATE_SYSTEM = "系统"
CATE_BEAUTY = "美化"
CATE_MULTIMEDIA = "影音"
CATE_GAME = "游戏"
CATE_GRAPHICS = "图形"
CATE_OFFICE = "办公"
CATE_DESKTOP = "桌面"
CATE_PROJECT = "工程"
CATE_DEVELOP = "开发"
CATE_OTHERS = "其他"

SUBCATE_ALL = "全部"
SUBCATE_MAIL = "邮件"
SUBCATE_WEB = "网络"
SUBCATE_NEWS = "新闻"
SUBCATE_OTHERS = "其他"

SUBCATE_ADMIM = "系统管理"

SUBCATE_FONT = "字体"

SUBCATE_VIDEO = "视频"
SUBCATE_SOUND = "音频"

SUBCATE_GAME = "游戏"

SUBCATE_GRAPHICS = "图形"

SUBCATE_OFFICE = "办公"

SUBCATE_GNOME = "Gnome"
SUBCATE_KDE = "KDE"
SUBCATE_XFCE = "XFCE"

SUBCATE_FM = "无线电"
SUBCATE_MATH = "数学"
SUBCATE_SCIENCE = "科学"
SUBCATE_ELECTRONICS = "电子学"

SUBCATE_DATABASE = "数据库"
SUBCATE_DEBUG = "调试"
SUBCATE_EMBEDDED = "嵌入式"
SUBCATE_INTERPRETERS = "解释器"
SUBCATE_LIBDEVEL = "开发库"
SUBCATE_LIBS = "库"
SUBCATE_VCS = "版本控制"
SUBCATE_SHELL = "Shell"
SUBCATE_EDITOR = "编辑器"
SUBCATE_PROGRAMMINGLANGUAGE = "编程语言"
SUBCATE_KERNEL = "内核"

SUBCATE_TRANSLATIONS = "翻译"
SUBCATE_LOCALIZATION = "本地化"
SUBCATE_DOC = "文档"
SUBCATE_UTILS = "工具"
SUBCATE_MISC = "杂项"

RANK_DICT = {
    # CATE_WEB
    "Internet"      : (CATE_WEB, SUBCATE_WEB),
    "mail"          : (CATE_WEB, SUBCATE_MAIL),
    "web"           : (CATE_WEB, SUBCATE_WEB),
    "news"          : (CATE_WEB, SUBCATE_NEWS),
    "httpd"         : (CATE_WEB, SUBCATE_OTHERS),
    "net"           : (CATE_WEB, SUBCATE_OTHERS),
    # CATE_SYSTEM
    "admin"         : (CATE_SYSTEM, SUBCATE_ADMIM),
    "base"          : (CATE_SYSTEM, SUBCATE_ADMIM),
    # CATE_BEAUTY
    "fonts"         : (CATE_BEAUTY, SUBCATE_FONT),
    # CATE_MULTIMEDIA
    "video"         : (CATE_MULTIMEDIA, SUBCATE_VIDEO),
    "sound"         : (CATE_MULTIMEDIA, SUBCATE_SOUND),
    "otherosfs"     : (CATE_MULTIMEDIA, SUBCATE_OTHERS),
    # CATE_GAMES
    "games"         : (CATE_GAME, SUBCATE_GAME),
    # CATE_GRAPHICS
    "graphics"      : (CATE_GRAPHICS, SUBCATE_GRAPHICS),
    # CATE_OFFICE
    "text"          : (CATE_OFFICE, SUBCATE_OFFICE),
    "tex"           : (CATE_OFFICE, SUBCATE_OFFICE),
    # CATE_DESKTOP
    "gnome"         : (CATE_DESKTOP, SUBCATE_GNOME),
    "kde"           : (CATE_DESKTOP, SUBCATE_KDE),
    "xfce"          : (CATE_DESKTOP, SUBCATE_XFCE),
    "x11"           : (CATE_DESKTOP, SUBCATE_OTHERS),
    "metapackages"  : (CATE_DESKTOP, SUBCATE_OTHERS),
    # CATE_PROJECT
    "hamradio"      : (CATE_PROJECT, SUBCATE_FM),
    "math"          : (CATE_PROJECT, SUBCATE_MATH),
    "science"       : (CATE_PROJECT, SUBCATE_SCIENCE),
    "electronics"   : (CATE_PROJECT, SUBCATE_ELECTRONICS),
    "gnu-r"         : (CATE_PROJECT, SUBCATE_OTHERS),
    # CATE_DEVELOP
    "database"      : (CATE_DEVELOP, SUBCATE_DATABASE),
    "debug"         : (CATE_DEVELOP, SUBCATE_DEBUG),
    "devel"         : (CATE_DEVELOP, SUBCATE_OTHERS),
    "embedded"      : (CATE_DEVELOP, SUBCATE_EMBEDDED),
    "interpreters"  : (CATE_DEVELOP, SUBCATE_INTERPRETERS),
    "libdevel"      : (CATE_DEVELOP, SUBCATE_LIBDEVEL),
    "libs"          : (CATE_DEVELOP, SUBCATE_LIBS),
    "oldlibs"       : (CATE_DEVELOP, SUBCATE_LIBS),
    "vcs"           : (CATE_DEVELOP, SUBCATE_VCS),
    "shells"        : (CATE_DEVELOP, SUBCATE_SHELL),
    "zop"           : (CATE_DEVELOP, SUBCATE_OTHERS),
    "editors"       : (CATE_DEVELOP, SUBCATE_EDITOR),
    "cli-mono"      : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "php"           : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "haskell"       : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "java"          : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "lisp"          : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "ocaml"         : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "perl"          : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "python"        : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "ruby"          : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "comm"          : (CATE_DEVELOP, SUBCATE_PROGRAMMINGLANGUAGE),
    "zope"          : (CATE_DEVELOP, SUBCATE_OTHERS),
    "gnustep"       : (CATE_DEVELOP, SUBCATE_OTHERS),
    "kernel"        : (CATE_DEVELOP, SUBCATE_KERNEL),
    # CATE_OTHERS
    "translations"  : (CATE_OTHERS, SUBCATE_TRANSLATIONS),
    "localization"  : (CATE_OTHERS, SUBCATE_LOCALIZATION),
    "doc"           : (CATE_OTHERS, SUBCATE_DOC),
    "input"         : (CATE_OTHERS, SUBCATE_UTILS),
    "utility"       : (CATE_OTHERS, SUBCATE_UTILS),
    "utils"         : (CATE_OTHERS, SUBCATE_UTILS),
    "unknown"       : (CATE_OTHERS, SUBCATE_MISC),
    "misc"          : (CATE_OTHERS, SUBCATE_MISC),
    }

APP_STATE_NORMAL = 1
APP_STATE_UPGRADE = 2
APP_STATE_INSTALLED = 3
APP_STATE_DOWNLOADING = 4
APP_STATE_DOWNLOAD_PAUSE = 5
APP_STATE_INSTALLING = 6
APP_STATE_UPGRADING = 7
APP_STATE_UNINSTALLING = 8
APP_STATE_UNINSTALL_CONFIRM = 9

ACTION_INSTALL = 0
ACTION_UPGRADE = 1
ACTION_UNINSTALL = 2

PAGE_RECOMMEND = 0
PAGE_REPO = 1
PAGE_UPGRADE = 2
PAGE_UNINSTALL = 3
PAGE_COMMUNITY = 4
PAGE_MORE = 5

DOWNLOAD_STATUS_COMPLETE = 0
DOWNLOAD_STATUS_FAILED = 1
DOWNLOAD_STATUS_DONT_NEED = 2
DOWNLOAD_STATUS_PAUSE = 3
DOWNLOAD_STATUS_STOP = 4
DOWNLOAD_STATUS_TIMEOUT = 5

CATEGORY_LIST = [(CATE_WEB,              
                  ("web.png", 
                   sortedDict.SortedDict([
                                    (SUBCATE_ALL, []),
                                    (SUBCATE_MAIL, []),
                                    (SUBCATE_WEB, []),
                                    (SUBCATE_NEWS, []),
                                    (SUBCATE_OTHERS, []),
                                    ]))),
                 (CATE_SYSTEM,
                  ("system.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_ADMIM, []),
                                 ]))),
                 (CATE_BEAUTY,   
                  ("beauty.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_FONT, []),
                                 ]))),
                 (CATE_MULTIMEDIA,       
                  ("multimedia.png", 
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_VIDEO, []),
                                 (SUBCATE_SOUND, []),
                                 (SUBCATE_OTHERS, []),
                                 ]))),
                 (CATE_GAME,     
                  ("game.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_GAME, []),
                                 ]))),
                 (CATE_GRAPHICS, 
                  ("graphics.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_GRAPHICS, []),
                                 ]))),
                 (CATE_OFFICE,   
                  ("office.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_OFFICE, []),
                                 ]))),
                 (CATE_DESKTOP,  
                  ("desktop.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_GNOME, []),
                                 (SUBCATE_KDE, []),
                                 (SUBCATE_XFCE, []),
                                 (SUBCATE_OTHERS, []),
                                 ]))),
                 (CATE_PROJECT,          
                  ("project.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_FM, []),
                                 (SUBCATE_MATH, []),
                                 (SUBCATE_SCIENCE, []),
                                 (SUBCATE_ELECTRONICS, []),
                                 (SUBCATE_OTHERS, []),
                                 ]))),
                 (CATE_DEVELOP,
                  ("develop.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_DATABASE, []),
                                 (SUBCATE_DEBUG, []),
                                 (SUBCATE_EMBEDDED, []),
                                 (SUBCATE_INTERPRETERS, []),
                                 (SUBCATE_LIBDEVEL, []),
                                 (SUBCATE_LIBS, []),
                                 (SUBCATE_VCS, []),
                                 (SUBCATE_SHELL, []),
                                 (SUBCATE_EDITOR, []),
                                 (SUBCATE_PROGRAMMINGLANGUAGE, []),
                                 (SUBCATE_KERNEL, []),
                                 (SUBCATE_OTHERS, []),
                                 ]))),
                 (CATE_OTHERS,   
                  ("other.png",
                   sortedDict.SortedDict([
                                 (SUBCATE_ALL, []),
                                 (SUBCATE_TRANSLATIONS, []),
                                 (SUBCATE_LOCALIZATION, []),
                                 (SUBCATE_DOC, []),
                                 (SUBCATE_UTILS, []),
                                 (SUBCATE_MISC, []),
                                 (SUBCATE_OTHERS, [])
                                 ]))),
                 ]

RECOMMEND_LIST = [
    ("最近更新",        ["gedit", "eclipse", "eog", "vlc", "network-manager-gnome"]),
    ("编辑推荐",        ["stellarium", "samba", "wireshark", "playonlinux", "amarok"]),
    ("网络工具",        ["chromium-browser", "firefox", "uget", "qbittorrent", "amule"]),
    ("网络通讯",        ["pidgin", "openfetion", "xchat", "gnome-gmail-notifier", "thunderbird"]),
    ("多媒体",         ["rhythmbox", "gtk-recordmydesktop", "openshot", "moovida", "audacity"]),
    ("图形图像",        ["gwenview", "gnome-paint", "blender", "inkscape", "gimp"]),
    ("游戏",           ["beneath-a-steel-sky", "freedroid", "flightgear", "supertuxkart", "alien-arena"]),
    ("系统工具",        ["ibus-pinyin", "camorama", "brasero", "gparted", "unetbootin"]),
    ("驱动",           ["jockey-gtk", "ntfs-config", "fglrx", "ndisgtk", "aqsis"]),
    ("其他",           ["libreoffice", "liferea", "tomboy", "evince", "kchmviewer"]),
    ]

LANGUAGE = [
    "简体中文",
    "繁体中文",
    "英语",
    ]

SOURCE_LANGUAGE = "英语"
TARGET_LANGUAGE = "简体中文"

SCREENSHOT_DOWNLOAD_DIR = "/var/cache/deepin-software-center/screenshot/"
DOWNLOAD_FAILED = 1
DOWNLOAD_SUCCESS = 0

DEFAULT_FONT = "文泉驿微米黑"

LINE_TOP = 0
LINE_BOTTOM = 1
LINE_LEFT = 2
LINE_RIGHT = 3

BUTTON_FONT_SIZE_SMALL = 10
BUTTON_FONT_SIZE_MEDIUM = 11
LABEL_FONT_SIZE = 10 * 1000
LABEL_FONT_MEDIUM_SIZE = 11 * 1000
LABEL_FONT_LARGE_SIZE = 12 * 1000
LABEL_FONT_X_LARGE_SIZE = 15 * 1000
LABEL_FONT_XX_LARGE_SIZE = 20 * 1000

DOWNLOAD_TIMEOUT = 30           # times
POST_TIMEOUT = 10               # seconds
GET_TIMEOUT = 10               # seconds

ACTION_BUTTON_PADDING_X = 5
ACTION_BUTTON_WIDTH = 100

TOPBAR_PADDING_LEFT = 10
TOPBAR_PADDING_RIGHT = 40
TOPBAR_PADDING_UPDATE_RIGHT = 10
TOPBAR_SEARCH_RIGHT = 30
TOPBAR_SEARCH_ADJUST_RIGHT = 15

