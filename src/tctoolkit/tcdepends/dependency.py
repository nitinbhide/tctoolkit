'''
dependency.py
Defines utility class for extracting dependencies for various types of source files.
'''

import os,sys
import fnmatch
from pygments.lexers import get_lexer_for_filename

from tctoolkitutil.common import GetDirFileList, StripAtStart
from tcdepends.depfilter import get_import_filter
    

class Dependency:
    langSrcFileExten = { 'cpp':['c','cpp', 'cxx', 'hpp', 'h', 'hxx'],
                         'java': ['java'],
                         'c#':['cs']
                         }
    
    def __init__(self, language, dependspath=[]):
        self.dependencypath = dependspath
        self.language = language
        self.srcdir = None

    def getFileDependencies(self, srcfile):
        lexer = get_lexer_for_filename(srcfile,stripall=True)
        filter = get_import_filter(lexer, self.srcdir, self.dependencypath)
        dependList = set()

        if( filter != None):
            lexer.add_filter(filter)
        
            with open(srcfile,"r") as code:
                for ttype, value in lexer.get_tokens(code.read()):
                    dependson = filter.findFile(value)
                    dependList.add(dependson)
        else:
            print >> sys.stderr, "dependency filter not found for %s" % lexer.name
        
        return(dependList)

    def __getDependency(self, filelist):
        dependDict = dict()
        for srcfile in filelist:
            dependlist = self.getFileDependencies(srcfile)
            if( len(dependlist) > 0):
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
            ncount = self.__printFileDependency(fname, dependDict,uniqueList, recursedetect,level=1)
            print "\tdepends on %d unique files\n" % (ncount)

    def __printFileDependency(self, fname, dependDict, uniquelist,recursetest, level=1):
        recursetest.add(fname)                            

        dependlist = dependDict.get(fname, set())                
        ncount = len(dependlist)
        for dependon in dependlist:
            assert(fname != dependon)
            uniquelist.add(dependon)
            print "%s%s" % ('\t'*level, dependon),
                
            if( dependon in recursetest):
                #found a recursive dependency.
                print " - RECURSIVE"
            else:
                print
                ncount = ncount + self.__printFileDependency(dependon, dependDict, uniquelist, recursetest,level+1)
        recursetest.remove(fname)
            
        return(ncount)

    def getDependency(self, srcdir):
        self.srcdir = srcdir
        if( self.srcdir.endswith(os.sep) == False):
            self.srcdir  += os.sep
        filelist = GetDirFileList(self.srcdir )
        filelist = self.__filterFileList(filelist)
        dependDict = self.__getDependency(filelist)
        return(dependDict)
        
    def printDependency(self, srcdir):
        dependDict = self.getDependency(srcdir)
        self.__printDependency(dependDict)
        
    def __filterFileList(self, rawfilelist):
        '''
        get fnmatch file pattern for given language. Currently supported language are
        'cpp' (for both 'c' and 'c++'), 'java' (for java)
        '''
        language = self.language.lower()
        filelist = []
        
        extnList = Dependency.langSrcFileExten.get(language, None)
        if( extnList != None):
            for extn in extnList:
                extn = '*.' + extn
                filelist += fnmatch.filter(rawfilelist,extn)
                
        return(filelist)
    
    
