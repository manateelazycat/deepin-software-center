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
from lang import __, getDefaultLanguage, DEFAULT_LANG
from math import pi
import cairo
import gtk
import locale
import math
import os
import pango
import pangocairo
import socket
import stat
import subprocess
import threading as td
import time

def isDoubleClick(event):
    '''Whether an event is double click?'''
    return event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS

def getStarPath(starIndex, starLevel):
    '''Get star path.'''
    if starIndex == 1:
        if starLevel > 8:
            imgPath = "star_green.png"
        elif starLevel > 2:
            imgPath = "star_yellow.png"
        elif starLevel == 2:
            imgPath = "star_red.png"
        else:
            imgPath = "halfstar_red.png"
    elif starIndex in [2, 3, 4]:
        if starLevel > 8:
            imgPath = "star_green.png"
        elif starLevel >= starIndex * 2:
            imgPath = "star_yellow.png"
        elif starLevel == starIndex * 2 - 1:
            imgPath = "halfstar_yellow.png"
        else:
            imgPath = "star_gray.png"
    elif starIndex == 5:
        if starLevel >= starIndex * 2:
            imgPath = "star_green.png"
        elif starLevel == starIndex * 2 - 1:
            imgPath = "halfstar_green.png"
        else:
            imgPath = "star_gray.png"
            
    return "cell/%s" % (imgPath)

def getFontFamilies():
    '''Get all font families in system.'''
    fontmap = pangocairo.cairo_font_map_get_default()
    return map (lambda f: f.get_name(), fontmap.list_families())

def getScreenSize(widget):
    '''Get widget's screen size.'''
    screen = widget.get_screen()
    width = screen.get_width()
    height = screen.get_height()
    return (width, height)

def getPkgIcon(pkg, iconWidth=32, iconHeight=32):
    '''Get package icon.'''
    iconPath = "../pkgData/AppIcon/" + pkg.name + ".png"
    if os.path.exists (iconPath):
        return gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(iconPath, iconWidth, iconHeight))
    else:
        return gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(
                "../theme/default/image/icon/appIcon.ico", 
                iconWidth, iconHeight))
def getPkgName(pkg):
    '''Get package name.'''
    return pkg.name

def printExecTime(func):
    '''Print execute time.'''
    def wrap(*a, **kw):
        startTime = time.time()
        ret = func(*a, **kw)
        print "%s time: %s" % (str(func), time.time() - startTime)
        return ret
    return wrap

def getPkgExecPath(pkg):
    '''Get path of execute file.'''
    execPath = "../pkgData/pkgPath/%s" % (pkg.name)
    if os.path.exists(execPath):
        execFile = open(execPath, "r")
        content = execFile.read()
        execFile.close()
        
        # Just read first line, not include return char.
        return content.split("\n")[0]
    else:
        return None
    
def readFile(filepath, checkExists=False):
    '''Read file.'''
    if checkExists and not os.path.exists(filepath):
        return ""
    else:
        rFile = open(filepath, "r")
        content = rFile.read()
        rFile.close()
        
        return content

def readFirstLine(filepath, checkExists=False):
    '''Read first line.'''
    if checkExists and not os.path.exists(filepath):
        return ""
    else:
        rFile = open(filepath, "r")
        content = rFile.readline().split("\n")[0]
        rFile.close()
        
        return content

def evalFile(filepath, checkExists=False):
    '''Eval file content.'''
    if checkExists and not os.path.exists(filepath):
        return None
    else:
        try:
            readFile = open(filepath, "r")
            content = eval(readFile.read())
            readFile.close()
            
            return content
        except Exception, e:
            print e
            
            return None

def writeFile(filepath, content):
    '''Write file.'''
    f = open(filepath, "w")
    f.write(content)
    f.close()

def getPkgShortDesc(pkg):
    '''Get package's short description.'''
    pkgPath = "../pkgData/pkgInfo/" + pkg.name
    if os.path.exists(pkgPath):
        return ((evalFile(pkgPath))[getDefaultLanguage()])["shortDesc"]
    else:
        return pkg.candidate.summary

def getPkgLongDesc(pkg):
    '''Get package's long description.'''
    pkgPath = "../pkgData/pkgInfo/" + pkg.name
    if os.path.exists(pkgPath):
        return ((evalFile(pkgPath))[getDefaultLanguage()])["longDesc"]
    else:
        return pkg.candidate.description

def getPkgVersion(pkg):
    '''Get package's version.'''
    # Return current version if package has installed. 
    if pkg.is_installed:
        return pkg.installed.version    
    # Otherwise return candidate version.
    else:
        return pkg.candidate.version

def getPkgNewestVersion(pkg):
    '''Get package's newest version.'''
    if len(pkg.versions) == 0:
        print "%s: length of pkg.versions equal 0." % (getPkgName(pkg))
        return pkg.candidate.version
    else:
        return pkg.versions[0].version

def getPkgSection(pkg):
    '''Get package's section.'''
    return pkg.candidate.section

def getPkgSize(pkg):
    '''Get package's  size.'''
    return pkg.candidate.size

def getPkgHomepage(pkg):
    '''Get homepage of package.'''
    return pkg.candidate.homepage

def getPkgInstalledSize(pkg):
    '''Get package's installed size.'''
    return pkg.candidate.installed_size

def getPkgDependSize(cache, pkg, action):
    '''Get package's dependent size.'''
    try:
        # Clear first.
        cache.clear()
        
        # Mark package.
        if action == ACTION_INSTALL:
            pkg.mark_install()
        elif action == ACTION_UPGRADE:
            pkg.mark_upgrade()
        else:
            pkg.mark_delete()
            
        # Get change size.
        cache.get_changes()
        downloadSize = cache.required_download
        useSize = abs(cache.required_space)
        
        # Clear last.
        cache.clear()
        
        return (downloadSize, useSize)
    except Exception, e:
        # Just return package's size if exception throwed.
        print "Calculate `%s` dependent used size failed, instead package's used size." % (getPkgName(pkg))
        return (pkg.candidate.size, pkg.candidate.installed_size)

def getCommandOutputFirstLine(commands):
    '''Run command and return result.'''
    process = subprocess.Popen(commands, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.readline()

def getCommandOutput(commands):
    '''Run command and return result.'''
    process = subprocess.Popen(commands, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.readlines()
    
def getKernelPackages():
    '''Get running kernel packages.'''
    kernelVersion = (getCommandOutputFirstLine(["uname", "-r"]).split("-generic"))
    
    return ["linux-image-generic", 
            "linux-image-%s-generic" % (kernelVersion),
            "linux-headers-generic", 
            "linux-headers-%s" % (kernelVersion),
            "linux-headers-%s-generic" % (kernelVersion),
            "linux-generic"
            ]

KERNEL_PACKAGES = getKernelPackages()    
    
def isPkgUninstallable(pkg, checkInstalled=True):
    '''Is pkg is un-installable?'''
    inFilterSection = pkg.candidate.section in ["libs", "libdevel", "oldlibs"]
    isKernelPackages = pkg.name in KERNEL_PACKAGES
    
    # When first use cache need check installed.
    if checkInstalled:
        return pkg.is_installed and not pkg.essential and not inFilterSection and not isKernelPackages
    # Don't need check installed status when running.
    # Because package's is_installed not update sometimes.
    else:
        return not pkg.essential and not inFilterSection and not isKernelPackages

def containerRemoveAll(container):
    '''Remove all child widgets from container.'''
    container.foreach(lambda widget: container.remove(widget))

def formatFileSize(bytes, precision=2):
    '''Returns a humanized string for a given amount of bytes'''
    bytes = int(bytes)
    if bytes is 0:
        return '0B'
    else:
        log = math.floor(math.log(bytes, 1024))
        quotient = 1024 ** log
        size = bytes / quotient
        remainder = bytes % quotient
        if remainder < 10 ** (-precision): 
            prec = 0
        else:
            prec = precision
        return "%.*f%s" % (prec,
                           size,
                           ['B', 'KB', 'MB', 'GB', 'TB','PB', 'EB', 'ZB', 'YB']
                           [int(log)])

def pixbufNewFromIcon(stockId, size):
    '''Create pixbuf from given id and size.'''
    iconTheme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())
    return iconTheme.load_icon(stockId, size, gtk.ICON_LOOKUP_USE_BUILTIN)

def isInRect((cx, cy), (x, y, w, h)):
    '''Whether coordinate in rectangle.'''
    return (cx >= x and cx <= x + w and cy >= y and cy <= y + h)

def scrollToTop(scrolledWindow):
    '''Scroll scrolled window to top.'''
    scrolledWindow.get_vadjustment().set_value(0)
    
def postGUI(func):
    '''Post GUI code in main thread.'''
    def wrap(*a, **kw):
        gtk.gdk.threads_enter()
        ret = func(*a, **kw)
        gtk.gdk.threads_leave()
        return ret
    return wrap

def printEnv():
    '''Print environment variable.'''
    for param in os.environ.keys():
        print "*** %20s %s" % (param,os.environ[param])                

def setProgress(progressbar, progress):
    '''Set progress.'''
    progressbar.set_fraction(progress / 100.0)
    if progress == 0:
        progressbar.set_text("")
    else:
        progressbar.set_text(str(progress) + "%")

def resizeWindow(widget, event, window):
    '''Re-size window.'''
    # If a shift key is pressed, start resizing
    if event.state & gtk.gdk.SHIFT_MASK:
        window.begin_resize_drag(
            gtk.gdk.WINDOW_EDGE_SOUTH_EAST, 
            event.button, 
            int(event.x_root), 
            int(event.y_root), 
            event.time)
    
def moveWindow(widget, event, window):
    '''Move window.'''
    window.begin_move_drag(
        event.button, 
        int(event.x_root), 
        int(event.y_root), 
        event.time)

def addInScrolledWindow(scrolledWindow, widget, shadowType=gtk.SHADOW_NONE):
    '''Like add_with_viewport in ScrolledWindow, with shadow type.'''
    scrolledWindow.add_with_viewport(widget)
    viewport = scrolledWindow.get_child()
    if viewport != None:
        viewport.set_shadow_type(shadowType)
    else:
        print "addInScrolledWindow: Impossible, no viewport widget in ScrolledWindow!"
    
def newButtonWithoutPadding(content=None):
    '''Create button without padding.'''
    button = gtk.Button(content)
    button.set_property("can-focus", False)
    return button

def getFontYCoordinate(y, height, fontSize):
    '''Get font y coordinate.'''
    return y + (height + fontSize) / 2 - 1

# This is a hacking way, 
# Author recommend use xmlrpclib.ServerProxy('http://localhost:6800/rpc').getVersion() get version number.
# But above solution easy to failed when connect is unavailable.
# So i pick version information from output of command "aria2c --version".
def getAria2Version():
    '''Get aria2 version.'''
    versionList = getCommandOutputFirstLine(["aria2c", "--version"]).split().pop().split('.')
    
    return (int(versionList[0]), int(versionList[1]), int(versionList[2]))

def getOSVersion():
    '''Get OS version.'''
    versionInfos = getCommandOutputFirstLine(["lsb_release", "-i"]).split()
    
    if len(versionInfos) > 0:
        return versionInfos[-1]
    else:
        return ""

def compareCandidates((preA, matchA, restA, pkgA), (preB, matchB, restB, pkgB)):
    '''Compare candidates.'''
    lenA = len(preA)
    lenB = len(preB)
    # Candidate's order at front if pre string's length shorter.
    if lenA < lenB:
        return -1
    # Compare package name if pre string's length is same.
    elif lenA == lenB:
        return cmp(pkgA, pkgB)
    else:
        return 1        

def getCurrentTime():
    '''Get current time.'''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def runCommand(command):
    '''Run command.'''
    subprocess.Popen("nohup %s > /dev/null 2>&1" % (command), shell=True)
    
def sendCommand(command):
    '''Send command.'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    try:
        s.sendto(command, SOCKET_COMMANDPROXY_ADDRESS)
    except Exception, e:
        print "sendCommand got error: %s" % (e)
    finally:
        s.close()
    
def touchFile(filepath):
    '''Touch file.'''
    # Create directory first.
    dir = os.path.dirname(filepath)
    if not os.path.exists(dir):
        os.makedirs(dir)
        
    # Touch file.
    open(filepath, "w").close()

def showVersionTooltip(widget, pkg):
    '''Show version tooltip.'''
    newestVersion = getPkgNewestVersion(pkg)
    currentVersion = getPkgVersion(pkg)
    if newestVersion == currentVersion:
        setHelpTooltip(
            widget,
            "%s\n%s: %s" % (__("Click Show Detail"), __("Current Version"), currentVersion))
    else:    
        setHelpTooltip(
            widget,
            "%s\n%s: %s\n%s: %s" % (__("Click Show Detail"), 
                                    __("Current Version"), 
                                    currentVersion, 
                                    __("Upgrade Version"),
                                    newestVersion))
    
def setHelpTooltip(widget, helpText):
    '''Set help tooltip.'''
    widget.connect("enter-notify-event", lambda w, e: showHelpTooltip(w, helpText))

def showHelpTooltip(widget, helpText):
    '''Create help tooltip.'''
    widget.set_has_tooltip(True)
    widget.set_tooltip_text(helpText)
    widget.trigger_tooltip_query()
    
    return False

def treeViewGetToplevelNodeCount(treeview):
    '''Get toplevel node count.'''
    model = treeview.get_model()
    if model != None:
        return model.iter_n_children(None)
    else:
        return 0
    
def treeViewGetSelectedPath(treeview):
    '''Get selected path.'''
    selection = treeview.get_selection()
    (_, treePaths) = selection.get_selected_rows()
    if len(treePaths) != 0:
        return (treePaths[0])[0]
    else:
        return None
 
def treeViewFocusFirstToplevelNode(treeview):
    '''Focus first toplevel node.'''
    treeview.set_cursor((0))
    
def treeViewFocusLastToplevelNode(treeview):
    '''Focus last toplevel node.'''
    nodeCount = treeViewGetToplevelNodeCount(treeview)
    if nodeCount > 0:
        path = (nodeCount - 1)
    else:
        path = (0)
    treeview.set_cursor(path)
    
def treeViewScrollVertical(treeview, scrollUp=True):
    '''Scroll tree view vertical.'''
    # Init.
    scrollNum = 9
    candidateCount = treeViewGetToplevelNodeCount(treeview)
    cursor = treeview.get_cursor()
    (path, column) = cursor
    maxCandidate = candidateCount - 1
    
    # Get candidate at cursor.
    if path == None:
        currentCandidate = maxCandidate
    else:
        (currentCandidate,) = path
        
    # Set cursor to new candidate.
    if scrollUp:
        newCandidate = max(0, currentCandidate - scrollNum)
    else:
        newCandidate = min(currentCandidate + scrollNum, maxCandidate)
        
    treeview.set_cursor((newCandidate))
    
def treeViewFocusNextToplevelNode(treeview):
    '''Focus next toplevel node.'''
    selectedPath = treeViewGetSelectedPath(treeview)
    if selectedPath != None:
        nodeCount = treeViewGetToplevelNodeCount(treeview)
        if selectedPath < nodeCount - 1:
            treeview.set_cursor((selectedPath + 1))

def treeViewFocusPrevToplevelNode(treeview):
    '''Focus previous toplevel node.'''
    selectedPath = treeViewGetSelectedPath(treeview)
    if selectedPath != None:
        if selectedPath > 0:
            treeview.set_cursor((selectedPath - 1))

def removeFile(path):
    '''Remove file.'''
    if os.path.exists(path):
        os.remove(path)
        
def removeDirectory(path):
    """equivalent to rm -rf path"""
    for i in os.listdir(path):
        fullPath = os.path.join(path, i)
        if os.path.isdir(fullPath):
            removeDirectory(fullPath)
        else:
            os.remove(fullPath)
    os.rmdir(path)        

def getLastUpdateHours(filepath):
    """
    Return the number of hours since last update.
    
    If the date is unknown, return "None"
    """
    if not os.path.exists(filepath):
        return None
    agoHours = int((time.time() - os.stat(filepath)[stat.ST_MTIME]) / (60 * 60))
    return agoHours

class AnonymityThread(td.Thread):
    '''Anonymity thread.'''

    def __init__(self, callback):
        '''Init anonymity thread.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit

        self.callback = callback
        
    def run(self):
        '''Run.'''
        self.callback()    
        
def addInList(eList, element):
    '''Add element in list.'''
    if not element in eList:
        eList.append(element)
        
def removeFromList(eList, element):
    '''Remove element from list.'''
    if element in eList:
        eList.remove(element)
        
def sortAlpha(eList):
    '''Get alpha list.'''
    return sorted(eList, key=lambda e: e)

def sortMatchKeyword(eList, keyword):
    '''Sort list by match keyword.'''
    return sorted(eList, cmp=lambda x, y: cmpMatchKeyword(x, y, keyword))

def cmpMatchKeyword(x, y, keyword):
    '''Compare match keyword.'''
    xMatches = x.split(keyword)
    yMatches = y.split(keyword)
    xMatchPre, xMatchPost = xMatches[0], ''.join(xMatches[1:])
    yMatchPre, yMatchPost = yMatches[0], ''.join(yMatches[1:])
    xMatchTimes = len(xMatches)
    yMatchTimes = len(yMatches)
    xLenPre = len(xMatchPre)
    xLenPost = len(xMatchPost)
    yLenPre = len(yMatchPre)
    yLenPost = len(yMatchPost)
    
    if xLenPre < yLenPre:
        return -1
    elif xLenPre > yLenPre:
        return 1
    elif xLenPost < yLenPost:
        return -1
    elif xLenPost > yLenPost:
        return 1
    elif xMatchTimes > yMatchTimes:
        return -1
    elif xMatchTimes < yMatchTimes:
        return 1
    elif len(xMatchPost.split(keyword)[0]) < len(yMatchPost.split(keyword)[0]):
        return -1
    else:
        return cmp(xMatchPre + xMatchPost, yMatchPre + yMatchPost)

def todayStr():
    '''Get string of today.'''
    structTime = time.localtime()
    return "%s-%s-%s" % (structTime.tm_year, structTime.tm_mon, structTime.tm_mday)

def aptsearch(keywords):
    '''Search keywords.'''
    lines = getCommandOutput(["apt-cache", "search"] + keywords)
    pkgs = []
    for line in lines:
        splitList = line.split()
        if len(splitList) > 0:
            pkgs.append(splitList[0])        
            
    return pkgs

def getDirSize(dirname):
    '''Get directory size.'''
    totalSize = 0
    for root, dirs, files in os.walk(dirname):
        for filepath in files:
            totalSize += os.path.getsize(os.path.join(root, filepath))
            
    return totalSize

def getEntryText(entry):
    '''Get entry text.'''
    return entry.get_text().split(" ")[0]

def parseProxyString():
    '''Parse proxy string.'''
    proxyDict = evalFile("./proxy", True)
    if proxyDict != None and proxyDict.has_key("address") and "://" in proxyDict["address"]:
        [addressPre, addressPost] = proxyDict["address"].split("://")
        if proxyDict.has_key("port"):
            port = ":" + proxyDict["port"]
        else:
            port = ""
        if proxyDict.has_key("user"):
            user = proxyDict["user"]
        else:
            user = ""
        if proxyDict.has_key("password"):
            password = ":" + proxyDict["password"]
        else:
            password = ""
            
        if user == "" and password == "":
            proxyString = addressPre + "://" + user + password + addressPost + port
        else:
            proxyString = addressPre + "://" + user + password + "@" + addressPost + port
            
        return proxyString
    else:
        return None
    
def killProcess(proc):
    '''Kill process.'''
    try:
        if proc != None:
            proc.kill()
    except Exception, e:
        pass

#  LocalWords:  halfstar AppIcon pkgInfo shortDesc zh TW longDesc downloadSize
#  LocalWords:  getPkgInstalledSize getPkgDependSize useSize uname libdevel ZB
#  LocalWords:  oldlibs resize moveWindow addInScrolledWindow scrolledWindow
#  LocalWords:  shadowType viewport newButtonWithoutPadding getFontYCoordinate
#  LocalWords:  fontSize xmlrpclib ServerProxy getVersion getAria versionList
#  LocalWords:  getCommandOutputFirstLine pkgs len preStr matchStr restStr
#  LocalWords:  BBBB setMarkup activeMarkup normalMarkup setCursor eventbox
#  LocalWords:  setDefaultCursor resetAfterClick setCustomizeClickableCursor
#  LocalWords:  cursorPath setCustomizeCursor runCommand subprocess touchFile
#  LocalWords:  filepath makedirs getDefaultLanguage lang getdefaultlocale iter
#  LocalWords:  setHelpTooltip helpText showHelpTooltip treeview toplevel
#  LocalWords:  treeViewGetToplevelNodeCount treeViewGetSelectedPath treePaths
#  LocalWords:  treeViewFocusFirstToplevelNode treeViewFocusLastToplevelNode
#  LocalWords:  nodeCount treeViewFocusNextToplevelNode selectedPath removeFile
#  LocalWords:  treeViewFocusPrevToplevelNode
