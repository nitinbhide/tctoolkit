'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import matchstore
from rabinkarp import RabinKarp
from tokenizer import Tokenizer

class CodeDupDetect:
    def __init__(self,filelist, minmatch=100):
        self.matchstore = matchstore.MatchStore(minmatch)
        self.minmatch = minmatch #minimum number of tokens to be matched.
        self.filelist = filelist
        self.foundcopies = False

    def __findcopies(self):
        totalfiles = len(self.filelist)
        i=0
        for srcfile in self.filelist:
            i=i+1
            print "Analyzing file %s (%d of %d)" %(srcfile,i,totalfiles)
            tknzr = Tokenizer(srcfile)
            rk = RabinKarp(self.minmatch,self.matchstore)
            rk.addAllTokens(tknzr)            
        self.foundcopies = True
        
    def findcopies(self):
        if( self.foundcopies == False):
            self.__findcopies()
        return(self.matchstore.iter_matches())

    def printmatches(self,output):
        exactmatches = self.findcopies()
        #now sort the matches based on the matched line count (in reverse)
        exactmatches = sorted(exactmatches,reverse=True,key=lambda x:x.matchedlines)
        matchcount=0
        
        for matches in exactmatches:
            matchcount=matchcount+1
            output.write("Match %d:\n"%matchcount)
            output.write("number of duplications :%d\n" % len(matches))
            for match in matches:
                output.write("\tfile : %s start line: %d duplicate lines:%d\n"
                             % (match.srcfile(),match.getStartLine(),match.getLineCount()))
                
            output.write("***\n")

        return(exactmatches)            

