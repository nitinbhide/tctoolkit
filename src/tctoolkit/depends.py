'''
analyze the dependencies of individual source files. Calculates various metrics.
Uses Pygments to quickly parse source files.
'''

import os
import fnmatch
from tctoolkitutil.common import GetDirFileList, FindFileInPathList
from pygments.filter import simplefilter,Filter
from pygments.lexers import get_lexer_for_filename
from pygments.token import Token, is_token_subtype

class CppImportFilter(Filter):
    def __init__(self):
        Filter.__init__(self)
        pass
    
    def filter(self, lexer, stream):
        for ttype, value in stream:
            if ttype in Token.Comment.Preproc and value.startswith('include'):
                value = value[len('include'):]
                value = value.strip()
                #exclude the " or <>"
                value = value[1:-1]
                yield ttype, value

def stripSrcDir(fname, srcdir):
    if( fname.startswith(srcdir)):
        fname = fname[len(srcdir):]
    return(fname)    
    
def findFileDependencies(srcfile, pathlist):
    lexer = get_lexer_for_filename(srcfile,stripall=True)
    filter = CppImportFilter()
    lexer.add_filter(filter)
    dependList = set()
    
    with open(srcfile,"r") as code:
        for ttype, value in lexer.get_tokens(code.read()):
            dependList.add(value)
    return(dependList)

def findDependency(srcdir, filelist,pathlist):
    dependDict = dict()
    for srcfile in filelist:
        dependlist = findFileDependencies(srcfile, pathlist)
        if( len(dependlist) > 0):
            srcfile = stripSrcDir(srcfile, srcdir)
            assert(srcfile not in dependDict)
            dependDict[srcfile] = dependlist
        
    return(dependDict)

def PrintFileDependency(srcdir, fname, dependDict, pathlist, level=1):
    dependlist = dependDict.get(fname, set())
    
    if(len(dependlist) == 0):    
        fname = FindFileInPathList(fname, pathlist)
        if( fname != None):
            fname = stripSrcDir(fname, srcdir)
            dependlist = dependDict.get(fname, set())
            
    ncount = len(dependlist)
            
    for dependon in dependlist:
        print "%s%s" % ('\t'*level, dependon)
        ncount = ncount + PrintFileDependency(srcdir, dependon, dependDict, pathlist, level+1)
    return(ncount)

def PrintDependency(srcdir, dependDict,pathlist):
    print "Number of files : %d" % len(dependDict)
    
    for fname, dependlist in dependDict.iteritems():
        print "file <%s> : " % (fname)
        ncount = PrintFileDependency(srcdir, fname, dependDict,pathlist)
        print "\tdepends on %d files\n" % (ncount)
        
def RunMain():
    dirname = "E:\\users\\nitinb\\sources\\tctools\\test\\apache_httpd"
    #dirname = sys.argv[1]
    pathlist = ["E:\\users\\nitinb\\sources\\tctools\\test\\apache_httpd\\include"]
    rawfilelist = GetDirFileList(dirname)
    filelist = fnmatch.filter(rawfilelist,'*.cpp')
    filelist += fnmatch.filter(rawfilelist,'*.cxx')
    filelist += fnmatch.filter(rawfilelist,'*.h')
    filelist += fnmatch.filter(rawfilelist,'*.hpp')
    dependDict = findDependency(dirname, filelist, pathlist)
    PrintDependency(dirname, dependDict,pathlist)
    
    
if __name__ == "__main__":
    RunMain()