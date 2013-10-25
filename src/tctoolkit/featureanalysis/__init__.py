'''
Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''
import os.path

from .topictokenizer import TopicTokenizer

class FeatureAnalysisBase(object):
    def __init__(self):
        self.allwords = dict()
        self.filewords = []
        self.filetitles = []
            
    def updateFileWords(self, filelist):    
        # Loop over all files        
        for fname in filelist:
            print "adding file %s" % fname
            # Extract the words
            self.filetitles.append(fname)
            tokenizer = TopicTokenizer(fname)
            words=tokenizer.get_tokens()
            self.filewords.append({})
            fidx = len(self.filetitles)-1
            
            # Increase the counts for this word in allwords and in articlewords
            for word in words:
                self.allwords.setdefault(word,0)
                self.allwords[word]+=1
                self.filewords[fidx].setdefault(word,0)
                self.filewords[fidx][word]+=1
            
