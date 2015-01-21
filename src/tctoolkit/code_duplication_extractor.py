'''
Copyright:   (c) Geometric 2015
Purpose: Runs CDD & Extracts code duplicate into a dictionary which can be consumed by another program
'''

import os
import sys


from tctoolkit.codedupdetect import CodeDupDetect
from tctoolkit import cdd

def extract_duplicates():
    cdd.RunMain()

if __name__=='__main__':
    extract_duplicates()