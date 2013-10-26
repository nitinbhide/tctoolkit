#!/usr/bin/env python
'''
topictokenizer.py

Tokenizes the source code for use in feature/topic detection

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import re
import unicodedata
import string
from itertools import izip, tee

from pygments.token import Token

from tokentagcloud.tokentagcloud import Tokenizer


STOPWORDS_SET= set(["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all",
                    "almost", "alone", "along", "already", "also","although","always","am","among", "amongst",
                    "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway",
                    "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes",
                    "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides",
                    "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant",
                    "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down",
                    "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty",
                    "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except",
                    "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly",
                    "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has",
                    "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon",
                    "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc",
                    "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly",
                    "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more",
                    "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither",
                    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing",
                    "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other",
                    "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps",
                    "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious",
                    "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some",
                    "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such",
                    "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then",
                    "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these",
                    "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout",
                    "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two",
                    "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what",
                    "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein",
                    "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole",
                    "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your",
                    "yours", "yourself", "yourselves", "the"]);

def deaccent(text):
    """
    Remove accentuation from the given string. Input text is either a unicode string or utf8 encoded bytestring.

    Return input string with accents removed, as unicode.

    >>> deaccent("??f chomutovsk?ch komunist? dostal po?tou b?l? pr??ek")
    u'Sef chomutovskych komunistu dostal postou bily prasek'
    """
    if not isinstance(text, unicode):
        text = unicode(text, 'utf8') # assume utf8 for byte strings, use default (strict) error handling
    norm = unicodedata.normalize("NFD", text)
    result = u''.join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize("NFC", result)



class TopicTokenizer(Tokenizer):
    '''
    Tokenizes the source code for use in feature/topic detection
    Uses following logic
    1. Detect all names in the source code
    2. Split the names on CamelCase, '.' and '_'
        get_something becomes 'get' 'something'
        GetSomething also becomes 'get' 'something'
    3. Use the stop words list to remove the stop words from token.
    4. Parse the comments and return words from the comments
    '''
    SPLIT_VAR_RE = re.compile("(\A\w|[A-Z_\.]+)[a-z0-9]+")
    PAT_ALPHABETIC = re.compile('(((?![\d])\w)+)', re.UNICODE)
    
    def __init__(self, filename,ignore_comments=True, ngram=1, ngram_join_char=' '):
        '''
        if ngram is 1 return each individual word,
        if ngram is 2 return pairs of words as 'token'
        '''
        super(TopicTokenizer, self).__init__(filename, ignore_comments=ignore_comments)
        self.ngram = ngram
        self.ngram_join_char = ngram_join_char
    
    def split_variable_name(self, variable):
        '''
        split variable names like GetSomething into 'get' and 'something'. Use
        CamelCase and '_' as seperator.
        '''    
        tokens = TopicTokenizer.SPLIT_VAR_RE.sub(lambda s: '_'+s.group(), variable)
        tokens = tokens.lower().strip('_').split('_')
        return tokens        

    def is_name_token(self, ttype):
        return ( ttype in Token.Name and
            (ttype == Token.Name or ttype in Token.Name.Class \
            or ttype in Token.Name.Function \
            or ttype in Token.Name.Variable or ttype in Token.Name.Constant \
            or ttype in Token.Name.Namespace))
            

    def tokenize_comments(self, comment):
        '''
        tokenize the comments and return the words in the comment. This code is
        inspired by utils.tokenize() from gensim.
        '''
        if not isinstance(comment, unicode):
            comment = unicode(comment, encoding='utf8', errors='ignore')
        
        comment = comment.lower()
        comment = deaccent(comment)
        comment = comment.strip('/#*')
        for match in TopicTokenizer.PAT_ALPHABETIC.finditer(comment):
            word = match.group()
            if word not in STOPWORDS_SET:
                yield word

    
    def get_raw_tokens(self):
        '''
        extract tokens from source code and comments using the pygments
        based tokenizer
        '''
        for ttype,tokenstr in super(TopicTokenizer, self).get_tokens():
            if self.is_name_token(ttype):
                #split the variable and function names in word
                for tk in self.split_variable_name(tokenstr):
                    if tk not in STOPWORDS_SET:
                        yield unicode(tk.strip('.').lower(), "utf8")
            
            if ttype in Token.Comment:
                for word in self.tokenize_comments(tokenstr):
                    yield word
    
    def get_tokens(self):
        '''
        yield the tokens (apply grouper if ngrams > 1)
        '''
        def grouper(n, iterable, fillvalue=None):
            "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
            args = tee(iterable, n)
            for i in range(n):
                for j in range(i+1, n):
                    next(args[j])
            
            for tk in izip(*args):
                yield string.join(tk, self.ngram_join_char)
                
        token_iter = self.get_raw_tokens()
        if self.ngram > 1:
            token_iter = grouper(self.ngram, token_iter, ' ')
            
        return token_iter
            
    def __iter__(self):
        '''
        make an iterator which returns the tokens
        '''
        return self.get_tokens()
    

