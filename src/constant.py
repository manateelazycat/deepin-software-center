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

from lang import __, getDefaultLanguage

OS_VERSION = "LinuxDeepin"

VERSION = "2.0"
AUTHOR = ["Wang Yong"]
ARTISTS = ["Can Yang"]

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
PAGE_DOWNLOAD_MANAGE = 4

DOWNLOAD_STATUS_COMPLETE = 0
DOWNLOAD_STATUS_FAILED = 1
DOWNLOAD_STATUS_DONT_NEED = 2
DOWNLOAD_STATUS_PAUSE = 3
DOWNLOAD_STATUS_STOP = 4
DOWNLOAD_STATUS_TIMEOUT = 5

CLASSIFY_NEWS = __("Classify News")
CLASSIFY_RECOMMEND = __("Classify Recommend")
CLASSIFY_WEB = __("Classify Web")
CLASSIFY_MULTIMEDIA = __("Classify Multimedia")
CLASSIFY_GAME = __("Classify Game")
CLASSIFY_GRAPHICS = __("Classify Graphics")
CLASSIFY_WORD = __("Classify Word")
CLASSIFY_PROFESSIONAL = __("Classify Professional")
CLASSIFY_PROGRAMMING = __("Classify Programming")
CLASSIFY_DRIVER = __("Classify Driver")
CLASSIFY_WINDOWS = __("Classify Windows")
CLASSIFY_OTHERS = __("Classify Others")

CLASSIFY_FILES = [(CLASSIFY_WEB,          "web.txt"),
                  (CLASSIFY_MULTIMEDIA,   "multimedia.txt"),
                  (CLASSIFY_GAME,         "game.txt"),
                  (CLASSIFY_GRAPHICS,     "graphics.txt"),
                  (CLASSIFY_WORD,         "word.txt"),
                  (CLASSIFY_PROFESSIONAL, "professional.txt"),
                  (CLASSIFY_PROGRAMMING,  "programming.txt"),
                  (CLASSIFY_DRIVER,       "driver.txt"),
                  (CLASSIFY_WINDOWS,      "windows.txt"),
                  (CLASSIFY_OTHERS,       "others.txt")
                  ]

CLASSIFY_LIST = [(CLASSIFY_WEB,          ("web.png", None)),
                 (CLASSIFY_MULTIMEDIA,   ("multimedia.png", None)),
                 (CLASSIFY_GAME,         ("game.png", None)),
                 (CLASSIFY_GRAPHICS,     ("graphics.png", None)),
                 (CLASSIFY_WORD,         ("word.png", None)),
                 (CLASSIFY_PROFESSIONAL, ("professional.png", None)),
                 (CLASSIFY_PROGRAMMING,  ("develop.png", None)),
                 (CLASSIFY_DRIVER,       ("driver.png", None)),
                 (CLASSIFY_WINDOWS,      ("win.png", None)),
                 (CLASSIFY_OTHERS,       ("other.png", None))
                 ]

SCREENSHOT_DOWNLOAD_DIR = "/var/cache/deepin-software-center/screenshot/"
UPDATE_DATA_BACKUP_DIR = "../updateData/"
UPDATE_DATA_DIR = "/var/cache/deepin-software-center/updateData/"
UPDATE_DATA_DOWNLOAD_DIR = "/var/cache/deepin-software-center/"
UUID_FILE = "/var/lib/deepin-software-center/uuid"
DOWNLOAD_FAILED = 1
DOWNLOAD_SUCCESS = 0

DEFAULT_FONT = "文泉驿微米黑"

LINE_TOP = 0
LINE_BOTTOM = 1
LINE_LEFT = 2
LINE_RIGHT = 3

DEFAULT_FONT_SIZE = 10
BUTTON_FONT_SIZE_SMALL = 10
BUTTON_FONT_SIZE_MEDIUM = 11
BUTTON_FONT_SIZE_LARGE = 12
LABEL_FONT_SIZE = 10 * 1000
LABEL_FONT_MEDIUM_SIZE = 11 * 1000
LABEL_FONT_LARGE_SIZE = 12 * 1000
LABEL_FONT_X_LARGE_SIZE = 13 * 1000
LABEL_FONT_XX_LARGE_SIZE = 15 * 1000
LABEL_FONT_XXX_LARGE_SIZE = 20 * 1000

DOWNLOAD_TIMEOUT = 120          # times
POST_TIMEOUT = 10               # seconds
GET_TIMEOUT = 10                # seconds

ACTION_BUTTON_PADDING_X = 5
ACTION_BUTTON_PADDING_Y = 5
lang = getDefaultLanguage()
if lang == "default":
    ACTION_BUTTON_WIDTH = 140
    APP_BASIC_WIDTH_ADJUST = 120
else:
    ACTION_BUTTON_WIDTH = 100
    APP_BASIC_WIDTH_ADJUST = 0

DEFAULT_WINDOW_WIDTH = 890
DEFAULT_WINDOW_HEIGHT = 631

TOPBAR_PADDING_LEFT = 10
TOPBAR_PADDING_RIGHT = 40
TOPBAR_PADDING_UPDATE_RIGHT = 10
TOPBAR_SEARCH_RIGHT = 30
TOPBAR_SEARCH_ADJUST_RIGHT = 15

SOCKET_SOFTWARECENTER_ADDRESS = ("127.0.0.1", 31500)
SOCKET_UPDATEMANAGER_ADDRESS = ("127.0.0.1", 31501)
SOCKET_COMMANDPROXY_ADDRESS = ("127.0.0.1", 31502)
UPDATE_INTERVAL = 24            # in hours
RADIUS = 6
POPUP_WINDOW_RADIUS = 4
THEME_WINDOW_WIDTH = 318
THEME_WINDOW_HEIGHT = 177

DRAW_LOOP = "loop"
DRAW_EXTEND = "extend"
DRAW_LEFT = "left"
DRAW_RIGHT = "right"

SCREENSHOT_NONEED = -1
SCREENSHOT_UPLOAD = 0

COOKIE_FILE = "cookie.txt"

SERVER_ADDRESS = "http://apis.linuxdeepin.com"

