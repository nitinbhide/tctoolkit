'''
common.py
Common utility functions required for the other modules.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''

import os
import string
import sys
import time
import re
import codecs
from contextlib import contextmanager
    

@contextmanager
def FileOrStdout(filename):
    '''
    return an file or stdout if the name is None that can used with 'with' statement.
    '''
    #enter code
    output = sys.stdout
    if( filename != None):        
        try:
            output = codecs.open(filename, "wb", encoding='utf-8', errors= 'ignore')
        except:
            pass
    yield(output)
    #exit code
    if( output != sys.stdout):
        output.close()

@contextmanager
def TimeIt(fout,prefix=''):
    '''
    return a timer context manager. return the elapsed time.
    '''
    start_time = time.clock()
    
    yield
    
    end_time = time.clock()
    timediff = end_time - start_time
    fout.write("%s : %.2f seconds" % (prefix, timediff))
    

def StripAtStart(src, strtostrip):
    if( src.startswith(strtostrip)):
        src = src[len(strtostrip):]
    return(src)    

def readJsText(dirname, filename):
    '''
    read the entire text content of javascript file.
    '''
    jsfile = os.path.join(dirname, *filename)
    
    return open(jsfile, "r").read()

def getJsDirPath():
    '''
    get the javascript directory path based on path of the current script.
    '''
    srcdir = os.path.dirname(os.path.abspath(__file__))
    jsdir = os.path.join(srcdir, '..','thirdparty', 'javascript')
    jsdir = os.path.abspath(jsdir)
    return jsdir

