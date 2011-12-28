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
from pprint import pprint
from utils import *
import Queue as Q
import apt
import apt_pkg
import errno
import glib
import hashlib
import optparse
import os.path
import subprocess
import sys
import textwrap
import threading as td
import time
import urllib
import urllib2
import utils
import xmlrpclib

(ARIA2_MAJOR_VERSION, ARIA2_MINOR_VERSION, _) = utils.getAria2Version()

class Download(td.Thread):
    def __init__(self, pkgName, rpcListenPort, updateCallback, finishCallback, messageCallback):
        # Init.
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        
        self.cache = apt.Cache()
        self.pkgName = pkgName
        self.rpcListenPort = rpcListenPort
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback
        self.messageCallback = messageCallback
        self.server = xmlrpclib.ServerProxy('http://localhost:%s/rpc' % (self.rpcListenPort))
        self.downloadStatus = {}
        self.totalLength = 0
        self.cacheLength = 0
        self.progress = 0
        self.archiveDir = apt_pkg.config.find_dir('Dir::Cache::Archives')
        self.partialDir = os.path.join(self.archiveDir, "deepin_software_center_cache", pkgName)
        self.retryTicker = 0    # retry ticker
        self.updateInterval = 1 # in seconds
        self.signalChannel = Q.Queue()
        self.maxConcurrentDownloads = 50 # maximum number of parallel downloads for every static (HTTP/FTP) URI,
                                         # torrent and metalink.
        self.metalinkServers = 5         # the number of servers to connect to simultaneously
        self.maxConnectionPerServer = 10 # the maximum number of connections to one server for each download
        self.minSplitSize = "1M"         # minimum split size (1M - 1024M)
        self.maxOverallDownloadLimit = "100K" # max overall download speed in bytes/sec
        self.autoSaveInterval = 10       # time to auto save progress, in seconds
        if not self.archiveDir:
            raise Exception(('No archive dir is set.'
                             ' Usually it is /var/cache/apt/archives/'))
    
    def run(self):
        '''Run'''
        # Build command line.
        cmdline = ['aria2c',
                   '--dir=%s' % (self.partialDir),
                   '--file-allocation=none',
                   '--auto-file-renaming=false',
                   '--summary-interval=0',
                   '--remote-time=true',
                   '--auto-save-interval=%s' % (self.autoSaveInterval),
                   '--max-concurrent-downloads=%s' % (self.maxConcurrentDownloads),
                   '--metalink-servers=%s' % (self.metalinkServers),
                   '--check-integrity=true',
                   '--disable-ipv6=true',
                   # '--max-overall-download-limit=%s' % (self.maxOverallDownloadLimit),
                   ]
        
        # Compatible with aria2c 1.12.x, damn Japanese, why change options every version? Damn you!
        if ARIA2_MAJOR_VERSION >= 1 and ARIA2_MINOR_VERSION >= 12:
            cmdline.append('--enable-rpc=true')
            cmdline.append('--rpc-listen-port=%s' % (self.rpcListenPort))
        else:
            cmdline.append('--enable-xml-rpc=true')
            cmdline.append('--xml-rpc-listen-port=%s' % (self.rpcListenPort))
            
        # Add `max-connection-per-server` and `min-split-size` options if aria2c >= 1.10.x.
        if ARIA2_MAJOR_VERSION >= 1 and ARIA2_MINOR_VERSION >= 10:
            cmdline.append('--max-connection-per-server=%s' % (self.maxConnectionPerServer))
            cmdline.append('--min-split-size=%s' % (self.minSplitSize))
            
        # Make software center can work with aria2c 1.9.x.
        if ARIA2_MAJOR_VERSION >= 1 and ARIA2_MINOR_VERSION <= 9:
            cmdline.append("--no-conf")
            cmdline.append("--continue")
        else:
            cmdline.append("--no-conf=true")
            cmdline.append("--continue=true")

        # Append proxy configuration.
        # proxyString = utils.parseProxyString()
        # if proxyString != None:
        #     cmdline.append("=".join(["--all-proxy", proxyString]))

        # Start child process.
        self.proc = subprocess.Popen(cmdline)
        
        # Get process result.
        result = DOWNLOAD_STATUS_FAILED
        try:
            result = self.download([self.pkgName])
            self.server.aria2.shutdown()
        except Exception, e:
            self.messageCallback((__("% s: Download failed, please check your network link.") % self.pkgName))
            self.updateCallback(self.pkgName, self.progress, __("Download failed"))
            result = DOWNLOAD_STATUS_FAILED
            print "Download error: ", e
        
        # Kill child process.
        killProcess(self.proc)
        
        print self.proc.returncode
        
        # Call callback.
        self.finishCallback(self.pkgName, result)
            
    def download(self, pkg_names):
        # Mark packages.
        for pkg_name in pkg_names:
            if pkg_name in self.cache:
                pkg = self.cache[pkg_name]
                if not pkg.installed:
                    pkg.mark_install()
                elif pkg.is_upgradable:
                    pkg.mark_upgrade()
            else:
                raise Exception('%s is not found' % pkg_name)
        return self._get_changes()

    def _get_changes(self):
        pkgs = sorted(self.cache.get_changes(), key=lambda p: p.name)
        
        if len(pkgs) != 0:
            # Get total length.
            self.totalLength = self.cache.required_download
            
            # Get packages to download.
            pkgs = [pkg for pkg in pkgs if not pkg.marked_delete and not self._file_downloaded(pkg)]
            
            # Return DOWNLOAD_STATUS_DONT_NEED haven't packages need download,  
            if len(pkgs) == 0:
                self.updateCallback(self.pkgName, 100, __("Download Finish"))
                return DOWNLOAD_STATUS_DONT_NEED
            # Otherwise download.
            else:
                return self._download(pkgs)
        else:
            # Return DOWNLOAD_STATUS_DONT_NEED if don't need download anything.
            return DOWNLOAD_STATUS_DONT_NEED
        
    def make_metalink(self, pkgs):
        '''Make metalink.'''
        lines = []
        
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<metalink xmlns="urn:ietf:params:xml:ns:metalink">')
        for pkg in pkgs:
            version = pkg.candidate
            hashtype, hashvalue = get_hash(version)
            lines.append('<file name="{0}">'.format(get_filename(version)))
            lines.append('<size>{0}</size>'.format(version.size))
            if hashtype:
                lines.append('<hash type="{0}">{1}</hash>'.format(hashtype, hashvalue))
                
            for uri in version.uris:
                # Debug.
                print "Add link %s" % (uri)

                lines.append('<url priority="1">{0}</url>'.format(uri))
                
            lines.append('</file>')
        lines.append('</metalink>')
        
        return ''.join(lines)

    def _download(self, pkgs):
        # Update status.
        self.updateCallback(self.pkgName, 0, __("Start Download"))
        
        # Make metalink.
        self.server.aria2.addMetalink(xmlrpclib.Binary(self.make_metalink(pkgs)))
        
        # Download loop.
        downloadCompleted = False
        while not downloadCompleted:
            # Sleep thread.
            time.sleep(self.updateInterval)
            
            # Stop download if reach retry times.
            if self.retryTicker > DOWNLOAD_TIMEOUT:
                self.messageCallback((__("% s: Download timeout, please check your network link.") % (self.pkgName)))
                self.updateCallback(self.pkgName, self.progress, __("Download Timeout"))
                return DOWNLOAD_STATUS_TIMEOUT
            elif self.retryTicker > 0:
                print "Retry (%s/%s)" % (self.retryTicker, DOWNLOAD_TIMEOUT)
            
            # Stop download if received signal.
            if not self.signalChannel.empty():
                signal = self.signalChannel.get_nowait()
                if signal == "STOP":
                    return DOWNLOAD_STATUS_STOP
                elif signal == "PAUSE":
                    self.updateCallback(self.pkgName, self.progress, __("Download Pause"), APP_STATE_DOWNLOAD_PAUSE)
                    return DOWNLOAD_STATUS_PAUSE
            # Otherwise wait download complete.
            else:
                # Get status list.
                statusList = self.server.aria2.tellActive()
                
                completedStatus = []
                for status in statusList:
                    gid = status['gid']
                    self.downloadStatus[gid] = int(status['completedLength'])
                    completedStatus.append(status['status'] == 'complete')
                
                # Get current download length.
                currentLength = sum(self.downloadStatus.values())
                
                # Get download speed.
                if self.cacheLength == 0:
                    downloadSpeed = 0
                else:
                    downloadSpeed = currentLength - self.cacheLength / self.updateInterval
                    
                # Store cache length.
                self.cacheLength = currentLength
                
                # Increases retry ticker if download speed is zero.
                if downloadSpeed == 0:
                    self.retryTicker += 1
                # Init retry ticker if download speed is not zero.
                else:
                    self.retryTicker = 0
                
                # Get progress.
                if self.totalLength == 0:
                    self.progress = 0
                else:
                    self.progress = int(currentLength * 100 / self.totalLength)                
                    
                # Update status.
                self.updateCallback(self.pkgName, self.progress, utils.formatFileSize(downloadSpeed) + "/s")
                
                # Whether all download complete.
                downloadCompleted = all(completedStatus)
            
        link_success = True
        # Link archives/pkgName/*.deb to archives/
        for pkg in pkgs:
            filename = get_filename(pkg.candidate)
            dst = os.path.join(self.archiveDir, filename)
            src = os.path.join(self.partialDir, filename)
            ctrl_file = ''.join([src, '.aria2'])
            # If control file exists, we assume download is not
            # complete.
            if os.path.exists(ctrl_file):
                continue
            try:
                # Making hard link because aria2c needs file in
                # partial directory to know download is complete
                # in the next invocation.
                os.rename(src, dst)
            except OSError, e:
                if e.errno != errno.ENOENT:
                    print "Failed to move archive file", e
                link_success = False
                
        # Return DOWNLOAD_STATUS_COMPLETE if link success.
        if link_success:
            self.updateCallback(self.pkgName, 100, __("Download Finish"))
            
            # Send download count to server.
            SendDownloadCount(self.pkgName).start()
            
            return DOWNLOAD_STATUS_COMPLETE
        # Otherwise return DOWNLOAD_STATUS_FAILED.
        else:
            return DOWNLOAD_STATUS_FAILED

    def _file_downloaded(self, pkg):
        # Check whether file has downloaded.
        candidate = pkg.candidate
        path = os.path.join(self.archiveDir, get_filename(candidate))
        if not os.path.exists(path) or os.stat(path).st_size != candidate.size:
            return False
        
        # Hash check.
        hash_type, hash_value = get_hash(pkg.candidate)
        try:
            return check_hash(path, hash_type, hash_value)
        except IOError, e:
            if e.errno != errno.ENOENT:
                print "Failed to check hash", e
                self.messageCallback((__("%s checkout failed.") % self.pkgName))
            return False
        
class SendDownloadCount(td.Thread):
    '''Send download count.'''
	
    def __init__(self, pkgName):
        '''Init for vote.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit 
        self.pkgName = pkgName

    def run(self):
        '''Run'''
        try:
            args = {
                'a' : 'd', 
                'n' : self.pkgName}
            
            connection = urllib2.urlopen(
                "%s/softcenter/v1/analytics" % (SERVER_ADDRESS),
                data=urllib.urlencode(args),
                timeout=POST_TIMEOUT
                )
            print "Send download count (%s) successful." % (self.pkgName)
        except Exception, e:
            print "Send download count (%s) failed." % (self.pkgName)
            print "Error: ", e

def check_hash(path, hash_type, hash_value):
    '''Check hash value.'''
    hash_fun = hashlib.new(hash_type)
    with open(path) as f:
        while 1:
            bytes = f.read(4096)
            if not bytes:
                break
            hash_fun.update(bytes)
    return hash_fun.hexdigest() == hash_value

def get_hash(version):
    '''Get hash value.'''
    if version.sha256:
        return ("sha256", version.sha256)
    elif version.sha1:
        return ("sha1", version.sha1)
    elif version.md5:
        return ("md5", version.md5)
    else:
        return (None, None)

def get_filename(version):
    '''Get file name.'''
    return os.path.basename(version.filename)

class DownloadQueue(object):
    '''Download queue'''
	
    def __init__(self, updateCallback, finishCallback, failedCallback, messageCallback):
        '''Init for download queue.'''
        # Init.
        self.maxConcurrentDownloads = 5 # max concurrent download
        self.downloadingQueue = []
        self.downloadingChannel = {}
        self.portTicker = 7000
        self.waitQueue = []
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback
        self.failedCallback = failedCallback
        self.messageCallback = messageCallback
        
    def startDownloadThread(self, pkgName):
        '''Start download thread.'''
        # Add in download list.
        utils.addInList(self.downloadingQueue, pkgName)
        
        # Start download thread.
        self.portTicker += 1 # generate new rpc listen port
        download = Download(pkgName, self.portTicker, self.updateCallback, self.finishDownloadCallback, self.messageCallback)
        download.start()
        
        # Add signal channel.
        self.downloadingChannel[pkgName] = download
        
    def addDownload(self, pkgName):
        '''Add new download'''
        if len(self.downloadingQueue) >= self.maxConcurrentDownloads:
            utils.addInList(self.waitQueue, pkgName)
        else:
            self.startDownloadThread(pkgName)
        
    def stopDownload(self, pkgName):
        '''Stop download.'''
        # Send pause signal if package at download list.
        if pkgName in self.downloadingQueue:
            if self.downloadingChannel.has_key(pkgName):
                # Pause download.
                self.downloadingChannel[pkgName].signalChannel.put('PAUSE')
            else:
                print "Impossible: downloadingChannel not key '%s'" % (pkgName)
        # Otherwise just simple remove from download queue.
        else:
            utils.removeFromList(self.waitQueue, pkgName)
            
    def finishDownloadCallback(self, pkgName, downloadStatus):
        '''Finish download, start new download if have download in queue.'''
        # Remove pkgName from download list.
        utils.removeFromList(self.downloadingQueue, pkgName)
        del self.downloadingChannel[pkgName]
                
        # Call back if download success.
        if downloadStatus in [DOWNLOAD_STATUS_COMPLETE, DOWNLOAD_STATUS_DONT_NEED]:
            self.finishCallback(pkgName)
        elif downloadStatus == DOWNLOAD_STATUS_FAILED:
            self.failedCallback(pkgName)
        elif downloadStatus == DOWNLOAD_STATUS_TIMEOUT:
            print "Download %s timeout." % (pkgName)
            self.failedCallback(pkgName)
        elif downloadStatus == DOWNLOAD_STATUS_STOP:
            print "Download %s stop." % (pkgName)
        elif downloadStatus == DOWNLOAD_STATUS_PAUSE:
            print "Download %s pause." % (pkgName)
        
        # Start new download thread if download list's length is not reach max limit.
        if len(self.downloadingQueue) < self.maxConcurrentDownloads and len(self.waitQueue) > 0:
            self.startDownloadThread(self.waitQueue.pop(0))

    def getDownloadPkgs(self):
        '''Get download packages.'''
        return self.downloadingQueue + self.waitQueue
    
    def stopAllDownloads(self):
        '''Stop all download task.'''
        for channel in self.downloadingChannel.values():
            channel.signalChannel.put('STOP')
            killProcess(channel.proc) # must kill here, otherwise aria2c process exit even send STOP signal
            
#  LocalWords:  completedLength
