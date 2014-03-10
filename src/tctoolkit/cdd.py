'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

from __future__ import with_statement

import sys
import logging

from optparse import OptionParser

from tctoolkitutil.common import *
from codedupdetect.codedupdetect import CodeDupDetect

import string, os, datetime
        
class CDDApp(object):
    def __init__(self, dirname, options):
        self.dirname=dirname
        self.options = options
        self.filelist = None
        self.matches = None
        self.dupsInFile = None

    def getFileList(self):
        if( self.filelist == None):
            if( self.options.pattern ==''):
                self.filelist = PreparePygmentsFileList(self.dirname)
            else:
                rawfilelist = GetDirFileList(self.dirname)
                self.filelist = fnmatch.filter(rawfilelist,self.options.pattern)
                
        return(self.filelist)

    def run(self):
        filelist = self.getFileList()        
        self.cdd = CodeDupDetect(filelist,self.options.minimum, fuzzy=self.options.fuzzy, min_lines=self.options.min_lines)
        
        if self.options.format.lower() == 'html':
            self.cdd.html_output(self.options.filename)
        else:
            #assume that format is 'txt'.
            self.printDuplicates(self.options.filename)
            
        if self.options.comments:
            self.cdd.insert_comments(self.dirname)        
        
    def printDuplicates(self, filename):
        with FileOrStdout(filename) as output:
            exactmatch = self.cdd.printmatches(output)
            tm2 = datetime.datetime.now()            

    def foundMatches(self):
        '''
        return true if there is atleast one match found.
        '''
        matches = self.getMatches()
        return( len(matches) > 0)        
            
    def getMatches(self):
        if( self.matches == None):
            exactmatches = self.cdd.findcopies()
            self.matches = sorted(exactmatches,reverse=True,key=lambda x:x.matchedlines)
        return(self.matches)
    
                                  
def RunMain():
    usage = "usage: %prog [options] <directory name>"
    description = """Code Duplication Detector. (C) Nitin Bhide nitinbhide@thinkingcraftsman.in
    Uses RabinKarp algorithm for finding exact duplicates. Fuzzy duplication detection support is
    experimental.
    """
    parser = OptionParser(usage,description=description)

    parser.add_option("-p", "--pattern", dest="pattern", default='',
                      help="find duplications with files matching the pattern")
    parser.add_option("-c", "--comments", action="store_true", dest="comments", default=False,
                      help="Mark duplicate patterns in-source with c-style comment.")
    parser.add_option("-r", "--report", dest="report", default=None,
                      help="Output html to given filename.This is essentially combination '-f html -o <filename>")
    parser.add_option("-o", "--out", dest="filename", default=None,
                      help="output file name. This is simple text file")
    parser.add_option("-f", "--fmt", dest="format", default=None,
                      help="output file format. If not specified, determined from outputfile extension. Supported : txt, html")
    parser.add_option("-m", "--minimum", dest="minimum", default=100, type="int",
                      help="Minimum token count for matched patterns.")
    parser.add_option("", "--lines", dest="min_lines", default=3, type="int",
                      help="Minimum line count for matched patterns.")
    parser.add_option("-z", "--fuzzy", dest="fuzzy", default=False, action="store_true",
                      help="Enable fuzzy matching (ignore variable names, function names etc).")
    parser.add_option("-g", "--log", dest="log", default=False, action="store_true",
                      help="Enable logging. Log file generated in the current directory as cdd.log")
    (options, args) = parser.parse_args()
    
    if options.report != None:
        options.format = 'html'
        options.filename = options.report

    if options.format == None:
        #auto detect the format based on the out file extension.
        options.format = 'txt'
        if options.filename:
            name, ext = os.path.splitext(options.filename)
            if ext in set(['.html', '.htm', '.xhtml']):
                options.format = 'html'

    if( len(args) < 1):
        print "Invalid number of arguments. Use cdd.py --help to see the details."
    else:
        if options.log == True:
            logging.basicConfig(filename='cdd.log',level=logging.INFO)
            
        dirname = args[0]
        app = CDDApp(dirname, options)
        with TimeIt(sys.stdout, "Time to calculate the duplicates") as timer:
            app.run()
            
if(__name__ == "__main__"):    
    RunMain()
    