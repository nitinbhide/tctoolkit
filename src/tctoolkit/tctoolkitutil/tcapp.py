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

import logging

from .filelist import DirFileLister
from .sourcetokenizer import SourceCodeTokenizer


class TCApp(object):

    '''
    Base class for typical comamndline TCToolkit applications. Provides
        1. iteration of files in directory based on language or pattern
        2. storing default option parameters using optparse (or its derived classes)
    '''

    def __init__(self, optparser, min_num_args):
        self.optparser = optparser
        self.min_num_args = min_num_args
        self.options = []
        self.args = []
        self.filelist = None
        self.addDefaultOptions()

    def prog_name(self):
        return self.optparser.get_prog_name().replace('.py', '')

    def addDefaultOptions(self):
        '''
        add the default options like 'logging' , 'file pattern' or 'langugage selection' to all
        applications.
        '''
        self.optparser.add_option("-g", "--log", dest="log", default=False, action="store_true",
                                  help="Enable logging. Log file generated in the current directory as %s.log" % self.prog_name())
        self.optparser.add_option("-p", "--pattern", dest="pattern", default='*.c',
                                  help="select matching the pattern. Default is '*.c' ")
        self.optparser.add_option("-o", "--outfile", dest="outfile", default=None,
                                  help="outfile name. Output to stdout if not specified")
        self.optparser.add_option("-l", "--lang", dest="lang", default=None,
                                  help="programming language. Pattern will be ignored if language is defined.")

    def parse_args(self):
        self.options, self.args = self.optparser.parse_args()
        success = True
        if(len(self.args) < self.min_num_args):
            self.optparser.error(
                "Invalid number of arguments. Use %s.py --help to see the details." % self.prog_name())
            success = False
        else:
            self.lang = self.options.lang
            self.pattern = self.options.pattern
            self.outfile = self.options.outfile
            success = False
            if self.options.log == True:
                logging.basicConfig(filename='%s.log' %
                                    self.prog_name(), level=logging.INFO)

            if self.lang:
                if not SourceCodeTokenizer.is_lang_supported(self.lang):
                    supported_lang = SourceCodeTokenizer.language_list()
                    msg = "Language %s is not supported.\n\nSupported languages are %s" % (
                        self.lang, '\n'.join(supported_lang))
                    self.optparser.error(msg)
                success = True
            elif self.pattern:
                success = True

        return success

    def getFileList(self, dirname=None, exclude_dirs=None):
        '''
        iterator over the file list based on the options parameters
        '''
        if self.filelist == None or self.dirname != dirname:
            self.dirname = dirname
            filelister = DirFileLister(self.dirname, exclude_dirs)

            # first add all names into the set
            self.filelist = filelister.getFilesForPatternOrLang(
                pattern=self.pattern, lang=self.lang)

        return self.filelist

    def _run(self):
        '''
        to be implemented by the derived class
        '''
        raise NotImplementedError()

    def run(self):
        '''
        parse the arguments using options parser and then call '_run' function for actually running
        the application.
        '''
        if self.parse_args():
            self._run()
