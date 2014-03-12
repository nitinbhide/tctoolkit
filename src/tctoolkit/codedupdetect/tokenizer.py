'''
tokenizer.py
A tokenizer wrapper on top of Pygments lexer for the Code Duplication Detector 

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''

import os
import logging
from pygments.lexers import get_lexer_for_filename
from pygments.filter import simplefilter
from pygments.token import Token, is_token_subtype


class Tokenizer(object):
    __LEXERS_CACHE = dict() #dictionary of lexers keyed by file extensions
    
    def __init__(self, srcfile, fuzzy=False):
        self.srcfile = srcfile
        self.tokenlist=None
        self.fuzzy = fuzzy
        self.pos_dict = dict()        
        
    def __iter__(self):
        self.update_token_list()        
        return(self.tokenlist.__iter__())
    
    @classmethod
    def get_lexer2(selfcls, filename):
        '''
        search lexer in the lexers list first based on the file extension.
        if it not there then call the get_lexer_for_filename
        '''
        name, extension = os.path.splitext(filename)
        pyglexer = Tokenizer.__LEXERS_CACHE.get(extension, None)

        if(pyglexer == None):
            try:
                pyglexer = get_lexer_for_filename(filename,stripall=True)          
                Tokenizer.__LEXERS_CACHE[extension] = pyglexer                            
            except:
                logging.warning("Lexer not found for file %s" % filename)
                pyglexer = None

        return pyglexer

    def get_lexer(self):
        '''
        search lexer in the lexers list first based on the file extension.
        if it not there then call the get_lexer_for_filename
        '''
        return Tokenizer.get_lexer2(self.srcfile)
        
    def update_token_list(self):
        if(self.tokenlist==None):
            self.tokenlist = list()
            for idx, token in enumerate(self.get_tokens()):
                self.tokenlist.append(token)
                self.pos_dict[token[2]] = idx
    
    def get_tokens(self):
        '''
        token tupple is returned. Format of token data tuple is
        (source file path, line number of token, charposition of token, text value of the token)
        '''
        linenum=1
        pyglexer = self.get_lexer()
        
        if pyglexer != None:
            with open(self.srcfile,"r") as code:
                for charpos,ttype,value in pyglexer.get_tokens_unprocessed(code.read()):    
                    #print ttype
                    if( self.fuzzy and is_token_subtype(ttype,Token.Name)):
                        #we are doing fuzzy matching. Hence replace the names
                        #e.g. variable names by value 'Variable'.
                        newvalue='#variable#'
                    else:
                        newvalue = value.strip()
                    if( newvalue !='' and ttype not in Token.Comment):
                        yield self.srcfile, linenum,charpos,newvalue
                    linenum=linenum+value.count('\n')
                
        
    def get_tokens_frompos(self, fromcharpos):
        self.update_token_list()
        if fromcharpos not in self.pos_dict:
            import pdb
            pdb.set_trace()
        idx = self.pos_dict[fromcharpos]
        return self.tokenlist[idx:]

            