'''
tokenizer.py
A tokenizer wrapper on top of Pygments lexer for the Code Duplication Detector 

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''
from __future__ import with_statement

from pygments.lexers import get_lexer_for_filename
from pygments.filter import simplefilter
from pygments.token import Token, is_token_subtype

class Tokenizer(object):
    def __init__(self, srcfile, fuzzy=False):
        self.srcfile = srcfile
        self.tokenlist=None
        self.fuzzy = fuzzy
        self.pos_dict = dict()
        
    def __iter__(self):
        self.update_token_list()        
        return(self.tokenlist.__iter__())
    
    def update_token_list(self):
        if(self.tokenlist==None):
            self.tokenlist = list()
            for idx, token in enumerate(self.get_tokens()):
                self.tokenlist.append(token)
                self.pos_dict[token[2]] = idx

    
    def get_tokens(self):
        pyglexer = get_lexer_for_filename(self.srcfile,stripall=True)
        
        linenum=1
        with open(self.srcfile,"r") as code:
            for charpos,ttype,value in pyglexer.get_tokens_unprocessed(code.read()):    
                #print ttype
                if( self.fuzzy and is_token_subtype(ttype,Token.Name)):
                    #we are doing fuzzy matching. Hence replace the names
                    #e.g. variable names by value 'Variable'.
                    newvalue='#variable'
                else:
                    newvalue = value.strip()
                if( newvalue !='' and ttype not in Token.Comment):
                    yield self.srcfile, linenum,charpos,newvalue
                linenum=linenum+value.count('\n')
                
        
    def get_tokens_frompos(self, fromcharpos):
        self.update_token_list()                
        idx = self.pos_dict[fromcharpos]
        for tokendata in self.tokenlist[idx:]:
            yield tokendata
            

            