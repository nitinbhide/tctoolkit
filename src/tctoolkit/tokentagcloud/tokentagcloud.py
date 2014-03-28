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

from pygments.token import Token

from tctoolkitutil import DirFileLister
from tctoolkitutil import TagCloud
from tctoolkitutil import SourceCodeTokenizer
from tctoolkitutil import TagTypeFilter, KeywordFilter, NameFilter, ClassFuncNameFilter, FuncNameFilter, ClassNameFilter

class TagCloudTokenizer(SourceCodeTokenizer):
    '''
    create tokenizer useful for tag cloud generation. (ignore comments, single character variable names, etc)
    '''
    def __init__(self, srcfile, ignore_comments=True):
        super(TagCloudTokenizer, self).__init__(srcfile)
        self.ignore_comments = ignore_comments

    def ignore_type(self, srctoken):
        ignore = False
        if(self.ignore_comments==True and srctoken.is_type(Token.Comment)):
            ignore=True
        elif( srctoken.is_type(Token.Operator) or srctoken.is_type(Token.Punctuation)):
            ignore = True
        elif( srctoken.value ==''):
            ignore=True
        elif( (srctoken.is_type(Token.Name) or srctoken.is_type(Token.Literal)) and len(srctoken.value) < 2):
            ignore=True        
        return(ignore)

    def update_type(self, srctoken, prevtoken):
        '''
        update the token type based on the previous token value. 
        Useful for detecting class names in languages like c++ or java, c#. Typically for strings
        like 'new A()' , A is detected as 'function' as determined by pygments.
        '''
        if prevtoken != None and prevtoken.ttype in Token.Keyword and prevtoken.value == 'new' and srctoken.is_type(Token.Name):
            srctoken.ttype = Token.Name.Class


class SourceCodeTagCloud(object):
    '''
    wrapper class for generating the data for source code tag cloud
    '''
    def __init__(self, dirname, pattern='*.c', lang=None):
        self.dirname = dirname
        self.pattern = pattern
        self.lang = lang
        self.tagcloud = None #Stores frequency of tag cloud.
        self.fileTagCount = dict() #Store information about how many files that tag was found
        self.createTagCloud()
        
        
    def createTagCloud(self):
        self.tagcloud = TagCloud()
    
        dirlister= DirFileLister(self.dirname)    
        for fname in dirlister.getFilesForPatternOrLang(pattern= self.pattern, lang=self.lang):
            self.__addFile(fname)
        
    def __addFile(self, srcfile):
        assert(self.tagcloud != None)
        print "Adding tags information of file: %s" % srcfile
        tokenizer = TagCloudTokenizer(srcfile)
        fileTokenset = set()
        for srctoken in tokenizer:
            value = srctoken.value
            self.tagcloud.addWord(value,srctoken.ttype)
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

