'''
tokenizer.py
A tokenizer wrapper on top of Pygments lexer for the Code Duplication Detector

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''

import os
import logging

from tctoolkit.tctoolkitutil import SourceCodeTokenizer

from pygments.token import Token


class Tokenizer(SourceCodeTokenizer):

    '''
    tokenizer for code duplication detection.
    '''

    def __init__(self, srcfile, fuzzy=False):
        super(Tokenizer, self).__init__(srcfile)
        self.fuzzy = fuzzy
        self.pos_dict = dict()

    def update_token_list(self):
        if(self.tokenlist == None):
            self.tokenlist = list()
            for idx, token in enumerate(self.get_tokens()):
                self.tokenlist.append(token)
                self.pos_dict[token[2]] = idx

    def is_fuzzy_token(self, srctoken):
        '''
        check if the given token is 'fuzzy' token i.e. a variable name, class name, constant
        string, number etc.
        '''
        if srctoken.is_type(Token.Name):
            return True
        if srctoken.is_type(Token.Literal):
            return True
        return False

    def get_tokens(self):
        '''
        token tupple is returned. Format of token data tuple is
        (source file path, line number of token, charposition of token, text value of the token)
        '''
        linenum = 1
        for srctoken in self._parse_tokens():
            # print ttype
            if(self.fuzzy and self.is_fuzzy_token(srctoken)):
                # we are doing fuzzy matching. Hence replace the names
                # e.g. variable names by value 'Variable'.
                value = '#FUZZY#'
            else:
                value = srctoken.value
                if(value != '' and not srctoken.is_type(Token.Comment)):
                    yield self.srcfile, linenum, srctoken.charpos, value

            linenum = linenum + srctoken.num_lines

    def get_tokens_frompos(self, fromcharpos):
        self.update_token_list()
        idx = self.pos_dict[fromcharpos]
        return self.tokenlist[idx:]
