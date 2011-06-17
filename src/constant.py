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

CLASSIFY_NEWS = "最近更新"
CLASSIFY_RECOMMEND = "编辑推荐"
CLASSIFY_WEB = "网络应用"
CLASSIFY_MULTIMEDIA = "影音播放"
CLASSIFY_GAME = "游戏娱乐"
CLASSIFY_GRAPHICS = "图形图像"
CLASSIFY_UTILS = "实用工具"
CLASSIFY_PROFESSIONAL = "行业软件"
CLASSIFY_PROGRAMMING = "编程开发"
CLASSIFY_DRIVER = "硬件驱动"
CLASSIFY_WINDOWS = "WIN 软件"
CLASSIFY_OTHERS = "其他软件"

CLASSIFY_FILES = [(CLASSIFY_WEB,          "web.txt"),
                  (CLASSIFY_MULTIMEDIA,   "multimedia.txt"),
                  (CLASSIFY_GAME,         "game.txt"),
                  (CLASSIFY_GRAPHICS,     "graphics.txt"),
                  (CLASSIFY_UTILS,        "utils.txt"),
                  (CLASSIFY_PROFESSIONAL, "professional.txt"),
                  (CLASSIFY_PROGRAMMING,  "programming.txt"),
                  (CLASSIFY_DRIVER,       "driver.txt"),
                  (CLASSIFY_WINDOWS,      "windows.txt"),
                  (CLASSIFY_OTHERS,       "others.txt")
                  ]

CLASSIFY_LIST = [(CLASSIFY_WEB,          ("web.png", [])),
                 (CLASSIFY_MULTIMEDIA,   ("multimedia.png", [])),
                 (CLASSIFY_GAME,         ("game.png", [])),
                 (CLASSIFY_GRAPHICS,     ("graphics.png", [])),
                 (CLASSIFY_UTILS,        ("desktop.png", [])),
                 (CLASSIFY_PROFESSIONAL, ("project.png", [])),
                 (CLASSIFY_PROGRAMMING,  ("develop.png", [])),
                 (CLASSIFY_DRIVER,       ("office.png", [])),
                 (CLASSIFY_WINDOWS,      ("win.png", [])),
                 (CLASSIFY_OTHERS,       ("other.png", []))
                 ]

RECOMMEND_LIST = [
    (CLASSIFY_NEWS,             False, ["gedit", "g2ipmsg", "eog", "vlc", "network-manager-gnome"]),
    (CLASSIFY_RECOMMEND,        False, ["stellarium", "samba", "wireshark", "playonlinux", "amarok"]),
    (CLASSIFY_WEB,              True,  ["chromium-browser", "uget", "pidgin", "thunderbird", "qbittorrent"]),
    (CLASSIFY_MULTIMEDIA,       True,  ["rhythmbox", "gtk-recordmydesktop", "openshot", "moovida", "audacity"]),
    (CLASSIFY_GAME,             True,  ["beneath-a-steel-sky", "freedroid", "flightgear", "supertuxkart", "alien-arena"]),
    (CLASSIFY_GRAPHICS,         True,  ["gwenview", "gnome-paint", "blender", "inkscape", "gimp"]),
    (CLASSIFY_UTILS,            True,  ["ibus-pinyin", "camorama", "brasero", "gparted", "unetbootin"]),
    (CLASSIFY_PROFESSIONAL,     True,  ["qcad", "mayavi2", "maxima", "axiom", "cadabra"]),
    (CLASSIFY_PROGRAMMING,      True,  ["emacs", "eclipse", "anjuta", "codeblocks", "geany"]),
    (CLASSIFY_DRIVER,           True,  ["jockey-gtk", "ntfs-config", "fglrx", "ndisgtk", "xserver-xorg-video-nv"]),
    (CLASSIFY_WINDOWS,          True,  ["wine", "playonlinux", "q4wine", "winetricks", "wisotool"]),
    (CLASSIFY_OTHERS,           True,  ["libreoffice", "liferea", "tomboy", "evince", "kchmviewer"]),
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
GET_TIMEOUT = 10                # seconds

ACTION_BUTTON_PADDING_X = 5
ACTION_BUTTON_PADDING_Y = 5
ACTION_BUTTON_WIDTH = 100

TOPBAR_PADDING_LEFT = 10
TOPBAR_PADDING_RIGHT = 40
TOPBAR_PADDING_UPDATE_RIGHT = 10
TOPBAR_SEARCH_RIGHT = 30
TOPBAR_SEARCH_ADJUST_RIGHT = 15

