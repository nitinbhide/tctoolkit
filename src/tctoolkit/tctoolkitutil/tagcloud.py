'''
tagcloud.py
utility functions to create tag cloud HTML string.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''

import math
import operator
import locale


class TagCloud(object):

    '''
    store the information about tags
    '''

    def __init__(self):
        self.tagDict = dict()
        self.tagTypeDict = dict()

    def addWord(self, word, ttype):
        '''
        add word, update frequency and type of the word
        '''
        freq = self.tagDict.get(word, 0)
        freq = freq + 1
        self.tagDict[word] = freq
        # now update the word
        cur_ttype = self.tagTypeDict.get(word, None)
        if cur_ttype == None or (ttype != cur_ttype and ttype in cur_ttype):
            self.tagTypeDict[word] = ttype

    def filterWords(self, filterFunc):
        '''
        filter the words using the filter function
        '''
        tagDict = dict()
        for word, freq in self.tagDict.items():
            taginfo = filterFunc(word, self.tagTypeDict[word], freq)
            if(taginfo != None):
                tagDict[taginfo[0]] = taginfo[1]
        return(tagDict)

    def getSortedTagWordList(self, numWords, filterFunc):
        '''
        return list of tag words sorted alphabetically
        '''
        tagWordList = []
        tagDict = self.tagDict
        if(filterFunc != None):
            tagDict = self.filterWords(filterFunc)

        if(len(tagDict) > 0):
            # first get sorted wordlist (reverse sorted by frequency)
            tagWordList = sorted(
                list(tagDict.items()), key=operator.itemgetter(1), reverse=True)
            totalTagWords = len(tagWordList)
            # now extract top 'numWords' from the list and then sort it with alphabetical order.
            # comparison should be case-insensitive
            tagWordList = sorted(tagWordList[0:numWords], key=lambda x: x[0].lower())

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
            print("%s(%d):%f" % (word, freq, log_freq))
