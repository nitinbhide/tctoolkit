'''
This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

Purpose: This is only the testdata for testing tctoolkit, not actual code of tctoolkit.
'''

#!/usr/bin/env python
import cookielib
import difflib
import getpass
import marshal
import mimetools
import ntpath
import os
import string
import re
import socket
import stat
import subprocess
import sys
import tempfile
import urllib
import urllib2
from optparse import OptionParser
from tempfile import mkstemp
from urlparse import urljoin, urlparse

try:
    from hashlib import md5
except ImportError:
    # Support Python versions before 2.5.
    from md5 import md5

try:
    import json
except ImportError:
    import simplejson as json

# This specific import is necessary to handle the paths for
# cygwin enabled machines.
if (sys.platform.startswith('win')
    or sys.platform.startswith('cygwin')):
    import ntpath as cpath
else:
    import posixpath as cpath

###
# Default configuration -- user-settable variables follow.
###

# The following settings usually aren't needed, but if your Review
# Board crew has specific preferences and doesn't want to express
# them with command line switches, set them here and you're done.
# In particular, setting the REVIEWBOARD_URL variable will allow
# you to make it easy for people to submit reviews regardless of
# their SCM setup.

def commit_file(filename):
    try:
        client = pysvn.Client()
        client.checkin([filename], 'Updating gsdsadmins list')
    except:
        print filename
        logger = get_logger()
        logger.error("%s is not part of working copy",filename)
        del logger

def commit_file(filename):
    try:
        client = pysvn.Client()
        client.checkin([filename], 'Updating gsdsadmins list')
    except:
        print filename
        logger = get_logger()
        logger.error("%s is not part of working copy",filename)
        del logger