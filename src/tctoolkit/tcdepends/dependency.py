'''
dependency.py
Defines utility class for extracting dependencies for various types of source files.
'''

import os
import sys
import codecs

from pygments.lexers import get_lexer_by_name

from tctoolkitutil.filelist import DirFileLister
from tctoolkitutil.common import StripAtStart

from tcdepends.depfilter import get_import_filter


class Dependency(object):

    def __init__(self, language, dependspath=[]):
        self.dependencypath = dependspath
        self.language = language
        self.srcdir = None
        self.lexer = get_lexer_by_name(language)
        self.filter = get_import_filter(
            self.lexer, self.srcdir, self.dependencypath)
        assert(self.filter != None)

        self.lexer.add_filter(self.filter)

    def getFileDependencies(self, srcfile):
        dependList = set()
        assert(self.filter != None)

        with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
            for ttype, value in self.lexer.get_tokens(code.read()):
                dependson = self.filter.findFile(value)
                dependList.add(dependson)

        return(dependList)

    def __getDependency(self, filelist):
        dependDict = dict()
        for srcfile in filelist:
            dependlist = self.getFileDependencies(srcfile)
            if(len(dependlist) > 0):
                assert(srcfile not in dependDict)
                srcfile = StripAtStart(srcfile, self.srcdir)
                dependDict[srcfile] = dependlist

        return(dependDict)

    def __printDependency(self, dependDict):
        print "Number of files : %d" % len(dependDict)

        for fname, dependlist in dependDict.iteritems():
            print "file <%s> : " % (fname)
            uniqueList = set()
            recursedetect = set()
            ncount = self.__printFileDependency(
                fname, dependDict, uniqueList, recursedetect, level=1)
            print "\tdepends on %d unique files\n" % (ncount)

    def __printFileDependency(self, fname, dependDict, uniquelist, recursetest, level=1):
        recursetest.add(fname)

        dependlist = dependDict.get(fname, set())
        ncount = len(dependlist)
        for dependon in dependlist:
            assert(fname != dependon)
            uniquelist.add(dependon)
            print "%s%s" % ('\t' * level, dependon),

            if(dependon in recursetest):
                # found a recursive dependency.
                print " - RECURSIVE"
            else:
                print
                ncount = ncount + \
                    self.__printFileDependency(
                        dependon, dependDict, uniquelist, recursetest, level + 1)
        recursetest.remove(fname)

        return(ncount)

    def getDependency(self, srcdir):
        self.srcdir = srcdir
        if(self.srcdir.endswith(os.sep) == False):
            self.srcdir += os.sep
        filelister = DirFileLister(self.srcdir)
        filelist = filelister.getFilesForLang(self.language)
        dependDict = self.__getDependency(filelist)
        return(dependDict)

    def printDependency(self, srcdir):
        dependDict = self.getDependency(srcdir)
        self.__printDependency(dependDict)
