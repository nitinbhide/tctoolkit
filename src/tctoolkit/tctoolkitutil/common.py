'''
common.py
Common utility functions required for the other modules.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import fnmatch
import os
import string
import sys
from contextlib import contextmanager

IGNOREDIRS = ['.svn','.cvs'] 

@contextmanager
def FileOrStdout(filename):
    output = sys.stdout
    if( filename != None):        
        try:
            output = open(filename, "w")
        except:
            pass
    yield(output)
    if( output != sys.stdout):
        output.close()
    
def RemoveIgnoreDirs(dirs):
    for ignoredir in IGNOREDIRS:
        if ignoredir in dirs:
            dirs.remove(ignoredir)            
    return(dirs)

def GetDirFileList(dirname):
    rawfilelist = []
    #prepare list of all files ignore the directories defined in 'ignoredirs' list.
    for root, dirs, files in os.walk(dirname):
        dirs = RemoveIgnoreDirs(dirs)
        for fname in files:
            rawfilelist.append(os.path.join(root, fname))
    return(rawfilelist)

def PreparePygmentsFileList(dirname):
    '''
    Use the lexer list and file extensions from the Pygments and prepare the list of files for which
    lexers are available.
    '''
    from pygments.lexers import get_all_lexers
    import fnmatch

    #Prepare a list of fnmatch patterns from lexers
    fnmatchpatlist = []
    for lexer in get_all_lexers():
        fnmatchpatlist = fnmatchpatlist+[pat for pat in lexer[2]]

    rawfilelist = GetDirFileList(dirname)

    #since one fnmatch pattern can exist in multiple lexers. We need remove duplicates from the fnmatch pattern list
    fnmatchpatlist=set(fnmatchpatlist)
    
    filelist = []
    for fname in rawfilelist:
        for pattern in fnmatchpatlist:
            if(fnmatch.fnmatch(fname,pattern)):
                filelist.append(fname)
                #match is found.now break out of pattern matching loop
                #but continue the outer loop
                break
    return(filelist)

def FindFileInPathList(fname, pathlist, extList=None):
    '''
    search the directories in 'pathlist' one by one to see if fname exists in that
    directory. Search inside a directory is NOT recursive. First 'hit' is returned.
    '''
    patternList = []
    if( extList != None and len(extList) > 0):
        for exten in extList:
            if( exten.startswith('.') == False):
                exten = '.' + exten
            patternList.append(fname + exten)
    else:
        patternList.append(fname)

    
    for fpath in pathlist:
        for pattern in patternList:
            testfname = os.path.join(fpath, pattern)        
            if( os.path.exists(testfname)):
                return(testfname)
    return(None)

def StripAtStart(src, strtostrip):
    if( src.startswith(strtostrip)):
        src = src[len(strtostrip):]
    return(src)    
