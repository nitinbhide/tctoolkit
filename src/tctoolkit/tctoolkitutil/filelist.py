'''
filelist.py
Utility functions to get the filelist for a given match patterns or from given directory etc.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''

import fnmatch
import re
import os
import string
import logging
import sys

__all__ = ['DirFileLister', 'FindFileInPathList']


class DirFileLister(object):
    '''
    creates list of files for given directory. Matching file pattern or all files handled by pygments
    or files specific to a language etc
    '''
    IGNOREDIRS = set([u'.svn',u'.cvs', u'.hg', u'.git'])

    def __init__(self, dirname):                
        self.dirname = dirname
        #dirname is not unicode then convert it to unicode using the filesystem encoding
        if isinstance(self.dirname, str):
            self.dirname = self.dirname.decode(sys.getfilesystemencoding())
        
    def RemoveIgnoreDirs(self, dirs):
        '''
        remove directories in the IGNOREDIRS list from the 'dirs'. Update
        same 'input' variable. Since 'dirs' variable may have come from the os.walk. Hence
        it is important to change the same variable.
        '''
        dirs2 = list(set(dirs) - DirFileLister.IGNOREDIRS)    
        dirs[:] = dirs2    

    def getFileList(self):
        '''
        return list of files (including files in subdirectories)
        '''
        rawfilelist = []
        #prepare list of all files ignore the directories defined in 'ignoredirs' list.
        def errfunc(err):
            logging.warn(err.message)
            print err

        for root, dirs, files in os.walk(self.dirname,topdown=True, onerror=errfunc):
            self.RemoveIgnoreDirs(dirs)
            logging.info("searching directory %s" % root)
            for fname in files:
                rawfilelist.append(os.path.join(root, fname))
        return(rawfilelist)

    
    def getMatchingFiles(self, patterns):
        '''
        Get list of files matching to 'patterns' in directory 'dirname'.
        patterns : list (or iterable) of fnmatch patterns
        '''
        if isinstance(patterns, basestring):
            #pattern is a single string. Make it into a list
            patterns = [patterns]

    
        #combine the match patterns to a single regex
        matchregex = '|'.join([fnmatch.translate(pat) for pat in patterns])    
        matchregex = re.compile(matchregex)
    
        rawfilelist = self.getFileList()

        filelist = []
        for fname in rawfilelist:
            if (matchregex.match(fname) != None):
                filelist.append(fname)
        return(filelist)

    def getPygmentsFiles(self):
        '''
        Use the lexer list and file extensions from the Pygments and prepare the list of files for which
        lexers are available.
        '''
        from pygments.lexers import get_all_lexers
    
        #Prepare a list of fnmatch patterns from lexers
        fnmatchpatlist = []
        for lexer in get_all_lexers():
            fnmatchpatlist = fnmatchpatlist+[pat for pat in lexer[2]]

        #since one fnmatch pattern can exist in multiple lexers. We need remove duplicates from the fnmatch pattern list
        fnmatchpatlist=set(fnmatchpatlist)

        return self.getMatchingFiles(fnmatchpatlist)    

    def _getExtensionsForLang(self, lang):
        '''
        get the filename extensions for given programming language. The 'lang' is short name/alias used by Pygments
        '''
        from pygments.lexers import get_lexer_by_name

        filepats = []
        try:
            lexer = get_lexer_by_name(lang)
            filepats = lexer.filenames
            #create an copy of filepatterns with 'all upper case' and 'all lowercase' pattern as well
            filepats = filepats + map(string.lower, filepats) + map(string.upper, filepats)
            #remove the duplicates
            filepats = list(set(filepats))
        except Exception, exp:
            #lexer not found for the language. Return an 'empty' list
            logging.warn(exp.message)
            filepats = []
        
        return filepats

    def getFilesForLang(self, lang):
        '''
        get files for given language.
        '''
        extensions = self._getExtensionsForLang(lang)
        return self.getMatchingFiles(extensions)

        
    def getFilesForPatternOrLang(self, pattern=None, lang=None):
        '''
        get list of files for given pattern or language. if the language is given, then
        pattern is ignored.
        '''
        if( lang != None):
            filelist = self.getFilesForLang(lang)
        elif( pattern =='' or pattern ==None):
            filelist = self.getPygmentsFiles()
        else:
            filelist = self.getMatchingFiles(pattern)
        return filelist

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

#############################
# temporary for backward compatibility
def GetDirFileList(dirname):
    filelister = DirFileLister(dirname)
    return filelister.getFileList()

def PreparePygmentsFileList(dirname):
    filelister = DirFileLister(dirname)
    return filelister.getPygmentsFiles()


