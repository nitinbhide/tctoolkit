'''
tagcloud.py
utility functions to create tag cloud HTML string.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''

import math
import operator
import locale

MINFONTSIZE = -2
MAXFONTSIZE = 8

class TagCloud:
    def __init__(self):
        self.tagDict = dict()
        self.maxFreqLog = 0.0
        self.minFreqLog = 0.0
        self.fontsizevariation = MAXFONTSIZE-MINFONTSIZE
        assert(self.fontsizevariation > 0)
        
    def __getTagFontSize(self, freq):
        #change the font size between MINFONTSIZE to MAXFONTSIZE relative to current font size
        #now calculate the scaling factor for scaling the freq to fontsize.
        scalingFactor = self.fontsizevariation/(self.maxFreqLog-self.minFreqLog)
        fontsize = int(MINFONTSIZE+((math.log(freq)-self.minFreqLog)*scalingFactor)+0.5)
        #now round off to ensure that font size remains in MINFONTSIZE and MAXFONTSIZE
        assert(fontsize >= MINFONTSIZE and fontsize <= MAXFONTSIZE)
        return(fontsize)

    def addWord(self, word):
        freq = self.tagDict.get(word)
        if(freq == None):
            freq = 0
        freq = freq +1
        self.tagDict[word] = freq
        
    def filterWords(self, filterFunc):
        tagDict = dict()
        for word, freq in self.tagDict.iteritems():
            taginfo = filterFunc(word, freq)
            if(taginfo != None):
                tagDict[taginfo[0]] = taginfo[1]
        return(tagDict)
        
    def getTagCloudHtml(self,numWords=100, filterFunc=None):
        tagHtmlStr = ''

        tagDict = self.tagDict
        if( filterFunc != None):
            tagDict = self.filterWords(filterFunc)
        
        if( len(tagDict) > 0):            
            #first get sorted wordlist (reverse sorted by frequency)
            tagWordList = sorted(tagDict.items(), key=operator.itemgetter(1),reverse=True)
            totalTagWords = len(tagWordList)
            #now extract top 'numWords' from the list and then sort it with alphabetical order.
            #comparison should be case-insensitive            
            tagWordList = sorted(tagWordList[0:numWords], key=operator.itemgetter(0),
                                 cmp=lambda x,y: cmp(x.lower(), y.lower()) )
            
            minFreq = min(tagWordList,key=operator.itemgetter(1))[1]
            self.minFreqLog = math.log(minFreq)            
            maxFreq = max(tagWordList,key=operator.itemgetter(1))[1]
            self.maxFreqLog = math.log(maxFreq)
            difflog = self.maxFreqLog-self.minFreqLog
            #if the minfreqlog and maxfreqlog are nearly same then makesure that difference is at least 0.001 to avoid
            #division by zero errors later.
            assert(difflog >= 0.0)
            if( difflog < 0.001):
                self.maxFreqLog = self.minFreqLog+0.001
            #change minFreqLog in such a way smallest log(freq)-minFreqLog is greater than 0
            self.minFreqLog = self.minFreqLog-((self.maxFreqLog-self.minFreqLog)/self.fontsizevariation)
            
            #change the font size between "-2" to "+8" relative to current font size
            tagHtmlStr = ' '.join([('<font size="%+d" class="tagword">%s(%d)</font>\n'%(self.__getTagFontSize(freq), x,freq))
                                       for x,freq in tagWordList])
        return(tagHtmlStr)
    
