#!/usr/bin/env python
'''
featureanalysis.py
Do a feature analysis using NNMF (ref. Programming Collective Intelligence) of mulitple
source files to find common features across multiple files.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''
from __future__ import with_statement

import logging
import string
import sys,fnmatch
import math
from optparse import OptionParser

from tctoolkitutil.common import PreparePygmentsFileList
from featureanalysis.featureanalysis import FeatureAnalysis

def AnalyzeFeatures(dirname, pattern,outfilename):
    filelist = PreparePygmentsFileList(dirname)
    filelist = fnmatch.filter(filelist,pattern)
    
    feat = FeatureAnalysis()
    feat.detectFeatures(filelist)
    print "writing features to %s" % outfilename
    with open(outfilename, "wb") as outfile:
        feat.printFeatures(outfile)
    
def TestMain():
    #AnalyzeFeatures('./test/apache_httpd', '*.c', "features.txt")
    #AnalyzeFeatures('./test/tomcat', '*.java', "features.txt")
    AnalyzeFeatures('./test/ccnet/WebDashboard', '*.cs', "features.txt")
    
def RunMain():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    usage = "usage: %prog [options] <directory name>"
    parser = OptionParser(usage)

    parser.add_option("-p", "--pattern", dest="pattern", default='*.c',
                      help="do feature analysis of files matching the pattern")
    parser.add_option("-o", "--outfile", dest="outfile", default="features.txt",
                      help="outfile name. Output to stdout if not specified")
    
    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        print "Invalid number of arguments. Use featureanalysis.py --help to see the details."
    else:        
        dirname = args[0]
            
        AnalyzeFeatures(dirname, options.pattern, options.outfile)            
        
if(__name__ == "__main__"):
    RunMain()
    #TestMain()
    
    