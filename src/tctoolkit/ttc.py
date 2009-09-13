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

def OutputTagCloud(outfilename, tmplDict):
    htmlTmplStr = '''
    <html>
    <style type="text/css">
    .tagword { border : 1px groove blue }
    .tagcloud { text-align:justify }
    </style>
    <body>
    <h2 align="center">Language Keyword Tag Cloud</h2>
    <p class="tagcloud">
    $KEYWORD_TAGSTR
    </p>
    <hr/>
    <h2 align="center">Names (classname, variable names) Tag Cloud</h2>
    <p class="tagcloud">
    $NAME_TAGSTR
    </p>
    <hr/>
    <h2 align="center">Class Name/Function Name Tag Cloud</h2>
    <p class="tagcloud">
    $CLASSFUNCNAME_TAGSTR
    </p>
    <hr/>
    </body>
    </html>
    '''
    htmlTmpl = string.Template(htmlTmplStr)   
    taghtml = htmlTmpl.safe_substitute(tmplDict)

    fout = sys.stdout
    if( outfilename != None):
        try:
            fout = open(outfilename, "w")
        except:
            pass
    fout.write(taghtml)
    if( fout != sys.stdout):
        fout.close()

    
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
            
        tmplDict = dict()
        tagcld = CreateTagCloud(dirname, options.pattern)
        
        tmplDict['KEYWORD_TAGSTR']= tagcld.getTagCloudHtml(filterFunc=KeywordFilter)
        tmplDict['NAME_TAGSTR']= tagcld.getTagCloudHtml(filterFunc=NameFilter)
        tmplDict['CLASSFUNCNAME_TAGSTR']= tagcld.getTagCloudHtml(filterFunc=ClassFuncNameFilter)
        
        OutputTagCloud(options.outfile, tmplDict)
        
if(__name__ == "__main__"):
    RunMain()
    
    