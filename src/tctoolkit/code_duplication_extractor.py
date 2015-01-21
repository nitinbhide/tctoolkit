'''
Copyright:   (c) Geometric 2015
Purpose: Runs CDD & Extracts code duplicate into a dictionary which can be consumed by another program
'''

import os
import sys


from tctoolkit.codedupdetect import CodeDupDetect
from tctoolkit import cdd

def extract_duplicates():
    cdd.getApp = lambda parser : DuplicatesExtractor(parser)
    cdd.RunMain()


class DuplicatesExtractor(cdd.CDDApp):
     def _run(self):
        filelist = self.getFileList(self.args[0])
        self.cdd = CodeDupDetect(filelist,self.options.minimum, fuzzy=self.options.fuzzy,\
                                 min_lines=self.options.min_lines, blameflag=self.options.blame)

        self.printDuplicates(self.outfile)


if __name__=='__main__':
    extract_duplicates()