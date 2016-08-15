'''
This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

Purpose: Runs CDD & Extracts code duplicate into a dictionary which can be consumed by another program
Reading Convention: view the code top to bottom. Callers are at the top, followed by callees.
'''

from codedupdetect import CodeDupDetect
import cdd
import os


def extract_duplicates(optionparser=None):
    parser = cdd.createOptionParser() if (
        optionparser == None) else optionparser
    
    app = DuplicatesExtractor(parser)
    app.run()
    return app.extract_duplicates()

#-------------------------------------------------------------


class DuplicatesExtractor(cdd.CDDApp):

    def getCDDInstance(self):
        filelist = self.getFileList(self.args[0],'')
        return DuplicatesDetector(filelist, self.options.minimum, fuzzy=self.options.fuzzy,
                                  min_lines=self.options.min_lines, blameflag=self.options.blame)

    def extract_duplicates(self):
        dups = self.cdd.extract_matches()
        analytics = extract_dups_analytics(dups)
        dups.update(analytics)
        return dups

#-------------------------------------------------------------


class DuplicatesDetector(CodeDupDetect):

    def extract_matches(self):
        exactmatches = self.findcopies()
        # now sort the matches based on the matched line count (in reverse)
        exactmatches = sorted(
            exactmatches, reverse=True, key=lambda x: x.matchedlines)
        matchcount = 0

        dups = {}
        for matches in exactmatches:
            matchcount = matchcount + 1
            fcount = len(matches)
            dups[matchcount] = {}
            dups[matchcount].update({'fcount': fcount})
            first = True
            for match in matches:
                if(first):
                    dups[matchcount].update(
                        {'linecount': match.getLineCount()})
                    first = False

        return dups
#-------------------------------------------------------------


def extract_dups_analytics(dups):
    data = {}
    data.update({'num_dups': len(dups.keys())})
    data.update({'num_dups_across_files': find_dups_across_files(dups)})
    data.update({'dups_loc': find_dups_loc(dups)})
    analytics = {'analytics': data}
    return analytics


def find_dups_across_files(dups):
    dups_across_files = dict((k, v)
                             for (k, v) in dups.iteritems() if v['fcount'] > 1)
    return len(dups_across_files.keys())


def find_dups_loc(dups):
    def add_loc(a, b):
        loc_item = b[1]['linecount']
        fcount_item = b[1]['fcount']
        accumulated_loc = a[1]['linecount']

        assert fcount_item > 1, '''Assumption based on existing behavior: Even if the duplicates are inside same file,
                the same file is repeated multiple times'''
        accumulated_loc = accumulated_loc + (loc_item * (fcount_item - 1))
        return ('don\'tcare', {'linecount': accumulated_loc, 'fcount': 0})

    loc = reduce(
        add_loc, dups.iteritems(), ('don\'tcare', {'linecount': 0, 'fcount': 0}))
    return loc[1]['linecount']

#----------------------------------------------------------------
if __name__ == '__main__':
    print extract_duplicates()
