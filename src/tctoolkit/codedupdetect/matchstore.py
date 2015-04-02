'''
Matchstore.py

Stores the potential matches and finds exact matches from that list.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''

import codecs
import tokenizer

try:
    from svn_blame import *
    BLAME_SUPPORT = True
except:
    print "svn_blame not found : SVN blame detection for duplicate files is not supported"
    BLAME_SUPPORT = False

class MatchData(object):
    '''
    store the match/duplication data of one instance
    '''
    __slots__ = ['matchlen', 'starttoken', 'endtoken', 'revisioninfo']
    def __init__(self, matchlen, starttoken, endtoken, revisioninfo):
        self.matchlen = matchlen
        assert starttoken[0] == endtoken[0]  #make sure filenames are same
        assert starttoken[1] <= endtoken[1]  #line number of starttoken has to be earlier than end token
        assert starttoken[2] <= endtoken[2] #file position of starttoken has to be earlier than end token
        self.starttoken = starttoken
        self.endtoken = endtoken
        self.revisioninfo = revisioninfo

    def __cmp__(self, other):
        val = 1
        if other != None:
            val = cmp(self.srcfile(), other.srcfile())
            if val == 0:
                #file name is same now. Compareline numbers
                val = cmp(self.getStartLine(), other.getStartLine())
        return val

    def __hash__(self):
        tpl = (self.srcfile(), self.getStartLine())
        return hash(tpl)
                    
    def getLineCount(self):
        lc = self.endtoken[1] - self.starttoken[1]
        assert lc >= 0
        return lc

    def srcfile(self):
        return self.starttoken[0]
    
    def getStartLine(self):
        return self.starttoken[1]

    def getRevisionNumber(self):
        return self.revisioninfo[1]

    def getAuthorName(self):
        return self.revisioninfo[0]

class MatchSet(object):
    def __init__(self, blameflag):
        self.matchset = set()
        self.matchedlines = None
        self.firstMatch = None
        self.svn_blame_client = None

        if BLAME_SUPPORT and blameflag :
            self.svn_blame_client = SvnBlameClient()
            
    def addMatch(self, matchlen, matchstart, matchend):
        '''
        add the match information in the match data set
        '''
        revisioninfo = (None, None)
        
        if self.svn_blame_client:
            startlinenum = matchstart[1]
            endlinenum = startlinenum + matchend[1]
            dupFileName = str(matchstart[0])
            revisioninfo = self.svn_blame_client.findAuthorForFragment(dupFileName, startlinenum, endlinenum)

        matchdata = MatchData(matchlen, matchstart, matchend, revisioninfo)
        self.matchset.add(matchdata)
        if self.firstMatch == None:
            self.firstMatch = matchdata

        lc = matchdata.getLineCount()
        if self.matchedlines == None:
            self.matchedlines = lc
        else:
            self.matchedlines = min(self.matchedlines, lc)

        
    def __len__(self):
        return len(self.matchset)

    def __iter__(self):
        return self.matchset.__iter__()

    def getMatchSource(self):
        '''
        extract the source code from the first file in matchset.
        '''
        match = self.firstMatch
        with codecs.open(match.srcfile(), "rb", encoding='utf-8', errors='ignore') as src:
            for i in range(match.getStartLine()):
                src.readline()
            return [src.readline() for i in range(match.getLineCount())]
        
    def getSourceLexer(self):
        '''
        get lexer for firstMatch of this matcheset
        '''
        return tokenizer.Tokenizer.get_lexer_for_file(self.firstMatch.srcfile())

class MatchStore(object):
    def __init__(self, minmatch, blameflag):
        self.minmatch = minmatch
        self.blameflag = blameflag
        self.hashset = dict()
        self.matchlist = dict()
        
    def addHash(self, rhash, tokendata):
        rhash = hash((rhash, tokendata[3])) # create a new hash with (rolling hash value and actual token string)
        hashdata = self.hashset.get(rhash)
        if hashdata == None:
            hashdata = []
        hashdata.append(tokendata)
        self.hashset[rhash] = hashdata

    def getHashMatch(self, rhash, tokendata):
        rhash = hash((rhash, tokendata[3])) # create a new hash with (rolling hash value and actual token string)
        return(self.hashset.get(rhash))
    
        
    def addExactMatch(self, matchlen, sha1_hash, matchstart1, matchend1, matchstart2, matchend2):
        assert matchstart1[0] == matchend1[0] #ensure filenames of start and end are same
        assert matchstart2[0] == matchend2[0] #ensure filenames of start and end are same
        assert matchstart1[2] < matchend1[2] #ensure matchstart position is less than matchend position
        assert matchstart2[2] < matchend2[2] #ensure matchstart position is less than matchend position
        assert matchlen >= self.minmatch
                
        matchset = self.matchlist.get(sha1_hash)
        if matchset == None:
            matchset = MatchSet(self.blameflag)
        matchset.addMatch(matchlen, matchstart1, matchend1)
        matchset.addMatch(matchlen, matchstart2, matchend2)
        
        if len(matchset) > 1:
            self.matchlist[sha1_hash] = matchset
            
    def iter_matches(self):
        #print "number hashes : %d" % len(self.hashset)
        return self.matchlist.itervalues()
            
        