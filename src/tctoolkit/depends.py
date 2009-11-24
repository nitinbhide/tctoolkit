'''
analyze the dependencies of individual source files. Calculates various metrics.
Uses Pygments to quickly parse source files.
'''

import sys

from tcdepends.dependency import Dependency

def RunMain():
    language='cpp'
    if( language == 'cpp'):
        dirname = "E:\\users\\nitinb\\sources\\tctools\\test\\apache_httpd"
        pathlist = ["E:\\users\\nitinb\\sources\\tctools\\test\\apache_httpd\\include"]
    if( language == 'java'):
        dirname = "E:\\users\\nitinb\\sources\\tctools\\test\\tomcat\\java"
        pathlist = ["E:\\users\\nitinb\\sources\\tctools\\test\\tomcat\\java"]
        
    #dirname = sys.argv[1]
    dep = Dependency(language, pathlist)
    dep.printDependency(dirname)
    
if __name__ == "__main__":
    RunMain()