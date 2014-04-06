#!/usr/bin/env python
'''
featureanalysis_gensim.py
Detects features/ideas common in multiple source files. Useful in indentifying related files.
Uses 'gensim' library and LDA algorithms to detect topics in various code files.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''
import pickle
import os.path

from math import log
from numpy import *

from gensim import corpora, models, similarities
from gensim import utils

from tctoolkitutil import nnmf
from . import FeatureAnalysisBase
from .topictokenizer import STOPWORDS_SET
from .topictokenizer import TopicTokenizer

def _tokenize_text_file(fname):
    with open(fname, "r") as f:
        doc = f.read()
        
        for word in utils.tokenize(doc, lowercase=True):
            if word not in STOPWORDS_SET:
                yield word
        
class SourceCodeTextCorpus(object):
    def __init__(self, filelist):
        self.filelist = filelist
        self.dictionary = corpora.Dictionary()
        self.dictionary.add_documents(self.get_texts())
        #self.dictionary.filter_extremes()
        
    def get_texts(self):
        for fname in self.filelist:
            #print "tokenizing %s" % fname
            srccode_tokenizer =TopicTokenizer(fname)
            yield srccode_tokenizer.get_tokens()

    def __iter__(self):
        """
        The function that defines a corpus.

        Iterating over the corpus must yield sparse vectors, one for each document.
        """
        for text in self.get_texts():
            yield self.dictionary.doc2bow(text, allow_update=False)
        
    def __len__(self):
        return len(self.filelist)
    
    def __unicode__(self):
        '''
        print stats about the corpus
        '''
        return 'num docs : %d ' % self.dictionary.num_docs
    
    def __str__(self):
        return unicode(self)
    
    
class TopicAnalysisGensim(object):
    def __init__(self,filelist, corpusname, use_lsi=False):
        self.corpus = None
        self.corpusname = corpusname
        self.filelist = filelist

    def detectTopics(self):
        '''
        read the files and detect the topics in each file.
        '''
        print "Detecting Features"
        self.corpus = SourceCodeTextCorpus(self.filelist)
        print self.corpus
        
        self.topic_model = models.LsiModel(corpus=self.corpus, id2word=self.corpus.dictionary, num_topics=100)
        print self.topic_model
        
    def printFeatures(self, outfile):
        for topic in lda_model.print_topics(10):
            outfile.write(topic)
            outfile.write('\n')
            print topic
    
    def save(self, filename):
        #first save corpus
        fname, ext = os.path.splitext(filename)
        with open(fname +'.filelist', "wb") as fp:
            pickle.dump(self.filelist, fp) 
        self.corpus.dictionary.save(fname+'.corpus')
        #self.tfidf_model.save(fname+'.tfidf')
        self.topic_model.save(fname+'.model')
        index = similarities.MatrixSimilarity(self.topic_model[self.corpus])
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
            self.dictionary = corpora.Dictionary.load(self.corpusname+'.corpus')
            #print self.dictionary
        if not self.model:
            self.model = models.LsiModel.load(self.corpusname + '.model')
            #print self.model
        if not self.index :
            self.index =  similarities.MatrixSimilarity.load(self.corpusname + '.ldaidx')
            

    def find_topics(self, ntopics):
        '''
        find the topics from the corpus list. 
        '''
        self.init()
        self.model.print_topics(ntopics)
    
    def query(self, filename, numdocs=10):
        '''
        query the document similar to given document.
        '''
        self.init()
        #tokenize the document
        doc = _tokenize_text_file(filename)
        #convert the document to vector space
        vec_bow = self.dictionary.doc2bow(doc)
        #convert the query LDA space
        
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
    