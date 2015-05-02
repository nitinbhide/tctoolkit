'''
Various dependency filters (extracting import, #include statements etc) for different lexers.
'''

import os
import string

from pygments.filter import simplefilter, Filter
from pygments.lexers import JavaLexer, CppLexer, CLexer, CSharpLexer
from pygments.token import Token

from tctoolkitutil.filelist import FindFileInPathList
from tctoolkitutil.common import StripAtStart


def get_import_filter(lexer, srcdir, depsearchpath):
    '''
    get the appropriate import filter for the given lexer.
    '''
    filter = None

    if(lexer.name == JavaLexer.name or lexer.name == CSharpLexer.name):
        filter = JavaImportFilter(srcdir, depsearchpath)
    elif(lexer.name == CppLexer.name or lexer.name == CLexer.name):
        filter = CppImportFilter(srcdir, depsearchpath)

    return(filter)


class DependencyFilter(Filter):

    def __init__(self, srcdir, depsearchpath):
        self.srcdir = srcdir
        self.dependencypath = depsearchpath
        Filter.__init__(self)

    def findFile(self, dependson):
        '''
        find the actual file the file search path and source directory based on the token returned by
        filter.
        '''
        fname = FindFileInPathList(dependson, self.dependencypath)
        if(fname != None):
            fname = StripAtStart(fname, self.srcdir)
        else:
            fname = dependson
        return(fname)


class CppImportFilter(DependencyFilter):

    def __init__(self, srcdir, filesearchpath):
        DependencyFilter.__init__(self, srcdir, filesearchpath)
        pass

    def filter(self, lexer, stream):
        '''
        filter the token stream and only return the dependency related tokens.
        '''
        searchfor = 'include'
        incstrlen = len(searchfor)
        for ttype, value in stream:
            if ttype in Token.Comment.Preproc and value.startswith(searchfor):
                value = value[incstrlen:]
                value = value.strip()
                # exclude the " or <>"
                value = value[1:-1]
                yield ttype, value


class JavaImportFilter(DependencyFilter):

    def __init__(self, srcdir, filesearchpath):
        DependencyFilter.__init__(self, srcdir, filesearchpath)
        pass

    def filter(self, lexer, stream):
        '''
        filter the token stream and only return the dependency related tokens.
        '''
        namespace = False
        for ttype, value in stream:
            if (ttype in Token.Name.Namespace):
                yield ttype, value

    def findFile(self, dependson):
        '''
        find the actual file the file search path and source directory based on the token returned by
        filter.
        '''
        # replace the 'dot' in the namespace name with filename seperator for
        # os.
        fname = dependson.replace('.', os.sep)

        fname = FindFileInPathList(fname, self.dependencypath, ['java'])
        if(fname != None):
            fname = StripAtStart(fname, self.srcdir)
        else:
            fname = dependson
        return(fname)
