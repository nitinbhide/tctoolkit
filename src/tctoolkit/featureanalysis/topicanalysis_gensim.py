#!/usr/bin/env python
'''
featureanalysis_gensim.py
Detects features/ideas common in multiple source files. Useful in indentifying related files.
Uses 'gensim' library and LDA algorithms to detect topics in various code files.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''
import pickle
import os.path

from math import log
from numpy import *

from gensim import corpora, models, similarities

from tctoolkitutil import nnmf
from . import FeatureAnalysisBase
from . import tokenize_file,STOPWORDS_SET

def _tokenize_text_file(fname):
    with open(fname, "r") as f:
        doc = f.read()
        doc =  doc.split()
        for word in doc:
            if word not in STOPWORDS_SET:
                yield word
        
        
class GensimTextCorpus(corpora.textcorpus.TextCorpus):
    def __init__(self, filelist):
        self.length = 0;
        self.filelist = filelist
        super(GensimTextCorpus, self).__init__(filelist)
        
    def get_texts(self):
        self.input = self.filelist
        for fname in self.input:
            self.input = fname
            self.length = self.length+1
            #print "now tokenizing %s" % fname
            yield tokenize_file(fname)
    
    def __unicode__(self):
        '''
        print stats about the corpus
        '''
        return 'num docs : %d ' % self.dictionary.num_docs
    
    def __str__(self):
        return unicode(self)
    
    def __len__(self):
        return self.length
    

class TopicAnalysisGensim(object):
    def __init__(self,filelist):
        self.corpus = None
        self.filelist = filelist

    def detectTopics(self):
        '''
        read the files and detect the topics in each file.
        '''
        print "Detecting Features"
        self.corpus = GensimTextCorpus(self.filelist)
        print self.corpus
        self.model = models.LdaModel(self.corpus, id2word=self.corpus.dictionary, num_topics=100)
        print self.model
        
    def printFeatures(self, outfile):
        for topic in self.model.print_topics(10):
            outfile.write(topic)
            outfile.write('\n')
            print topic
    
    def save(self, filename):
        #first save corpus
        fname, ext = os.path.splitext(filename)
        with open(fname +'.filelist', "wb") as fp:
            pickle.dump(self.filelist, fp) 
        self.corpus.dictionary.save(fname+'.corpus')
        self.model.save(fname+'.lda')
        index = similarities.MatrixSimilarity(self.model[self.corpus])
        index.save(fname + '.ldaidx')    
    
        
class Similarity(object):
    '''
    utility class for similarity queries. (uses already created index)
    '''
    def __init__(self, corpusname):
        self.corpusname = corpusname
        self.index = None
        self.model = None
        self.dictionary = None
        self.filelist = None
        
    def init(self):
        if not self.filelist:
            with open(self.corpusname +'.filelist', "rb") as fp:
                self.filelist = pickle.load(fp)
                print "num files %d" % len(self.filelist)
        if not self.dictionary:
            self.dictionary = corpora.dictionary.Dictionary.load(self.corpusname+'.corpus')
            print self.dictionary
        if not self.model:
            self.model = models.LdaModel.load(self.corpusname + '.lda')
            print self.model
        if not self.index :
            self.index =  similarities.MatrixSimilarity.load(self.corpusname + '.ldaidx')
            

    def query(self, filename, numdocs=10):
        '''
        query the document similar to given document.
        '''
        self.init()
        doc = _tokenize_text_file(filename)
        #tokenize the document
        
        #convert the document to vector space
        vec_bow = self.dictionary.doc2bow(doc)
        
        #conver the query LDA space
        vec_lda = self.model[vec_bow] # convert the query to LSI space
        #query for similarity
        sims = self.index[vec_lda]
        docs = sorted(enumerate(sims), key=lambda item: item[1], reverse=True)
        docs = docs[:numdocs]
        
        for docidx, sim in docs:
            yield self.filelist[docidx], sim
        
    def print_similar_docs(self, filename, numdocs=10):
        for docname, sim in self.query(filename, numdocs):
            print "%s : %.8f" % (docname, sim)
    