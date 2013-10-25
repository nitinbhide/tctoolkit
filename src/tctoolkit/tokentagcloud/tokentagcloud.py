'''
Token Tag Cloud
Create tag cloud of tokens used in source files. Tag size is based on the number of times token is used
and tag color is based on the type of token.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

from __future__ import with_statement

from pygments.lexers import get_lexer_for_filename
from pygments.filter import simplefilter
from pygments.token import Token

import operator
import math
import string
from tctoolkitutil.common import *
from tctoolkitutil.tagcloud import TagCloud

class Tokenizer(object):
    def __init__(self, srcfile, ignore_comments=True):
        self.srcfile = srcfile
        self.tokenlist=None
        self.ignore_comments = ignore_comments
        
    def __iter__(self):
        if(self.tokenlist==None):
            self.tokenlist = [token for token in self.get_tokens()]
        return(self.tokenlist.__iter__())

    def ignore_type(self, ttype,value):
        ignore = False
        if(self.ignore_comments==True and ttype in Token.Comment ):
            ignore=True
        if( ttype in Token.Operator or ttype in Token.Punctuation):
            ignore = True
        if( ignore==False and value ==''):
            ignore=True
        if( ignore==False and ttype in Token.Name and len(value) < 2):
            ignore=True
        if( ignore == False and ttype in Token.Literal and len(value) < 2):
            ignore = True
        return(ignore)
    
    def get_tokens(self):
        pyglexer = get_lexer_for_filename(self.srcfile,stripall=True)
        
        linenum=1
        with open(self.srcfile, "r") as code:
            for charpos,ttype,value in pyglexer.get_tokens_unprocessed(code.read()):    
                newvalue = value.strip()
                if( self.ignore_type(ttype,newvalue)==False):
                    yield ttype,newvalue
                

def UpdateTagCloud(srcfile, tagcloud):        
    assert(tagcloud != None)
    tokenizer = Tokenizer(srcfile)
    for ttype, value in tokenizer:
        tagcloud.addWord((value,ttype))
    
def CreateTagCloud(dirname, pattern):
    flist = GetDirFileList(dirname)    
    tagcld = TagCloud()
    
    for fname in flist:
        if fnmatch.fnmatch(fname,pattern):
            UpdateTagCloud(fname,tagcld)
    return(tagcld)

def KeywordTagCloud(dirname, pattern):
    tagcld = CreateTagCloud(dirname, pattern)            
    taghtml = tagcld.getTagCloudHtml(filterFunc=KeywordFilter)
    return(taghtml)

def NameTagCloud(dirname, pattern):
    tagcld = CreateTagCloud(dirname, pattern)    
    taghtml = tagcld.getTagCloudHtml(filterFunc=NameFilter)
    
    return(taghtml)

'''
Filter Functions to get extract tag clouds
'''

def TagTypeFilter(taginfo, freq, tagType):
    validtag = None
    if(freq > 1 and taginfo[1] in tagType):
        validtag = (taginfo[0], freq)
    return(validtag)
    
def KeywordFilter(taginfo, freq):
    return(TagTypeFilter(taginfo, freq, Token.Keyword))    

def NameFilter(taginfo, freq):
    return(TagTypeFilter(taginfo, freq, Token.Name))    
    
def ClassNameFilter(taginfo, freq):
    return(TagTypeFilter(taginfo, freq, Token.Name.Class))    
    
def FuncNameFilter(taginfo, freq):
    return(TagTypeFilter(taginfo, freq, Token.Name.Function))

def ClassFuncNameFilter(taginfo, freq):
    validtag = ClassNameFilter(taginfo, freq)
    if( validtag == None):
        validtag = FuncNameFilter(taginfo, freq)
    return(validtag)
