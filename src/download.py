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

from constant import *
from pprint import pprint
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
import utils
import urllib2
import xmlrpclib

(ARIA2_MAJOR_VERSION, ARIA2_MINOR_VERSION, _) = utils.getAria2Version()

class Download(td.Thread):
    def __init__(self, pkgName, updateCallback, finishCallback, messageCallback):
        # Init.
        td.Thread.__init__(self)
        self.cache = apt.Cache()
        self.pkgName = pkgName
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback
        self.messageCallback = messageCallback
        self.hashCheck = True
        self.server = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
        self.downloadStatus = {}
        self.totalLength = 0
        self.cacheLength = 0
        self.progress = 0
        self.archiveDir = apt_pkg.config.find_dir('Dir::Cache::Archives')
        self.partialDir = os.path.join(self.archiveDir, 'partial')
        self.retryTicker = 0    # retry ticker
        self.updateInterval = 1 # in seconds
        self.queue = Q.Queue()
        self.maxConcurrentDownloads = 50 # maximum number of parallel downloads for every static (HTTP/FTP) URI,
                                         # torrent and metalink.
        self.metalinkServers = 5         # the number of servers to connect to simultaneously
        self.maxConnectionPerServer = 10 # the maximum number of connections to one server for each download
        self.minSplitSize = "1M"         # minimum split size (1M - 1024M)
        self.autoSaveInterval = 10       # time to auto save progress, in seconds
        if not self.archiveDir:
            raise Exception(('No archive dir is set.'
                             ' Usually it is /var/cache/apt/archives/'))
    
    def run(self):
        '''Run'''
        # Build command line.
        cmdline = ['aria2c',
                   '--file-allocation=none',
                   '--auto-file-renaming=false',
                   '--dir=%s' % (self.partialDir),
                   '--summary-interval=0',
                   '--no-conf=true',
                   '--remote-time=true',
                   '--auto-save-interval=%s' % (self.autoSaveInterval),
                   '--continue=true',
                   '--enable-xml-rpc=true',
                   '--max-concurrent-downloads=%s' % (self.maxConcurrentDownloads),
                   '--metalink-servers=%s' % (self.metalinkServers),
                   ]
        
        # Add `max-connection-per-server` and `min-split-size` options if aria2c >= 1.10.x.
        if ARIA2_MAJOR_VERSION >= 1 and ARIA2_MINOR_VERSION >= 10:
            cmdline.append('--max-connection-per-server=%s' % (self.maxConnectionPerServer))
            cmdline.append('--min-split-size=%s' % (self.minSplitSize))
        
        # Whether check hash value?
        if self.hashCheck:
            cmdline.append('--check-integrity=true')

        # Append proxy configuration.
        http_proxy = apt_pkg.config.find('Acquire::http::Proxy')
        https_proxy = apt_pkg.config.find('Acquire::https::Proxy', http_proxy)
        ftp_proxy = apt_pkg.config.find('Acquire::ftp::Proxy')

        if http_proxy:
            cmdline.append('='.join(['--http-proxy', http_proxy]))
        if https_proxy:
            cmdline.append('='.join(['--https-proxy', https_proxy]))
        if ftp_proxy:
            cmdline.append('='.join(['--ftp-proxy', ftp_proxy]))

        # Start child process.
        proc = subprocess.Popen(cmdline)
        
        # Get process result.
        result = DOWNLOAD_STATUS_FAILED
        try:
            result = self.download([self.pkgName])
            self.server.aria2.shutdown()
        except Exception, e:
            self.messageCallback("%s: 下载失败, 请检查你的网络链接." % self.pkgName)
            self.updateCallback(self.pkgName, self.progress, "下载失败")
            result = DOWNLOAD_STATUS_FAILED
            print "Download error: ", e
        
        # Kill child process.
        proc.kill()
        
        print proc.returncode
        
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
            pkgs = [pkg for pkg in pkgs if not pkg.marked_delete and not self._file_downloaded(pkg, self.hashCheck)]
            
            # Return DOWNLOAD_STATUS_DONT_NEED haven't packages need download,  
            if len(pkgs) == 0:
                self.updateCallback(self.pkgName, 100, "下载完毕")
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
        self.updateCallback(self.pkgName, 0, "开始下载")
        
        # Make metalink.
        self.server.aria2.addMetalink(xmlrpclib.Binary(self.make_metalink(pkgs)))
        
        # Download loop.
        downloadCompleted = False
        while not downloadCompleted:
            # Sleep thread.
            time.sleep(self.updateInterval)
            
            # Stop download if reach retry times.
            if self.retryTicker > DOWNLOAD_TIMEOUT:
                self.messageCallback("%s: 下载超时, 请检查你的网络链接." % (self.pkgName))
                self.updateCallback(self.pkgName, self.progress, "下载超时")
                return DOWNLOAD_STATUS_TIMEOUT
            elif self.retryTicker > 0:
                print "Retry (%s/%s)" % (self.retryTicker, DOWNLOAD_TIMEOUT)
            
            # Stop download if received signal.
            if not self.queue.empty():
                signal = self.queue.get_nowait()
                if signal == "STOP":
                    return DOWNLOAD_STATUS_STOP
                elif signal == "PAUSE":
                    self.updateCallback(self.pkgName, self.progress, "下载暂停", APP_STATE_DOWNLOAD_PAUSE)
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
                downloadSpeed = currentLength - self.cacheLength / self.updateInterval
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
        # Link archives/partial/*.deb to archives/
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
            self.updateCallback(self.pkgName, 100, "下载完毕")
            
            # Send download count to server.
            sendDownloadCountThread = SendDownloadCount(self.pkgName)
            sendDownloadCountThread.start()
            
            return DOWNLOAD_STATUS_COMPLETE
        # Otherwise return DOWNLOAD_STATUS_FAILED.
        else:
            return DOWNLOAD_STATUS_FAILED

    def _file_downloaded(self, pkg, hashCheck=False):
        # Check whether file has downloaded.
        candidate = pkg.candidate
        path = os.path.join(self.archiveDir, get_filename(candidate))
        if not os.path.exists(path) or os.stat(path).st_size != candidate.size:
            return False
        if hashCheck:
            hash_type, hash_value = get_hash(pkg.candidate)
            try:
                return check_hash(path, hash_type, hash_value)
            except IOError, e:
                if e.errno != errno.ENOENT:
                    print "Failed to check hash", e
                    self.messageCallback("%s: 校验失败." % self.pkgName)
                return False
        else:
            return True
        
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
            urllib2.urlopen("http://test-linux.gteasy.com/down.php?n=" + self.pkgName, timeout=POST_TIMEOUT)
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

class DownloadQueue:
    '''Download queue'''
	
    def __init__(self, updateCallback, finishCallback, failedCallback, messageCallback):
        '''Init for download queue.'''
        # Init.
        self.lock = False
        self.queue = []
        self.pkgName = None
        self.downloadQueue = None
        self.updateCallback = updateCallback
        self.finishCallback = finishCallback
        self.failedCallback = failedCallback
        self.messageCallback = messageCallback
        
    def startDownloadThread(self, pkgName):
        '''Start download thread.'''
        # Lock first.
        self.lock = True
        
        # Init.
        self.pkgName = pkgName
        
        # Start download thread.
        download = Download(pkgName, self.updateCallback, self.finishDownload, self.messageCallback)
        download.start()
        
        # Get download queue.
        self.downloadQueue = download.queue
        
    def addDownload(self, pkgName):
        '''Add new download'''
        # Add in queue if download is lock.
        if self.lock:
            self.queue.append(pkgName)
        # Otherwise start new download thread.
        else:
            self.startDownloadThread(pkgName)

    def stopDownload(self, pkgName):
        '''Stop download.'''
        # Send pause signal if match current download one.
        if self.pkgName == pkgName and self.downloadQueue != None:
            self.downloadQueue.put('PAUSE')
        # Otherwise just simple remove from download queue.
        elif pkgName in self.queue:
            self.queue.remove(pkgName)
            
    def finishDownload(self, pkgName, downloadStatus):
        '''Finish download, start new download if have download in queue.'''
        # Remove finish download from queue.
        if pkgName in self.queue:
            self.queue.remove(pkgName)
            
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
        
        # Start new download thread if queue is not empty.
        if len(self.queue) > 0:
            self.startDownloadThread(self.queue.pop(0))
        # Otherwise release download lock.
        else:
            self.lock = False
            self.pkgName = None

    def getDownloadPkgs(self):
        '''Get download packages.'''
        if self.pkgName == None:
            return self.queue
        else:
            return self.queue + [self.pkgName]
     
