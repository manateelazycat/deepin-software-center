#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Yong Wang
#
# Author:     Yong Wang <lazycat.manatee@gmail.com>
# Maintainer: Yong Wang <lazycat.manatee@gmail.com>
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

VERSION = "2.0"
AUTHOR = ["Yong Wang"]
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
PAGE_MORE = 5

DOWNLOAD_STATUS_COMPLETE = 0
DOWNLOAD_STATUS_FAILED = 1
DOWNLOAD_STATUS_DONT_NEED = 2
DOWNLOAD_STATUS_PAUSE = 3
DOWNLOAD_STATUS_STOP = 4
DOWNLOAD_STATUS_TIMEOUT = 5

CLASSIFY_NEWS = "最近更新"         # 最近更新的软件, 主要用于推荐新的程序
CLASSIFY_RECOMMEND = "编辑推荐"    # 具体有特色的软件, 主要用于定期循环推荐
CLASSIFY_WEB = "网络应用"          # 任何以网络设计为主的软件
CLASSIFY_MULTIMEDIA = "影音播放"   # 围绕着视频、音频设计的播放软件和相关工具
CLASSIFY_GAME = "游戏娱乐"         # 游戏及其工具
CLASSIFY_GRAPHICS = "图形图像"     # 围绕图形编辑和设计的相关工具
CLASSIFY_WORD = "文字处理"         # 办公, 阅读, 和其他相关的文字处理软件
CLASSIFY_PROFESSIONAL = "行业软件" # 专业相关的软件, 需要相关的专业知识
CLASSIFY_PROGRAMMING = "编程开发"  # 围绕开发的各种相关工具
CLASSIFY_DRIVER = "硬件驱动"       # 硬件驱动及工具
CLASSIFY_WINDOWS = "WIN 软件"     # 通过 Wine 来运行的各种软件
CLASSIFY_OTHERS = "其他软件"       # 其他杂项

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
ACTION_BUTTON_WIDTH = 100

TOPBAR_PADDING_LEFT = 10
TOPBAR_PADDING_RIGHT = 40
TOPBAR_PADDING_UPDATE_RIGHT = 10
TOPBAR_SEARCH_RIGHT = 30
TOPBAR_SEARCH_ADJUST_RIGHT = 15

SOCKET_SOFTWARECENTER_ADDRESS = ("127.0.0.1", 31502)
SOCKET_UPDATEMANAGER_ADDRESS  = ("127.0.0.1", 31501)
UPDATE_INTERVAL = 24            # in hours
