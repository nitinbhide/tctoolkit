# -*- coding: utf-8 -*-
'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import matchstore
from rabinkarp import RabinKarp
from tokenizer import Tokenizer


import tempfile
import os
import shutil
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter


class CodeDupDetect(object):
    def __init__(self,filelist, minmatch=100, fuzzy=False,min_lines=3):
        self.matchstore = matchstore.MatchStore(minmatch)
        self.minmatch = minmatch #minimum number of tokens to be matched.
        self.min_lines = min_lines # minimum number of lines to match
        self.filelist = filelist
        self.foundcopies = False
        self.fuzzy = fuzzy

    def __findcopies(self):
        totalfiles = len(self.filelist)
        
        rk = RabinKarp(self.minmatch,self.min_lines, self.matchstore, self.fuzzy)
            
        for i, srcfile in enumerate(self.filelist):
            print "Analyzing file %s (%d of %d)" %(srcfile,i+1,totalfiles)
            rk.addAllTokens(srcfile)
        self.foundcopies = True

    def findcopies(self):
        if( self.foundcopies == False):
            self.__findcopies()
        return(self.matchstore.iter_matches())

    def printmatches(self,output):
        exactmatches = self.findcopies()
        #now sort the matches based on the matched line count (in reverse)
        exactmatches = sorted(exactmatches,reverse=True,key=lambda x:x.matchedlines)
        matchcount=0

        for matches in exactmatches:
                output.write('%s\n'%('='*50))
                matchcount=matchcount+1
                output.write("Match %d:\n"%matchcount)
                fcount = len(matches)
                first = True
                for match in matches:
                        if( first):
                                output.write("Found an approx. %d line duplication in %d files.\n" % (match.getLineCount(),fcount))
                                first = False
                        output.write("Starting at line %d of %s\n" % (match.getStartLine(),match.srcfile()))

        return(exactmatches)

    def insert_comments(self, dirname):
        begin_no = 0
        for matches in sorted(self.findcopies(),reverse=True,key=lambda x:x.matchedlines):
            for match in matches:
                fn = match.srcfile()
                infostring = ' '.join(['%s:%i+%i'%(f.srcfile(),f.getStartLine(),f.getLineCount()) for f in matches if f.srcfile() != fn]).replace(dirname, '')
                tmp_source = tempfile.NamedTemporaryFile(mode='wb', delete=False, prefix='cdd-')
                with open(fn, 'r') as srcfile:
                    for i in range(match.getStartLine()):
                        tmp_source.write(srcfile.readline())
                    comment = '//!DUPLICATE BEGIN %i -- %s\n'%(begin_no, infostring)
                    tmp_source.write(comment)
                    for i in range(match.getLineCount()):
                        line = srcfile.readline()
                        tmp_source.write(line)
                        with open('/tmp/%i.dup'%begin_no, 'a') as dup:
                            dup.write(line)
                    comment = '//!DUPLICATE END %i\n'%begin_no
                    tmp_source.write(comment)
                    line = srcfile.readline()
                    while line:
                        tmp_source.write(line)
                        line = srcfile.readline()
                #this should also work on windows
                tmp_source_name = tmp_source.name
                tmp_source.close()
                shutil.copy(tmp_source_name, fn)
                begin_no += 1

    def html_output(self,outfile_fn):
        def code(match):
            with open(match.srcfile(), 'rb') as src:
                for i in range(match.getStartLine()):
                    src.readline()
                return [src.readline() for i in range(match.getLineCount())]
        #try:
        #    import chardet
        #    lexer = CppLexer(encoding='chardet')
        #except:
        #    lexer = CppLexer(encoding='utf-8')
            
        formatter = HtmlFormatter(encoding='utf-8')
        with open(outfile_fn, 'wb') as out:
            out.write('<html><head><style type="text/css">%s</style></head><body>'%formatter.get_style_defs('.highlight'))
            id = 0
            copies = sorted(self.findcopies(),reverse=True,key=lambda x:x.matchedlines)
            out.write('<ul>%s</ul>'%'\n'.join(['<a href="#match_%i">Match %i</a>'%(i,i) for i in range(len(copies))]))
            for matches in copies:
                out.write('<h1 id="match_%i">MATCH %i</h1><ul>'%(id,id))
                out.write(' '.join(['<li>%s:%i-%i</li>'%(m.srcfile(), m.getStartLine(), m.getStartLine() + m.getLineCount()) for m in matches]))
                out.write('</ul><div class="highlight">')
                highlight(''.join(code([s for s in matches][0])),Tokenizer.get_lexer2(m.srcfile()), formatter, outfile=out)
                out.write('<a href="#">Up</a></div>')
                id += 1
            out.write('</body></html>')
            