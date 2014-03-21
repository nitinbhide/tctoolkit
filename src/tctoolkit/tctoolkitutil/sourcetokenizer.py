'''
Source Code Tokenizer

Parses various source code files using the Pygments and returns a stream of 'tokens'. To be used by
code duplication detector, token tag cloud etc.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''
import os.path

from pygments.lexers import get_lexer_for_filename
from pygments.filter import simplefilter
from pygments.token import Token

class SourceCodeTokenizer(object):
    '''
    tokenizing the source files
    '''
    __LEXERS_CACHE = dict() #dictionary of lexers keyed by file extensions
    
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
        pyglexer = self.get_lexer()
        
        linenum=1
        with open(self.srcfile, "r") as code:
            for charpos,ttype,value in pyglexer.get_tokens_unprocessed(code.read()):    
                newvalue = value.strip()
                if( self.ignore_type(ttype,newvalue)==False):
                    yield ttype,newvalue

    def get_lexer(self):
        '''
        return lexer for self.srcfile
        '''
        return SourceCodeTokenizer.get_lexer_for(self.srcfile)

    @classmethod
    def get_lexer_for(selfcls, filename):
        '''
        search lexer in the lexers list first based on the file extension.
        if it not there then call the get_lexer_for_filename
        '''
        name, extension = os.path.splitext(filename)
        if(extension not in SourceCodeTokenizer.__LEXERS_CACHE):
            pyglexer = get_lexer_for_filename(filename,stripall=True)
            SourceCodeTokenizer.__LEXERS_CACHE[extension] = pyglexer
        return SourceCodeTokenizer.__LEXERS_CACHE[extension]
                

'''
Filter Functions to get tokens of specific type only
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
