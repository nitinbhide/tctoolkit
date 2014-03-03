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


@stringfunction
def OutputTagCloud(tagcld):
    '''<html>
    <style type="text/css">
    .tagword { border : 1px groove blue }
    .tagcloud { text-align:justify }
    </style>
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
            
        tagcld = SourceCodeTagCloud(dirname, options.pattern)
        
        fout = sys.stdout
        if( options.outfile != None):
            try:
                fout = open(options.outfile, "w")
            except:
                pass
        fout.write(OutputTagCloud(tagcld))
        if( fout != sys.stdout):
            fout.close()
                
        
if(__name__ == "__main__"):
    RunMain()
    
    