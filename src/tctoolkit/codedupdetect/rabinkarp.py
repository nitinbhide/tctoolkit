'''
rabinkarp.py
experimental code to search duplicate strings using Rabin Karp algorithm

reference : http://code.google.com/p/rabinkarp/source/browse/trunk/RK.cpp

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''
import logging

from collections import deque
from itertools import izip
import operator
import hashlib

import tokenizer

# Maximum number of matches to find in a single file
MAX_SINGLE_FILEMATCHES = 50
HASH_BASE = 256
HASH_MOD = 16777619  # make sure it is a prime

# TOKEN_HASHBASE=HASH_BASE
# TOKEN_MOD = 251   # make sure it is prime and less than 256

# read the FNV has wikipedia entry for the details of these constants.
# http://en.wikipedia.org/wiki/Fowler_Noll_Vo_hash
FNV_OFFSET_BASIS = 2166136261
FNV_PRIME = 16777619


def int_mod(a, b):
    return (a % b + b) % b


def FNV8_hash(str):
    '''
    8 bit FNV hash created by XOR folding the FNV32 hash of the string
    '''
    #fhash = FNV_OFFSET_BASIS
    # for ch in str:
    #    fhash = fhash ^ ord(ch)
    #    fhash = fhash * FNV_PRIME
    #    fhash = fhash & 0xFFFFFFFF #ensure that hash remains 32 bit.
    fhash = FNV_OFFSET_BASIS
    for ch in str:
        fhash = ((fhash ^ ord(ch)) * FNV_PRIME) & 0xFFFFFFFF

    # now fold it with XOR folding
    # print "token hash ", hash
    fhash = (fhash >> 16) ^ (fhash & 0xFFFF)
    fhash = (fhash >> 8) ^ (fhash & 0xFF)
    # print "hash after folding ", hash
    return(fhash)


class RabinKarp(object):

    def __init__(self, patternsize, min_lines, matchstore, fuzzy=False, blameflag=False):
        self.patternsize = patternsize  # minimum number of tokens to match
        self.min_lines = min_lines  # minimum number of lines to match.
        self.matchstore = matchstore
        self.fuzzy = fuzzy
        self.blameflag = blameflag
        self.tokenqueue = deque()
        self.tokenizers = dict()
        self.token_hash = dict()
        self.__rollhashbase = 1
        self.curfilematches = 0  # number of matches found the current file.
        for i in xrange(0, patternsize - 1):
            self.__rollhashbase = (self.__rollhashbase * HASH_BASE) % HASH_MOD

    def rollCurHash(self, tknzr, curhash, pastmatchlen):
        matchlen = pastmatchlen
        if(len(self.tokenqueue) >= self.patternsize):
            '''
            if the number of tokens are reached patternsize then
            then remove hash value of first token from the rolling hash
            '''
            (thash, firsttoken) = self.tokenqueue.popleft()
            # add the current hash value in hashset
            if matchlen == 0:
                matchlen = self.findMatches(curhash, firsttoken, tknzr)
            else:
                matchlen = matchlen - 1

            self.matchstore.addHash(curhash, firsttoken)
            curhash = int_mod(
                curhash - int_mod(thash * self.__rollhashbase, HASH_MOD), HASH_MOD)
        return(curhash, matchlen)

    def getTokenHash(self, token):
        # if token size is only one charater (i.e. tokens like '{', '+' etc)
        # then don't call FNV hash. Just use the single character.
        if len(token) > 1:
            thash = FNV8_hash(token)
        else:
            thash = ord(token[0])
        return(thash)

    def addAllTokens(self, srcfile):
        curhash = 0
        matchlen = 0
        # empty the tokenqueue since we are starting a new file
        self.tokenqueue.clear()
        self.curfilematches = 0
        tknzr = self.getTokanizer(srcfile)
        for token in tknzr:
            curhash, matchlen = self.rollCurHash(tknzr, curhash, matchlen)
            curhash = self.addToken(curhash, token)
            if self.curfilematches > MAX_SINGLE_FILEMATCHES:
                break

    def addToken(self, curhash, tokendata):
        thash = self.getTokenHash(tokendata[3])
        curhash = int_mod(curhash * HASH_BASE, HASH_MOD)
        curhash = int_mod(curhash + thash, HASH_MOD)
        self.tokenqueue.append((thash, tokendata))
        return(curhash)

    def findPossibleMatches(self, tokendata1, hashmatches):
        '''
        filter the hashmatches for probabble matches. Current this filter checks
        if the match is in the same file and if in the same file then the
        distance between the tokens has to be at least 'patternsize'.
        This avoidds 'self' matches for sitations like "[0,0,0,0,0,0]"
        '''
        srcfile = tokendata1.srcfile
        srclineno = tokendata1.lineno
        for matchtoken in hashmatches:
            matchfile = matchtoken.srcfile
            if(srcfile == matchfile):
                # token are from same files. Now check the line numbers. The linenumbers
                # difference has to be at least 3
                matchlineno = matchtoken.lineno
                if abs(matchlineno - srclineno) > 3:
                    yield matchtoken
            else:
                # token are from different files.
                yield matchtoken

    def findMatches(self, curhash, tokendata1, tknzr):
        '''
        search for matches for the current rolling hash in the matchstore.
        If the hash match is found then go for full comparision to search for the match.
        '''
        assert tknzr.srcfile == tokendata1.srcfile
        maxmatchlen = 0

        matches = self.matchstore.getHashMatch(curhash, tokendata1)
        if matches != None:
            assert tknzr.srcfile == tokendata1.srcfile

            for tokendata2 in self.findPossibleMatches(tokendata1, matches):
                matchlen, sha1_hash, match_end1, match_end2 = self.findMatchLength(
                    tknzr, tokendata1, tokendata2)

                # matchlen has to be at least pattern size
                # and matched line count has to be atleast self.min_lines
                if matchlen >= self.patternsize and (match_end1[1] - tokendata1[1]) >= self.min_lines:
                    # add the exact match to match store.
                    self.matchstore.addExactMatch(
                        matchlen, sha1_hash, tokendata1, match_end1, tokendata2, match_end2)
                    maxmatchlen = max(maxmatchlen, matchlen)
                    self.curfilematches = self.curfilematches + 1

        return(maxmatchlen)

    def findMatchLength(self, tknzr1, tokendata1, tokendata2):
        matchend1 = None
        matchend2 = None
        matchlen = 0
        sha1_hash = None

        # make a basic sanity check token value is same
        # if the filename is same then distance between the token positions has to be at least patternsize
        #   and the line numbers cannot be same
        if(tokendata1.value == tokendata2.value
                and (tokendata1.srcfile != tokendata2.srcfile
                     or ((abs(tokendata1.charpos - tokendata2.charpos) > self.patternsize) and tokendata1.lineno > tokendata2.lineno))):

            tknzr2 = tknzr1

            # filenames are different, get the different tokenizer
            if tokendata2.srcfile != tokendata1.srcfile:
                srcfile2 = tokendata2.srcfile
                tknzr2 = self.getTokanizer(srcfile2)

            assert tknzr1.srcfile == tokendata1.srcfile
            assert tknzr2.srcfile == tokendata2.srcfile
            sha1 = hashlib.sha1()

            for matchdata1, matchdata2 in izip(tknzr1.get_tokens_frompos(tokendata1.charpos), tknzr2.get_tokens_frompos(tokendata2.charpos)):
                if matchdata1[3] != matchdata2[3]:
                    break
                sha1.update(matchdata1[3])
                matchend1 = matchdata1
                matchend2 = matchdata2
                matchlen = matchlen + 1
            sha1_hash = sha1.digest()

        return(matchlen, sha1_hash, matchend1, matchend2)

    def getTokanizer(self, srcfile):
        '''
        get the tokenizer for the given source file.
        '''
        tknizer = self.tokenizers.get(srcfile)
        if tknizer == None:
            tknizer = tokenizer.Tokenizer(srcfile, fuzzy=self.fuzzy)
            self.tokenizers[srcfile] = tknizer

        assert tknizer.srcfile == srcfile

        return tknizer
