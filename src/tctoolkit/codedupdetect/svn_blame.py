'''
# Name:        svn_blame
# Purpose: detecting who copied whome from subverison history.
#
# Original Author:      Prashant Lade
#
# Created:     23/08/2013
# Copyright:   (c) prashantbl 2013
# Licence:     This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
# New BSD License: http://www.opensource.org/licenses/bsd-license.php
# TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
-------------------------------------------------------------------------------
'''
import logging
import getpass
import sys
import re
import urllib, urlparse
from collections import OrderedDict
import operator

import pysvn

class SvnBlameClient:
    def __init__(self, username=None, password=None):
        self.svnclient = pysvn.Client()
        self.svnclient.exception_style = 1
        self.svnclient.callback_get_login = self.get_login
        self.set_user_password(username, password)
        self.blame_cache = dict() #file name against blame output dictionary

    def set_user_password(self, username, password):
        if(username != None):
            self.username = username
            self.svnclient.set_default_username(self.username)
        if (password != None):
            self.password = password
            self.svnclient.set_default_password(self.password)

    def get_login(self, realm, username, may_save):
        logging.debug("This is a svnclient.callback_get_login event. ")
        if( self.username == None):
            self.username = raw_input("username for %s:" % realm)
        #save = True
        if( self.password == None):
            self.password = getpass.getpass()
        if(self.username== None or self.username ==''):
            retcode = False
        else:
            retcode = True
        return retcode, self.username, self.password, may_save

    def findAuthorForFragment(self, filepath, startLineNumber=1, endLineNumber=1):
        '''
        find who is the main author of startLine/endLine code fragment
        '''                                                         
        blame = self.getBlame(filepath)
        auhtorCounts = dict()
        
        startLineNumber = min(startLineNumber, len(blame))
        endLineNumber = min(endLineNumber, len(blame))
        #create a statistics of author and revisiona and how many lines are modified in that
        #(auth,revision) combination
        for lineinfo in blame[startLineNumber: endLineNumber]:
            lineauthor = lineinfo['author']
            linerevision = lineinfo['revision']
            auhtorCounts[(lineauthor,linerevision)] = auhtorCounts.get((lineauthor,linerevision), 0)+1

        #now findout which author modified maximum number of lines
        maxauthor = sorted(auhtorCounts.iteritems(), key = operator.itemgetter(1))
        maxauthor = maxauthor[0]
        #findout who make highest number of changes. This is tupple of the form ((author, revision), changedlinecount)
        #we just need 'author and revision'.
        return maxauthor[0]
        
    def getBlame(self, filepath):
        '''
        run the blame command on file. Read the blame for SVN or from cache.
        '''
        if filepath not in self.blame_cache:
            logging.debug('trying to extract annotations for %s' % filepath)
            output = self.svnclient.annotate(filepath)
            logging.debug('extracted annotations for %s' % filepath)
            blameout = list()
            for blamedict in output:
                blameinfo = dict()
                blameinfo['revision'] = blamedict['revision'].number
                blameinfo['author']= blamedict['author']
                blameout.append(blameinfo)
            self.blame_cache[filepath] = blameout

        return self.blame_cache[filepath]

def main():
    svnclient = SvnBlameClient()
    path = "file:///F:/repos/svnrepos/dokanrepo/trunk/dokan/cleanup.c"
    author = svnclient.findAuthorForFragment(path, 10,20)

if __name__ == '__main__':
    main()
