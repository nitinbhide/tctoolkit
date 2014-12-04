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

import pysvn
import getpass
import sys
import re
import urllib, urlparse
from collections import OrderedDict

class SvnBlameClient:
    def __init__(self, username=None, password=None):
        self.svnclient = pysvn.Client()
        self.svnclient.exception_style = 1
        self.svnclient.callback_get_login = self.get_login
        self.set_user_password(username, password)

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

    def runAnnotateCommand(self, filepath, startLineNumber=1, endLineNumber=1):
        blameDict = {}
        blameRevList = []
        print(filepath)
        output = self.svnclient.annotate(filepath)
        largestKey = 0
        for item in output:
            if(item['number'] >= startLineNumber and item['number'] <= endLineNumber):
                match = re.search('\d+>', str(item['revision']))
                blameDict[int(match.group()[:-1])] = str(item['author'])
                if largestKey < int(match.group()[:-1]):
                    largestKey = int(match.group()[:-1])
        return largestKey,  blameDict[largestKey]

def main():
##    svnclient = SvnBlameClient("file:///C:/SoftwareCOE/TechnicalAudit/Honda_Check/repo/documents/ApplicationDevelopment/Code/Code/MainTrunk")
##    filepath = "file:///C:/SoftwareCOE/TechnicalAudit/Honda_Check/repo/documents/ApplicationDevelopment/Code/Code/MainTrunk/Spinner/Business/SourceFiles/verfJPMasterVerficiationSearchSummary_mxJPO.java"
##    svnclient.runAnnotateCommand(filepath)
    pass

if __name__ == '__main__':
    main()
