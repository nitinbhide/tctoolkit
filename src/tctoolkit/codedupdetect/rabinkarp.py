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
from itertools import groupby
import operator
import hashlib

from . import tokenizer

HASH_BASE = (256*256*256*256)  #a single token hash value is made up of 4 bytes
HASH_MOD = 16777619  # make sure it is a prime

# TOKEN_HASHBASE=HASH_BASE
# TOKEN_MOD = 251   # make sure it is prime and less than 256

# read the FNV has wikipedia entry for the details of these constants.
# http://en.wikipedia.org/wiki/Fowler_Noll_Vo_hash
FNV_OFFSET_BASIS = 2166136261
FNV_PRIME = 16777619


def int_mod(a, b):
    return (a % b + b) % b


def FNV_hash(str):
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
    #fhash = (fhash >> 16) ^ (fhash & 0xFFFF)
    #fhash = (fhash >> 8) ^ (fhash & 0xFF)
    # print "hash after folding ", hash
    return(fhash)


class RollingHash(object):
    '''
    separated out rolling hash algorithm so that it can be indepdently tested.
    Any bugs in this algorithm will cause wrong duplicate detection
    window_size : window size for calculating rolling hash. Every hash is computed for 'windows_size'
     number of previous tokens.
    '''
    def __init__(self, window_size, value_func=lambda tokendata:tokendata.value):
        assert window_size > 1
        self.__rollhashbase = 1
        self.curhash = 0
        self.window_size =window_size
        self.value_func = value_func
        
        for i in range(0, self.window_size - 1):
            self.__rollhashbase = (self.__rollhashbase * HASH_BASE) % HASH_MOD
        self.tokenqueue = deque()
        self.token_hash = dict()

    def getTokenHash(self, token):
        # if token size is only one charater (i.e. tokens like '{', '+' etc)
        # then don't call FNV hash. Just use the single character.
        thash = FNV_hash(token)
        thash = thash % HASH_BASE
        return(thash)
    
    def addToken(self, tokendata):
        thash = self.getTokenHash(self.value_func(tokendata))
        self.curhash = int_mod(self.curhash * HASH_BASE, HASH_MOD)
        self.curhash = int_mod(self.curhash + thash, HASH_MOD)
        self.tokenqueue.append((thash, tokendata))
        '''
        if the number of tokens are reached window size then
        then remove hash value of first token from the rolling hash
        '''
        
        if len(self.tokenqueue) >= self.window_size:
            self.removeToken()
        return thash

    def removeToken(self):
        '''
        remove first token and update the current hash
        '''
        (thash, firsttoken) = self.tokenqueue.popleft()
        self.curhash = int_mod(
                self.curhash - int_mod(thash * self.__rollhashbase, HASH_MOD), HASH_MOD)
        return firsttoken
    
    def firstToken(self):
        '''
        return first token and current hash 
        '''
        (thash, firsttoken) = self.tokenqueue[0]
            
        return self.curhash, thash, firsttoken    
        
    def restart(self):
        '''
        restart the rolling hash computations
        '''
        self.tokenqueue.clear()
        self.curhash = 0
        
class RabinKarp(object):
    '''
    Rabin Karp duplication detection algorithm
    '''
    def __init__(self, chunk, min_lines, matchstore, fuzzy=False, blameflag=False):
        self.chunk = chunk  # minimum number of tokens to match
        self.min_lines = min_lines  # minimum number of lines to match.
        self.patternsize = self.chunk
        self.matchstore = matchstore
        self.fuzzy = fuzzy
        self.blameflag = blameflag
        self.tokenizers = dict()
        self.curfilematches = 0  # number of matches found the current file.
        self.rollinghash = RollingHash(self.chunk)
            
    def addAllTokens(self, srcfile):
        '''
        add all token in the srcfile to matchstore.
        '''
        #self.curfilematches = 0
        hashlist = list()
        self.rollinghash.restart()
        tknzr = self.getTokanizer(srcfile)
        for token in tknzr:
            curhash, firsttoken = self.addHashInMatchStore()
            self.rollinghash.addToken(token)
            if curhash and firsttoken:
                hashlist.append((firsttoken, curhash))

        self.detectMatches(hashlist, srcfile)

        #print("Current number of matches %d" % self.curfilematches)

    def findPossibleMatches(self, hashlist):
        '''
        return location/tokens in current file with possible matches
        '''
        def possibledup(tokendata):
            token, thash = tokendata
            matches = self.matchstore.getHashMatch(thash, token)

            bFoundMatch = (matches != None and len(matches) > 1)
            return bFoundMatch
         
        for hasmatch, matchgroup in groupby(hashlist, possibledup):
            if hasmatch:
                matchgroup = list(matchgroup)
                if len(matchgroup) > 1:
                    yield matchgroup

    def detectMatches(self, hashlist, srcfile):
        '''
        detect matches in the hash list of current file.
        '''
        for matchgroup in self.findPossibleMatches(hashlist):
            #last duptoken in the each match group is current source file i.e. srcfile
            starttoken, starthash = matchgroup[0]
            endtoken, endhash = matchgroup[-1]
            assert starttoken.srcfile == srcfile
            assert endtoken.srcfile == srcfile
            if (endtoken.lineno-starttoken.lineno >= self.min_lines):
                self.findMatches(starthash, starttoken)
    

    def addHashInMatchStore(self):
        '''
        At appropriate point, the 'first token' is removed from the token queue and then 
        the rolling hash is added to match store. Later new token is added in 'rolling hash'        
        '''
        curhash, firsttoken = None, None
        if len(self.rollinghash.tokenqueue) > 0:
            (curhash, thash, firsttoken) = self.rollinghash.firstToken()
            self.matchstore.addHash(curhash, firsttoken)
        return curhash, firsttoken
        
    def findMatches(self, curhash, tokendata1):
        '''
        search for matches for the current rolling hash in the matchstore.
        If the hash match is found then go for full comparision to search for the match.
        '''
        maxmatchlen = 0

        matches = self.matchstore.getHashMatch(curhash, tokendata1)
        assert matches != None
        
        for tokendata2 in filter(lambda tokendata: tokendata1 != tokendata, matches):
            matchlen, sha1_hash, match_end1, match_end2 = self.findMatchLength(tokendata1, tokendata2)

            # matchlen has to be at least pattern size
            # and matched line count has to be atleast self.min_lines
            if matchlen >= self.patternsize and (match_end1.lineno - tokendata1.lineno) >= self.min_lines \
                    and (match_end2.lineno - tokendata2.lineno) >= self.min_lines:
                # add the exact match to match store.
                self.matchstore.addExactMatch(
                    matchlen, sha1_hash, tokendata1, match_end1, tokendata2, match_end2)
                maxmatchlen = max(maxmatchlen, matchlen)
                self.curfilematches = self.curfilematches + 1

        return(maxmatchlen)

    def findMatchLength(self, tokendata1, tokendata2):
        '''
        find how many tokens (characters) are matching between tokendata1 and tokendata2.
        '''
        matchend1 = None
        matchend2 = None
        matchlen = 0
        sha1_hash = None

        # make a basic sanity check token value is same
        # if the filename is same then distance between the token positions has to be at least patternsize
        #   and the line numbers cannot be same
        if(tokendata1.value == tokendata2.value):
            tknzr1 = self.getTokanizer(tokendata1.srcfile)
            tknzr2 = tknzr1

            # filenames are different, get the different tokenizer
            if tokendata2.srcfile != tokendata1.srcfile:
                srcfile2 = tokendata2.srcfile
                tknzr2 = self.getTokanizer(srcfile2)

            assert tknzr1.srcfile == tokendata1.srcfile
            assert tknzr2.srcfile == tokendata2.srcfile
            sha1 = hashlib.sha1()

            for matchdata1, matchdata2 in zip(tknzr1.get_tokens_frompos(tokendata1.charpos), tknzr2.get_tokens_frompos(tokendata2.charpos)):
                if matchdata1.value != matchdata2.value:
                    break
                sha1.update(matchdata1.value.encode('utf-8'))
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

if __name__ == '__main__':
    def addtokens(rh, inputval):
        for token in inputval:
            rh.addToken(token)
            print(rh.curhash)
            
    def test_rolling_hash(inputval):
        rhash1 = RollingHash(5, value_func=lambda x:x)
        addtokens(rhash1, inputval)
        #rhash1.removeToken()
        print('starting next')
        rhash2 = RollingHash(5,value_func=lambda x:x)
        nextval = inputval[1:]
        addtokens(rhash2, inputval[1:])
        assert rhash1.curhash == rhash2.curhash
    
    test_rolling_hash('nitin bhide')
    #test_rolling_hash('never argue with idiots')
    