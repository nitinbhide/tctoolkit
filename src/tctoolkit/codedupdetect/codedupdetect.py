# -*- coding: utf-8 -*-
'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''



import logging
import tempfile
import os
import shutil
from itertools import tee

from . import matchstore
from .rabinkarp import RabinKarp


class CodeDupDetect(object):

    def __init__(self, filelist, chunk=5, fuzzy=False, min_lines=3, blameflag=False):
        self.chunk = chunk  # minimum number of tokens to be matched.
        self.matchstore = matchstore.MatchStore(chunk, blameflag)
        self.min_lines = min_lines  # minimum number of lines to match
        self.filelist = filelist
        self.foundcopies = False
        self.fuzzy = fuzzy

    def __find_rk_copies(self):
        '''
        detect exact copies using the RabinKarp algorithm
        '''
        totalfiles = len(self.filelist)

        rk = RabinKarp(self.chunk, self.min_lines, self.matchstore, self.fuzzy)

        for i, srcfile in enumerate(self.filelist):
            print("Analyzing file %s (%d of %d)" % (srcfile, i + 1, totalfiles))
            logging.info("Analyzing file %s (%d of %d)" %
                         (srcfile, i + 1, totalfiles))
            rk.addAllTokens(srcfile)
        print("Total Hashes Stored %d\n" % len(self.matchstore.hashset))

        self.foundcopies = True

    def findcopies(self):
        if self.foundcopies == False:
            self.__find_rk_copies()
        return self.matchstore.iter_matches()

    def printmatches(self, output):
        exactmatches = self.findcopies()
        # now sort the matches based on the matched line count (in reverse)
        exactmatches = sorted(exactmatches, reverse=True, key=lambda x: x.matchedlines)
        duplicateLineCount = 0
        for matchidx, matches in enumerate(exactmatches, 1):
            output.write('%s\n' % ('=' * 50))
            output.write("Match %d:\n" % matchidx)
            fcount = len(matches)
            duplicateLineCount = duplicateLineCount+matches.getDuplicateLineCount()
            output.write("Found an minimum %d line duplication in %d files.\n" % (matches.matchedlines, fcount))

            for match in matches:
                output.write("Starting at line %d of %s\n" %
                             (match.getStartLine(), match.srcfile()))
        
        output.write("\n\nTotal Duplicate Lines : %d" % duplicateLineCount)

        return exactmatches

    def insert_comments(self, dirname):
        begin_no = 0
        for matches in sorted(self.findcopies(), reverse=True, key=lambda x: x.matchedlines):
            for match in matches:
                fn = match.srcfile()
                infostring = ' '.join(['%s:%i+%i' % (f.srcfile(), f.getStartLine(), f.getLineCount())
                                       for f in matches if f.srcfile() != fn]).replace(dirname, '')
                tmp_source = tempfile.NamedTemporaryFile(
                    mode='wb', delete=False, prefix='cdd-')
                with open(fn, 'r') as srcfile:
                    for i in range(match.getStartLine()):
                        tmp_source.write(srcfile.readline())
                    comment = '//!DUPLICATE BEGIN %i -- %s\n' % (
                        begin_no, infostring)
                    tmp_source.write(comment)
                    for i in range(match.getLineCount()):
                        line = srcfile.readline()
                        tmp_source.write(line)
                        # with open('/tmp/%i.dup'%begin_no, 'a') as dup:
                        #    dup.write(line)
                    comment = '//!DUPLICATE END %i\n' % begin_no
                    tmp_source.write(comment)
                    line = srcfile.readline()
                    while line:
                        tmp_source.write(line)
                        line = srcfile.readline()
                # this should also work on windows
                tmp_source_name = tmp_source.name
                tmp_source.close()
                shutil.copy(tmp_source_name, fn)
                begin_no += 1

    def getCooccuranceData(self, dirname):
        '''
        create a co-occurance data in nodes and links list format. Something that can be
        dumped to json quickly
        '''
        groups = dict()  # key = directory name, value = index
        nodes = dict()  # key = filename, value = index
        # key (filename, filename), value = number of ocurrances
        links = dict()

        # add group (directory of the file) into the groups list
        def addGroup(filename):
            dir_of_file = os.path.dirname(filename)
            if dir_of_file not in groups:
                groups[dir_of_file] = len(groups)

        # add file into file list
        def addNode(filename):
            filename = os.path.relpath(filename, dirname)
            addGroup(filename)
            if filename not in nodes:
                nodes[filename] = len(nodes)

        # add a link (duplication) between two files into links list.
        def addLink(match1, match2):
            file1 = os.path.relpath(match1.srcfile(), dirname)
            file2 = os.path.relpath(match2.srcfile(), dirname)
            if file1 > file2:
                file1, file2 = file2, file1
            linkinfo = links.get((file1, file2), {'lines': 0, 'count': 0})
            linkinfo['lines'] = linkinfo['lines'] + match1.getLineCount()
            linkinfo['count'] = linkinfo['count'] + 1
            links[(file1, file2)] = linkinfo

        # copied from python recipes to get 'two' items at a time from list.
        # (n, n+1)
        def pairwise(iterable):
            "s -> (s0, s1), (s1, s2), (s2, s3), ..."
            a, b = tee(iterable)
            next(b, None)
            return zip(a, b)

        for matchset in self.findcopies():
            # for each matchset first add files into the nodes dictionary
            matchset = list(matchset)
            for match in matchset:
                addNode(match.srcfile())
            for match1, match2 in pairwise(matchset):
                addLink(match1, match2)

        # the child folders should be near to each other. Hence reindex of
        # groups list again.
        groupslist = sorted(groups.keys())
        for i, grp in enumerate(groupslist):
            groups[grp] = i

        return groups, nodes, links
