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


class TagCloud(object):
    def __init__(self):
        self.tagDict = dict()
            
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

    def getSortedTagWordList(self, numWords, filterFunc):
        '''
        return list of tag words sorted alphabetically
        '''
        tagWordList = []
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
        
        return tagWordList
    
    def getTagStats(self, numWords, filterFunc):
        '''
        return tag statistics as 'tuple' of (tag name, count_or_frequency, log(frequency))
        '''
        tagWordList = self.getSortedTagWordList(numWords, filterFunc)
        for word, freq in tagWordList:
            yield word, freq, math.log(freq)

    
    def printTagStats(self, numWords=100, filterFunc=None):
        for word, freq, log_freq in self.getTagStats(numWords, filterFunc):
            print "%s(%d):%f" % (word, freq, log_freq)
        
    
