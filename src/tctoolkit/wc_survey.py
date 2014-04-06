'''
wc_survey.py
Generating Ward Cunningham 'signature survey' for code browsing. http://c2.com/doc/SignatureSurvey/

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''

import logging
import itertools
import operator
import json
import math
from cStringIO import StringIO

from optparse import OptionParser

from pygments.token import Token

from thirdparty.templet import stringfunction

from tctoolkitutil import SourceCodeTokenizer
from tctoolkitutil import FileOrStdout
from tctoolkitutil import TCApp

class SignatureTokenizer(SourceCodeTokenizer):
    '''
    tokenize to return only the class names from the source file
    '''
    def __init__(self, srcfile, lang):
        super(SignatureTokenizer, self).__init__(srcfile,lang=lang)
        self.acceptable_values = set(["{", "}", ";" ,"'", '"'])
        
    def ignore_token(self, srctoken):        
        ignore = True
        if(srctoken.is_type(Token.Comment) ):
            ignore=True
        elif( len(srctoken.value) > 0 and srctoken.value[0] in self.acceptable_values):
            ignore = False
        return(ignore)


class WCSignatureSurvey(TCApp):
    '''
    Ward Cunningham's signature survey generation. Based on http://c2.com/doc/SignatureSurvey/
    '''
    def __init__(self, optparser):
        super(WCSignatureSurvey, self).__init__(optparser, 1)

    def _run(self):
        with open(self.outfile, "wb") as outfile:
            for fname in self.getFileList(self.args[0]):
                print "Analyzing file %s" % fname
                outfile.write("%s : "% fname)
               
                tokenizer = SignatureTokenizer(fname, self.lang)
                signature= StringIO()

                for srctoken in tokenizer:
                    value =srctoken.value.strip()
                    signature.write(value)
                outfile.write("%s\n" % signature.getvalue())
                signature.close()
        
def RunMain():
    usage = "usage: %prog [options] <directory name>"
    description = '''wc_survey (C) Nitin Bhide
    Generating Ward Cunningham 'signature survey' for code browsing. http://c2.com/doc/SignatureSurvey/
    '''
    parser = OptionParser(usage,description=description)
    
    app = WCSignatureSurvey(parser)
    app.run()
                    
if(__name__ == "__main__"):
    RunMain()
    
