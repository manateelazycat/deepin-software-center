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

from ConfigParser import RawConfigParser
from lang import __, getDefaultLanguage
from utils import *
import axi
import glib
import os, re
import subprocess
import sys
import threading as td
import xapian

XDG_CACHE_HOME = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
CACHEFILE = os.path.join(XDG_CACHE_HOME, "axi-cache.state")

class DB(object):
    class BasicFilter(xapian.ExpandDecider):
        def __init__(self, stemmer=None, exclude=None, prefix=None):
            super(DB.BasicFilter, self).__init__()
            self.stem = stemmer if stemmer else lambda x:x
            self.exclude = set([self.stem(x) for x in exclude]) if exclude else set()
            self.prefix = prefix
        def __call__(self, term):
            if len(term) < 4: return False
            if self.prefix is not None:
                # Skip leading uppercase chars
                t = term
                while t and t[0].isupper():
                    t = t[1:]
                if not t.startswith(self.prefix):
                    return False
            if self.stem(term) in self.exclude: return False
            if term.startswith("XT") or term.startswith("XS"): return True
            return term[0].islower()

    class TermFilter(BasicFilter):
        def __call__(self, term):
            if len(term) < 4: return False
            if self.stem(term) in self.exclude: return False
            return term[0].islower()

    class TagFilter(xapian.ExpandDecider):
        def __call__(self, term):
            return term.startswith("XT")

    def __init__(self):
        # Access the Xapian index
        self.db = xapian.Database(axi.XAPIANINDEX)

        self.stem = xapian.Stem("english")

        # Build query parser
        self.qp = xapian.QueryParser()
        self.qp.set_default_op(xapian.Query.OP_AND)
        self.qp.set_database(self.db)
        self.qp.set_stemmer(self.stem)
        self.qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
        self.qp.add_prefix("pkg", "XP")
        self.qp.add_boolean_prefix("tag", "XT")
        self.qp.add_boolean_prefix("sec", "XS")

        #notmuch->value_range_processor = new Xapian::NumberValueRangeProcessor (NOTMUCH_VALUE_TIMESTAMP);
        #notmuch->query_parser->add_valuerangeprocessor (notmuch->value_range_processor);

        # Read state from previous runs
        self.cache = RawConfigParser()
        if os.path.exists(CACHEFILE):
            try:
                self.cache.read(CACHEFILE)
            except Error, e:
                print >>sys.stderr, e
                print >>sys.stderr, "ignoring %s which seems to be corrupted" % CACHEFILE

        self.dirty = False
        self.facets = None
        self.tags = None

    def save(self):
        "Save the state so we find it next time"
        if self.dirty:
            if not os.path.exists(XDG_CACHE_HOME):
                os.makedirs(XDG_CACHE_HOME, mode=0700)
            self.cache.write(open(CACHEFILE, "w"))
            self.dirty = False

    def vocabulary(self):
        if self.facets is None:
            self.facets, self.tags = readVocabulary()
        return self.facets, self.tags

    def unprefix(self, term):
        "Convert DB prefixes to user prefixes"
        if term.startswith("XT"):
            return "tag:" + term[2:]
        elif term.startswith("XS"):
            return "sec:" + term[2:]
        elif term.startswith("XP"):
            return "pkg:" + term[2:]
        return term

    def is_tag(self, t):
        return self.db.term_exists("XT" + t)

    def set_query_args(self, args, secondary=False):
        def term_or_tag(t):
            if "::" in t and self.is_tag(t):
                return "tag:" + t
            else:
                return t
        args = map(term_or_tag, args)
        self.set_query_string(" ".join(args), secondary=secondary)

    def set_query_string(self, q, secondary=False):
        "Set the query in the cache"
        if not secondary:
            self.set_cache_last("query", q)
            self.unset_cache_last("secondary query")
        else:
            self.set_cache_last("secondary query", q)
        self.unset_cache_last("skip")

    def set_sort(self, key=None, cutoff=60):
        "Set sorting method (default is by relevance)"
        if key is None:
            self.unset_cache_last("sort")
            self.unset_cache_last("cutoff")
        else:
            self.set_cache_last("sort", key)
            self.set_cache_last("cutoff", str(cutoff))
        self.unset_cache_last("skip")

    def build_query(self):
        "Build query from cached query info"
        q = self.get_cache_last("query")
        if not self.cache.has_option("last", "query"):
            raise SavedStateError("no saved query")
        self.query = self.qp.parse_query(q,
                xapian.QueryParser.FLAG_BOOLEAN |
                xapian.QueryParser.FLAG_LOVEHATE |
                xapian.QueryParser.FLAG_BOOLEAN_ANY_CASE |
                xapian.QueryParser.FLAG_WILDCARD |
                xapian.QueryParser.FLAG_PURE_NOT |
                xapian.QueryParser.FLAG_SPELLING_CORRECTION |
                xapian.QueryParser.FLAG_AUTO_SYNONYMS)

        secondary = self.get_cache_last("secondary query", None)
        if secondary:
            secondary = self.qp.parse_query(secondary,
                xapian.QueryParser.FLAG_BOOLEAN |
                xapian.QueryParser.FLAG_LOVEHATE |
                xapian.QueryParser.FLAG_BOOLEAN_ANY_CASE |
                xapian.QueryParser.FLAG_WILDCARD |
                xapian.QueryParser.FLAG_PURE_NOT |
                xapian.QueryParser.FLAG_SPELLING_CORRECTION |
                xapian.QueryParser.FLAG_AUTO_SYNONYMS)
            self.query = xapian.Query(xapian.Query.OP_AND, self.query, secondary)

        # print "Query:", self.query

        # Build the enquire with the query
        self.enquire = xapian.Enquire(self.db)
        self.enquire.set_query(self.query)

        sort = self.get_cache_last("sort")
        if sort is not None:
            values, descs = axi.readValueDB()

            # If we don't sort by relevance, we need to specify a cutoff in order to
            # remove poor results from the output
            #
            # Note: apt-cache implements an adaptive cutoff as follows:
            # 1. Retrieve only one result, with default sorting.  Read its relevance as
            #    the maximum relevance.
            # 2. Set the cutoff as some percentage of the maximum relevance
            # 3. Set sort by the wanted value
            # 4. Perform the query
            # TODO: didn't this use to work?
            #self.enquire.set_cutoff(int(self.get_cache_last("cutoff", 60)))

            # Sort by the requested value
            self.enquire.set_sort_by_value(values[sort])

    def get_spelling_correction(self):
        return self.qp.get_corrected_query_string()

    def get_suggestions(self, count=10, filter=None):
        """
        Compute suggestions for more terms

        Return a Xapian ESet
        """
        # Use the first 30 results as the key ones to use to compute relevant
        # terms
        rset = xapian.RSet()
        for m in self.enquire.get_mset(0, 30):
            rset.add_document(m.docid)

        # Get results, optionally filtered
        if filter is None:
            filter = self.BasicFilter()

        return self.enquire.get_eset(count, rset, filter)

    # ConfigParser access wrappers with lots of extra ifs, needed because the
    # ConfigParser API has been designed to throw exceptions in the most stupid
    # places one could possibly conceive

    def get_cache_last(self, key, default=None):
        if self.cache.has_option("last", key):
            return self.cache.get("last", key)
        return default

    def set_cache_last(self, key, val):
        if not self.cache.has_section("last"):
            self.cache.add_section("last")
        self.cache.set("last", key, val)
        self.dirty = True

    def unset_cache_last(self, key):
        if not self.cache.has_section("last"):
            return
        self.cache.remove_option("last", key)
        
class Search(object):
    '''Search.'''
	
    def __init__(self, repoCache, messageCallback, statusbar):
        '''Init search.'''
        self.repoCache = repoCache
        self.lockFile = "./firstLock"    
        self.messageCallback = messageCallback
        self.statusbar = statusbar
        
        if os.path.exists(self.lockFile):
            self.database = DB()
        else:
            # Init.
            self.database = None
            self.statusbar.setStatus((__("Files are indexed for the search ...")))
            
            # Start rebuild thread.
            rebuildSearchIndex = RebuildSearchIndex(self.initDB)
            rebuildSearchIndex.start()
            
    @postGUI
    def initDB(self):
        '''Init DB.'''
        self.database = DB()
        self.statusbar.setStatus((__("Build the search index file is completed.")))
        
        # Touch lock file.
        if not os.path.exists(self.lockFile):
            touchFile(self.lockFile)
        
        glib.timeout_add_seconds(2, self.resetStatus)
        
    def resetStatus(self):
        '''Reseet status.'''
        self.statusbar.initStatus()
    
        return False
        
    def query(self, args):
        '''Query.'''
        if self.database == None:
            self.messageCallback((__("Indexing, search capabilities please try again later.")))
            return []
        else:
            self.database.set_query_args(args)
            self.database.build_query()
            
            matches = self.database.enquire.get_mset(0, self.database.db.get_doccount())
            results = map(lambda m: m.document.get_data(), matches)
            
            if results == []:
                self.messageCallback((__("No search packages related %s") % (" ".join(args))))
            
            return self.repoCache.sortPackages(results, " ".join(args))
    
class RebuildSearchIndex(td.Thread):
    '''Rebuild search index.'''
	
    def __init__(self, finishCallback):
        '''Init for RebuildSearchIndex.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit
        
        self.finishCallback = finishCallback

    def run(self):
        '''Run.'''
        try:
            subprocess.call(["update-apt-xapian-index"])
            self.finishCallback()
        except Exception, e:
            print "RebuildSearchIndex error."
        
if __name__ == "__main__":
    search = Search()
    result = search.query(["python"])
    print result
    print len(result)

#  LocalWords:  XT XP notmuch TIMESTAMP valuerangeprocessor ESet ConfigParser
#  LocalWords:  API firstLock Reseet messageCallback RebuildSearchIndex td
#  LocalWords:  finishCallback setDaemon
