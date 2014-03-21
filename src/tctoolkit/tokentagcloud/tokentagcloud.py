'''
Token Tag Cloud
Create tag cloud of tokens used in source files. Tag size is based on the number of times token is used
and tag color is based on the type of token.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import operator
import math
import string

from tctoolkitutil.common import *
from tctoolkitutil import TagCloud
from tctoolkitutil import SourceCodeTokenizer
from tctoolkitutil import TagTypeFilter, KeywordFilter, NameFilter, ClassFuncNameFilter, FuncNameFilter, ClassNameFilter

class SourceCodeTagCloud(object):
    '''
    wrapper class for generating the data for source code tag cloud
    '''
    def __init__(self, dirname, pattern):
        self.dirname = dirname
        self.pattern = pattern
        self.tagcloud = None #Stores frequency of tag cloud.
        self.fileTagCount = dict() #Store information about how many files that tag was found
        self.createTagCloud()
        
        
    def createTagCloud(self):
        flist = GetDirFileList(self.dirname)    
        self.tagcloud = TagCloud()
    
        for fname in flist:
            if fnmatch.fnmatch(fname,self.pattern):
                self.__addFile(fname)        
        
    def __addFile(self, srcfile):
        assert(self.tagcloud != None)
        print "Adding tags information of file: %s" % srcfile
        tokenizer = SourceCodeTokenizer(srcfile)
        fileTokenset = set()
        for ttype, value in tokenizer:
            self.tagcloud.addWord((value,ttype))            
            if value not in fileTokenset:
                self.fileTagCount[value] = self.fileTagCount.get(value, 0)+1
                fileTokenset.add(value)
    
    def getTags(self, numWords=100, filterFunc=None):
        return self.tagcloud.getSortedTagWordList(numWords, filterFunc)
    
    def getFileCount(self, tagWord):
        return self.fileTagCount.get(tagWord, 0)
    
    
def KeywordTagCloud(dirname, pattern):
    tagcld = CreateTagCloud(dirname, pattern)            
    taghtml = tagcld.getTagCloudHtml(filterFunc=KeywordFilter)
    return(taghtml)

def NameTagCloud(dirname, pattern):
    tagcld = CreateTagCloud(dirname, pattern)    
    taghtml = tagcld.getTagCloudHtml(filterFunc=NameFilter)
    
    return(taghtml)

