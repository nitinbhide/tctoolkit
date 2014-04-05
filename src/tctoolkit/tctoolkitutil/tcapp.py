'''
tcapp.py

Base class for typical comamndline TCToolkit applications. Provides
1. iteration of files in directory based on language or pattern
2. storing default option parameters

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''

from .filelist import DirFileLister

class TCApp(object):
    '''
    Base class for typical comamndline TCToolkit applications. Provides
        1. iteration of files in directory based on language or pattern
        2. storing default option parameters
    '''

    def __init__(self, optparser, min_num_args):
        self.optparser=optparser
        self.min_num_args = min_num_args
        self.options = []
        self.args = []
        self.addDefaultOptions()
        
    def addDefaultOptions(self):
        self.optparser.add_option("-p", "--pattern", dest="pattern", default='*.c',
                      help="select matching the pattern. Default is '*.c' ")
        self.optparser.add_option("-o", "--outfile", dest="outfile", default=None,
                      help="outfile name. Output to stdout if not specified")
        self.optparser.add_option("-l", "--lang", dest="lang", default=None,
                      help="programming language. Pattern will be ignored if language is defined")
    
    def parse_args(self):
        self.options, self.args = self.optparser.parse_args()
        success=True
        if( len(self.args) < self.min_num_args):
            self.optparser.error( "Invalid number of arguments. Use %s --help to see the details." % self.optparser.get_prog_name())
            success = False
        else:
            self.lang = self.options.lang
            self.pattern = self.options.pattern
            self.outfile = self.options.outfile
            return True
        return success

    def getFileList(self, dirname=None):
        '''
        iterator over the file list based on the options parameters
        '''
        filelister = DirFileLister(dirname)

        #first add all names into the set               
        for fname in filelister.getFilesForPatternOrLang(pattern= self.pattern, lang=self.lang):
            yield fname

    def _run(self):
        '''
        to be implemented by the derived class
        '''
        raise NotImplementedError()

    def run(self):
        if self.parse_args():
            self._run()
                    