'''
Source Code Tokenizer

Parses various source code files using the Pygments and returns a stream of 'tokens'. To be used by
code duplication detector, token tag cloud etc.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''
import os.path

from pygments.lexers import get_lexer_for_filename,get_lexer_by_name,get_all_lexers
from pygments.filter import simplefilter
from pygments.token import Token

class SourceToken(object):
    '''
    present one source code token. Use __slots__ to reduce the size of each object instance
    '''
    __slots__ = ['rawvalue', 'ttype', 'charpos']
    def __init__(self, ttype, value, charpos=None):
        self.ttype = ttype
        self.rawvalue = value
        self.charpos = charpos
    
    def is_type(self, oftype):
        return self.ttype in oftype
    
    @property
    def value(self):
        return self.rawvalue.strip()

    @property
    def num_lines(self):
        return self.rawvalue.count('\n')

class SourceCodeTokenizer(object):
    '''
    tokenizing the source files
    '''
    __LEXERS_CACHE = dict() #dictionary of lexers keyed by file extensions
    
    def __init__(self, srcfile, lang=None, token_class=SourceToken):
        '''
        override the token_class if you want to use a drived class of 'SourceToken' class.
        '''
        self.srcfile = srcfile
        self.tokenlist=None        
        self.lang = lang # programming language.
        assert issubclass(token_class,SourceToken)==True, "token_class has to be subclass/derived class of SourceToken"
        self.TOKEN_CLASS = token_class
        
    def __iter__(self):
        self.update_token_list()
        return(self.tokenlist.__iter__())

    def update_token_list(self):
        if(self.tokenlist==None):
            self.tokenlist = [token for token in self.get_tokens()]
        
    def _parse_tokens(self):
        '''
        parse the tokens from the source file and return the raw parsed tokens.
        get_tokens functions will internally use this function.
        '''
        pyglexer = self.get_lexer()
         
        if pyglexer != None:
            prevtoken = None
            with open(self.srcfile, "r") as code:
                for charpos,ttype,value in pyglexer.get_tokens_unprocessed(code.read()):
                    #NOTE : do not call 'strip' on the 'value' variable.
                    #if derived class wants to calculate line numbers, the 'strip' call will screw up
                    #the line number computation.          
                    srctoken = self.TOKEN_CLASS(ttype, value,charpos)
                    self.update_type(srctoken, prevtoken)
                    yield srctoken
                    if srctoken.value != '':
                        prevtoken = srctoken
    
    def ignore_token(self, srctoken):
        return False

    def update_type(self, srctoken, prevtoken):
        '''
        place holder do nothing
        '''
        pass

    def get_tokens(self):
        '''
        iteratore over the tokens
        '''
        for srctoken in self._parse_tokens():
            if( self.ignore_token(srctoken)==False):
                    yield srctoken
                
    def get_lexer(self):
        '''
        if language is specified, then use it for 'getting lexer'. If the language is not
        specified then use the file for detecting the lexer.
        return lexer for self.srcfile
        '''        
        if self.lang :
            lexer = SourceCodeTokenizer.get_lexer_for_lang(self.lang)                        
            assert(lexer != None)
        else:
            lexer = SourceCodeTokenizer.get_lexer_for_file(self.srcfile)
        return lexer

    @classmethod
    def get_lexer_for_lang(selfcls, lang):
        '''
        get the lexer for the given language.
        '''
        pyglexer = SourceCodeTokenizer.__LEXERS_CACHE.get(lang, None)

        if(lang not in SourceCodeTokenizer.__LEXERS_CACHE):
            try:
                pyglexer = get_lexer_by_name(lang, encoding='utf-8')
                SourceCodeTokenizer.__LEXERS_CACHE[lang] = pyglexer
            except:
                #ignore the lexer not found exceptions
                assert(pyglexer == None)                

        return pyglexer

    @classmethod
    def get_lexer_for_file(selfcls, filename):
        '''
        search lexer in the lexers list first based on the file extension.
        if it not there then call the get_lexer_for_filename
        '''
        name, extension = os.path.splitext(filename)
        pyglexer = SourceCodeTokenizer.__LEXERS_CACHE.get(extension, None)

        if(extension not in SourceCodeTokenizer.__LEXERS_CACHE):
            try:
                pyglexer = get_lexer_for_filename(filename,stripall=True,encoding='utf-8')
                SourceCodeTokenizer.__LEXERS_CACHE[extension] = pyglexer
            except:
                #ignore the lexer not found exceptions
                assert(pyglexer == None)
                pass

        return pyglexer

    @classmethod
    def is_lang_supported(selfcls, lang):
        '''
        check 'lang' is there in the short name of supported lexers
        '''
        for lexer in get_all_lexers():
            if lang in lexer[1]:
                return True
        return False

    @classmethod
    def language_list(selfcls):
        '''
        get the support languages short name list from the pygments.
        '''    
        langlist = ['%s (Names : %s)' % (lexer[0], ','.join(lexer[1])) for lexer in get_all_lexers()]       
        langlist = sorted(langlist)
        return langlist

'''
Filter Functions to get tokens of specific type only
'''

def TagTypeFilter(word, ttype, freq, tagType):
    validtag = None
    if(freq > 1 and ttype in tagType):
        validtag = (word, freq)
    return(validtag)
    
def KeywordFilter(word, ttype, freq):
    return(TagTypeFilter(word, ttype, freq, Token.Keyword))    

def NameFilter(word, ttype, freq):
    return(TagTypeFilter(word, ttype, freq, Token.Name))    
    
def ClassNameFilter(word, ttype, freq):
    return(TagTypeFilter(word, ttype, freq, Token.Name.Class))    
    
def FuncNameFilter(word, ttype, freq):
    return(TagTypeFilter(word, ttype, freq, Token.Name.Function))

def ClassFuncNameFilter(word, ttype, freq):
    validtag = ClassNameFilter(word, ttype, freq)
    if( validtag == None):
        validtag = FuncNameFilter(word, ttype, freq)
    return(validtag)

def LiteralFilter(word, ttype, freq):
    return TagTypeFilter(word, ttype, freq, Token.Literal)