#!/usr/bin/env python
'''
featureanalysis.py
Detects features/ideas common in multiple source files. Useful in indentifying related files.
It is based on Chapter 10 of 'Programming Collective Intelligence' by Toby Segaran.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''
import re

from math import log
from numpy import *
from pygments.token import Token

from tokentagcloud.tokentagcloud import Tokenizer
from tctoolkitutil import nnmf

SPLIT_VAR_RE = re.compile("[A-Z_]+[a-z0-9]+")

def split_variable_name(variable):
    '''
    split variable names like GetSomething into 'get' and 'something'. Use
    CamelCase and '_' as seperator.
    '''    
    tokens = SPLIT_VAR_RE.sub(lambda s: '_'+s.group(), variable)
    tokens = tokens.lower().strip('_').split('_')
    return tokens

def tokenize(fname):
    tokenzr = Tokenizer(fname)
    for ttype,tokenstr in tokenzr.get_tokens():
        if( ttype in Token.Name):
            if( ttype in Token.Name.Class or ttype in Token.Name.Function ):
                #split the variable and function names in word.
                for tk in split_variable_name(tokenstr):
                    yield tk

class FeatureAnalysis:
    def __init__(self):
        self.allwords = dict()
        self.filewords = []
        self.filetitles = []
        
    def makematrix(self):
        wordvec=[]
        
        # Only take words that are common but not too common
        for w,c in self.allwords.items():
            if c>3 and c<len(self.filewords)*0.6:
              wordvec.append(w) 
        
        # Create the word matrix
        l1=[[(word in f and log(f[word]+1) or 0) for word in wordvec] for f in self.filewords]
        return l1,wordvec
    
    def updateFileWords(self, filelist):    
        ec=0
        # Loop over all files        
        for fname in filelist:
            print "adding file %s" % fname
            # Extract the words
            self.filetitles.append(fname)
            words=tokenize(fname)
            self.filewords.append({})
            
            # Increase the counts for this word in allwords and in articlewords
            for word in words:
                self.allwords.setdefault(word,0)
                self.allwords[word]+=1
                self.filewords[ec].setdefault(word,0)
                self.filewords[ec][word]+=1
            ec+=1
    
    def detectFeatures(self, filelist):        
        self.updateFileWords(filelist)
        wordmatrix,self.wordvec= self.makematrix()
        v=matrix(wordmatrix)
        print "Detecting Features"
        self.weights,self.feat=nnmf.factorize(v,pc=20,itercount=50)
        
    def printFeatures(self, outfile):        
        pc,wc=shape(self.feat)
        toppatterns=[[] for i in range(len(self.filetitles))]
        patternnames=[]
        
        # Loop over all the features
        for i in range(pc):
            outfile.write("Feature #%d\n" % (i+1))
            slist=[]
            # Create a list of words and their weights
            for j in range(wc):
              slist.append((self.feat[i,j],self.wordvec[j]))
            # Reverse sort the word list
            slist.sort(reverse=True)
            
            # Print the first six elements
            n=[s[1] for s in slist[0:10]]
            outfile.write(str(n)+'\n')
            patternnames.append(n)
            
            # Create a list of articles for this feature
            flist=[]
            for j in range(len(self.filetitles)):
              # Add the article with its weight
                if( self.weights[j,i] > 0.1):
                    flist.append((self.weights[j,i],self.filetitles[j]))
                    toppatterns[j].append((self.weights[j,i],i,self.filetitles[j]))
            
            # Reverse sort the list
            flist.sort(reverse=True)
            #weight tolerance is max weight/2. So the articles with weights between
            # max weight to (maxweight/2) are displayed
            minweight = flist[0][0]/4.0
            # Show the top 3 articles
            for f in flist:
                if f[0] >= minweight:
                    outfile.write(str(f)+'\n')
                else:
                    break
            outfile.write('\n')
    
        outfile.write('\n')
            
        
    def printArticles(outfile):        
        # Loop over all the articles
        for j in range(len(self.filetitles)):
            outfile.write(self.filetitles[j]+'\n')
            
            # Get the top features for this article and
            # reverse sort them
            toppatterns[j].sort()
            toppatterns[j].reverse()
            
            # Print the top three patterns
            for i in range(3):
              outfile.write(str(self.toppatterns[j][i][0])+' '+
                            str(self.patternnames[self.toppatterns[j][i][1]])+'\n')
            outfile.write('\n')
    

