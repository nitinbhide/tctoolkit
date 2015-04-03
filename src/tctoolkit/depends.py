'''
analyze the dependencies of individual source files. Calculates various metrics.
Uses Pygments to quickly parse source files.
'''

import sys
import string
from optparse import OptionParser

from tcdepends.dependency import Dependency


def RunMain():
    usage = "usage: %prog [options] <directory name>"
    parser = OptionParser(usage)

    parser.add_option("-l", "--lang", dest="lang", default='cpp',
                      help="programming language to determine the dependencies (cpp, java or c#)")
    parser.add_option("-I", "--includes", dest="includespath", default='.',
                      help="list of include paths (seperated by ;)")

    (options, args) = parser.parse_args()

    if(len(args) < 1):
        print "Invalid number of arguments. Use depends.py --help to see the details."
    else:
        dirname = args[0]
        pathlist = options.includespath.split(';')
        pathlist.append('.')  # append current directory to search path
        print "Language : %s" % (options.lang)
        print "Dependency search path : %s" % options.includespath
        print "Searching dependencies ..."
        dep = Dependency(options.lang, pathlist)
        dep.printDependency(dirname)

if __name__ == "__main__":
    RunMain()
