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
import os.path
from cStringIO import StringIO
from itertools import groupby
from contextlib import closing

from optparse import OptionParser

from pygments.token import Token

from thirdparty.templet import unicodefunction

from tctoolkitutil import SourceCodeTokenizer
from tctoolkitutil import FileOrStdout
from tctoolkitutil import TCApp


class SignatureTokenizer(SourceCodeTokenizer):

    '''
    tokenize to return only the class names from the source file
    '''

    def __init__(self, srcfile, lang):
        super(SignatureTokenizer, self).__init__(srcfile, lang=lang)
        self.acceptable_values = set(["{", "}", ";", "'", '"'])

    def ignore_token(self, srctoken):
        '''
        ignore comments and any token not in the 'acceptable_values'
        '''
        ignore = True
        if(srctoken.is_type(Token.Comment)):
            ignore = True
        elif(len(srctoken.value) > 0 and srctoken.value[0] in self.acceptable_values):
            ignore = False
        return(ignore)


def truncate_string(str, maxchar):
    '''
    if str is larger than 5 characters truncate it to 5 characters
    '''
    str = str.strip().strip("\"'")
    if len(str) > maxchar:
        str = str[:maxchar] + '...'
    return '"%s"' % str


class WCSignatureSurvey(TCApp):

    '''
    Ward Cunningham's signature survey generation. Based on http://c2.com/doc/SignatureSurvey/
    '''

    def __init__(self, optparser):
        super(WCSignatureSurvey, self).__init__(optparser, 1)
        self.signatures = dict()

    def create_signatures(self):
        # first calculate all signatures
        for fname in self.getFileList(self.args[0]):
            print "Analyzing file %s" % fname

            tokenizer = SignatureTokenizer(fname, self.lang)
            with closing(StringIO()) as signature:

                for srctoken in tokenizer:
                    value = srctoken.value.strip()
                    if len(value) > 1 and srctoken.is_type(Token.Literal.String):
                        value = truncate_string(value, 5)

                    signature.write(value)
                self.signatures[fname] = signature.getvalue()

    def group_filenames(self):
        groups = dict()
        dirnames = list()
        filelist = sorted(
            self.filelist, key=lambda fname: os.path.dirname(fname))
        for dname, files in groupby(filelist, lambda fname: os.path.dirname(fname)):
            groups[dname] = list(files)      # Store group iterator as a list
            dirnames.append(dname)
        return dirnames, groups

    def _run(self):
        if not self.outfile:
            print "Please specify output filename (use option -o)"
            return

        self.create_signatures()
        # now group the filenames with directory names
        dirnames, filegroups = self.group_filenames()

        with open(self.outfile, "wb") as outfile:
            print "Writing the signature to %s" % self.outfile
            for dname in dirnames:
                outfile.write("%s\n" % dname)
                for fname in filegroups[dname]:
                    signature = self.signatures[fname]
                    fname = os.path.basename(fname)
                    outfile.write("\t%s : %s\n" % (fname, signature))
                outfile.write("\n")


def RunMain():
    usage = "usage: %prog [options] <directory name>"
    description = '''wc_survey (C) Nitin Bhide
    Generating Ward Cunningham 'signature survey' for code browsing. http://c2.com/doc/SignatureSurvey/
    '''
    parser = OptionParser(usage, description=description)

    app = WCSignatureSurvey(parser)
    app.run()

if(__name__ == "__main__"):
    RunMain()
