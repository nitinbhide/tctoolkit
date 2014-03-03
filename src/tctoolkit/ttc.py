'''
Token Tag Cloud (TTC)
Create tag cloud of tokens used in source files. Tag size is based on the number of times token is used
and tag color is based on the type of token.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''

import string
import sys

from optparse import OptionParser

from tokentagcloud.tokentagcloud import *
from thirdparty.templet import stringfunction

class HtmlSourceTagCloud(SourceCodeTagCloud):
    '''
    Generate source code tag cloud in HTML format
    '''
    MINFONTSIZE = -2
    MAXFONTSIZE = 8

    def __init__(self, dirname, pattern):
        super(HtmlSourceTagCloud, self).__init__(dirname, pattern)
        self.maxFreqLog = 0.0
        self.minFreqLog = 0.0
        self.fontsizevariation = HtmlSourceTagCloud.MAXFONTSIZE-HtmlSourceTagCloud.MINFONTSIZE
        assert(self.fontsizevariation > 0)
        
    def __getTagFontSize(self, freq):
        #change the font size between MINFONTSIZE to MAXFONTSIZE relative to current font size
        #now calculate the scaling factor for scaling the freq to fontsize.
        scalingFactor = self.fontsizevariation/(self.maxFreqLog-self.minFreqLog)
        fontsize = int(HtmlSourceTagCloud.MINFONTSIZE+((math.log(freq)-self.minFreqLog)*scalingFactor)+0.5)
        #now round off to ensure that font size remains in MINFONTSIZE and MAXFONTSIZE
        assert(fontsize >= HtmlSourceTagCloud.MINFONTSIZE and fontsize <= HtmlSourceTagCloud.MAXFONTSIZE)
        return(fontsize)
    
    def getTagCloudHtml(self,numWords=100, filterFunc=None):
        tagHtmlStr = ''

        tagWordList = self.getTags(numWords, filterFunc)
                
        if( len(tagWordList) > 0):                        
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
    

@stringfunction
def OutputTagCloud(tagcld):
    '''<html>
    <head>
    <style type="text/css">
    .tagword { border : 1px groove blue }
    .tagcloud { text-align:justify }
    </style>
    </head>
    <body>
    <h2 align="center">Language Keyword Tag Cloud</h2>
    <p class="tagcloud">
    ${ tagcld.getTagCloudHtml(filterFunc=KeywordFilter)}
    </p>
    <hr/>
    <h2 align="center">Names (classname, variable names) Tag Cloud</h2>
    <p class="tagcloud">
    ${ tagcld.getTagCloudHtml(filterFunc=NameFilter) }    
    </p>
    <hr/>
    <h2 align="center">Class Name/Function Name Tag Cloud</h2>
    <p class="tagcloud">
    ${ tagcld.getTagCloudHtml(filterFunc=ClassFuncNameFilter) }
    </p>
    <hr/>
    </body>
    </html>
    '''    
    
def RunMain():
    usage = "usage: %prog [options] <directory name>"
    parser = OptionParser(usage)

    parser.add_option("-p", "--pattern", dest="pattern", default='*.c',
                      help="create tag cloud of files matching the pattern")
    parser.add_option("-o", "--outfile", dest="outfile", default=None,
                      help="outfile name. Output to stdout if not specified")
    
    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        print "Invalid number of arguments. Use ttc.py --help to see the details."
    else:        
        dirname = args[0]
            
        tagcld = HtmlSourceTagCloud(dirname, options.pattern)
        
        with FileOrStdout(options.outfile) as outf:
            outf.write(OutputTagCloud(tagcld))
                
        
if(__name__ == "__main__"):
    RunMain()
    
    