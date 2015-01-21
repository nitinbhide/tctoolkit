'''
Copyright:   (c) Geometric 2015
Purpose: Runs CDD & Extracts code duplicate into a dictionary which can be consumed by another program
'''

import os
import sys


from codedupdetect import CodeDupDetect
import cdd
import optparse

def extract_duplicates():
    cdd.getApp = lambda parser : DuplicatesExtractor(parser)
    parser = get_option_parser()
    app = cdd.getApp(parser)
    app.run()
    return app.extract_duplicates()

def get_option_parser():
    return cdd.createOptionParser()

class DuplicatesExtractor(cdd.CDDApp):
    def _run(self):
        filelist = self.getFileList(self.args[0])
        self.cdd = DuplicatesDetector(filelist,self.options.minimum, fuzzy=self.options.fuzzy,\
                                 min_lines=self.options.min_lines, blameflag=self.options.blame)

        self.printDuplicates(self.outfile)

    def extract_duplicates(self):
        return self.cdd.extract_matches()


class DuplicatesDetector(CodeDupDetect):
    def extract_matches(self):
        exactmatches = self.findcopies()
        #now sort the matches based on the matched line count (in reverse)
        exactmatches = sorted(exactmatches,reverse=True,key=lambda x:x.matchedlines)
        matchcount=0

        dups = {}
        for matches in exactmatches:
            matchcount=matchcount+1
            fcount = len(matches)
            dups[matchcount] = {}
            dups[matchcount].update({'fcount':fcount})
            first = True
            for match in matches:
                if( first):
                    dups[matchcount].update({'linecount':match.getLineCount()})
                    first = False

        return dups


if __name__=='__main__':
    print extract_duplicates()