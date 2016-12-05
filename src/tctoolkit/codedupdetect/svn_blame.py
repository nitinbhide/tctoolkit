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
import operator

from collections import OrderedDict

import pysvn

class BlameInfo(object):
    '''
    small class to store blame information. Uses slots to reduce 
    memory consumption.
    '''
    __slots__ = ['author', 'revision']
    def __init__(self, author, revision):
        self.author = author
        self.revision = revision


class SvnBlameClient(object):

    '''
    Subversion client to query the 'blame' information for a file.
    '''
    MAX_REVISIONS_FOR_BLAME = 100

    def __init__(self, username=None, password=None):
        self.svnclient = pysvn.Client()
        self.svnclient.exception_style = 1
        self.svnclient.callback_get_login = self.get_login
        self.set_user_password(username, password)
        self.blame_cache = OrderedDict()  # file name against blame output dictionary

    def set_user_password(self, username, password):
        if username != None:
            self.username = username
            self.svnclient.set_default_username(self.username)
        if password != None:
            self.password = password
            self.svnclient.set_default_password(self.password)

    def get_login(self, realm, username, may_save):
        logging.debug("This is a svnclient.callback_get_login event. ")
        if self.username == None:
            self.username = raw_input("username for %s:" % realm)
        #save = True
        if self.password == None:
            self.password = getpass.getpass()
        if self.username == None or self.username == '':
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
        # create a statistics of author and revisiona and how many lines are modified in that
        #(auth,revision) combination
        for lineinfo in blame[startLineNumber: endLineNumber]:
            lineauthor = lineinfo.author
            linerevision = lineinfo.revision
            auhtorCounts[(lineauthor, linerevision)] = auhtorCounts.get(
                (lineauthor, linerevision), 0) + 1

        # now findout which author modified maximum number of lines
        maxauthor = sorted(
            auhtorCounts.iteritems(), key=operator.itemgetter(1))
        maxauthor = maxauthor[0]
        # findout who make highest number of changes. This is tupple of the form ((author, revision), changedlinecount)
        # we just need 'author and revision'.
        return maxauthor[0]

    def getBlame(self, filepath):
        '''
        run the blame command on file. Read the blame for SVN or from cache.
        '''
        if filepath not in self.blame_cache:
            logging.debug('trying to extract annotations for %s' % filepath)

            revision_start = pysvn.Revision( pysvn.opt_revision_kind.number, 0 )
            revision_end = pysvn.Revision( pysvn.opt_revision_kind.head )

            #call 'log' and query the last 100 revisions of given file. For large repositories
            #annotate can put lot of stress on the server. Hence limit it to 100 revisions
            revlogs = self.svnclient.log(filepath, discover_changed_paths=False, 
                                         limit=self.MAX_REVISIONS_FOR_BLAME, include_merged_revisions=True,
                                         revprops = ['revision'])

            revision_start = revlogs[-1].revision
            revision_end = revlogs[0].revision
            output = self.svnclient.annotate(filepath,revision_start=revision_start,
                                             revision_end=revision_end)
            logging.debug('extracted annotations for %s' % filepath)

            blameout = list()

            for blamedict in output:
                blameinfo = BlameInfo(blamedict['author'], blamedict['revision'].number)
                blameout.append(blameinfo)
            self.blame_cache[filepath] = blameout

        return self.blame_cache[filepath]
