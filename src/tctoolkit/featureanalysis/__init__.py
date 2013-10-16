'''
Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''
import re

from pygments.token import Token
from tokentagcloud.tokentagcloud import Tokenizer

SPLIT_VAR_RE = re.compile("[A-Z_]+[a-z0-9]+")

STOPWORDS_SET= set(["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all",
                    "almost", "alone", "along", "already", "also","although","always","am","among", "amongst",
                    "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway",
                    "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes",
                    "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides",
                    "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant",
                    "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down",
                    "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty",
                    "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except",
                    "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly",
                    "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has",
                    "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon",
                    "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc",
                    "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly",
                    "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more",
                    "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither",
                    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing",
                    "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other",
                    "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps",
                    "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious",
                    "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some",
                    "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such",
                    "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then",
                    "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these",
                    "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout",
                    "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two",
                    "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what",
                    "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein",
                    "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole",
                    "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your",
                    "yours", "yourself", "yourselves", "the"]);

def split_variable_name(variable):
    '''
    split variable names like GetSomething into 'get' and 'something'. Use
    CamelCase and '_' as seperator.
    '''    
    tokens = SPLIT_VAR_RE.sub(lambda s: '_'+s.group(), variable)
    tokens = tokens.lower().strip('_').split('_')
    return tokens

def tokenize_file(fname):
    tokenzr = Tokenizer(fname)
    for ttype,tokenstr in tokenzr.get_tokens():
        if( ttype in Token.Name and (ttype in Token.Name.Class or ttype in Token.Name.Function) ):
                #split the variable and function names in word.
                for tk in split_variable_name(tokenstr):
                    if tk not in STOPWORDS_SET:
                        yield tk

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
            words=tokenize_file(fname)
            self.filewords.append({})
            fidx = len(self.filetitles)-1
            
            # Increase the counts for this word in allwords and in articlewords
            for word in words:
                self.allwords.setdefault(word,0)
                self.allwords[word]+=1
                self.filewords[fidx].setdefault(word,0)
                self.filewords[fidx][word]+=1
            
