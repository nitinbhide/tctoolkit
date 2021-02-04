import sys,os,io
import string, sqlite3
import pandas as pd
from optparse import OptionParser
from datetime import datetime
from pygments.token import Comment,Token
from pygments.lexers import get_lexer_by_name
import codecs
sys.path.append("..")
from tctoolkitutil import DirFileLister
class Countlines():
    def StripAtStart(self,src, strtostrip):
        if(src.startswith(strtostrip)):
            src = src[len(strtostrip):]
        return(src)
    def __init__(self, language, dependspath=[]):
        self.dependencypath = dependspath
        self.language = language
        self.srcdir = None
        self.lexer = get_lexer_by_name(language)

    def getFiles(self, srcdir):
        self.srcdir = srcdir
        if(self.srcdir.endswith(os.sep) == False):
            self.srcdir += os.sep
        filelister = DirFileLister(self.srcdir)
        filelist = filelister.getFilesForLang(self.language)
        return filelist

    def run(self,srcdir):
        filelist = self.getFiles(srcdir)
        # database
        conn = sqlite3.connect("analysis.db")
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS Files (FILENAME text PRIMARY KEY,DATE text,src_loc integer,total_loc integer)""")
        c.execute('''CREATE TABLE IF NOT EXISTS Blockdepth (FILENAME text PRIMARY KEY,Function text,Max_depth integer,loc integer, FOREIGN KEY (FILENAME)
       REFERENCES Files (FILENAME))''')
        c.execute("DELETE FROM Files")
        conn.commit()
        for srcfile in filelist:
            a=self.Readfile(srcfile)
            c.execute('''INSERT INTO Files VALUES(?,?,?,?)''',(self.StripAtStart(srcfile,self.srcdir),datetime.now(),a[0],a[1]))
            conn.commit()
            # for i, j in (self.Blockdept(srcfile).items()):
            #     c.execute('''INSERT INTO Blockdepth VALUES(?,?,?,?)''',(self.StripAtStart(srcfile,self.srcdir),i,j[0],j[1]))
            #     conn.commit()
        print (pd.read_sql_query("SELECT * FROM Blockdepth", conn))
        
    def Blockdept(self, srcfile):
        d = dict()
        function = []
        a = []
        open = ['{',':']
        close = ['}']
        ans = 0
        count = 0
        startcal = False
        with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
            for ttype, value in self.lexer.get_tokens(code.read()):
                if ttype == Token.Name.Function:
                    startcal=True
                    function.append(value)
                if value in open:
                    a.append(1)
                    ans = max(ans, len(a))
                elif value in close:
                    a.pop()
                if startcal and '\n' in value:count+=1
                if not a and ans > 0:
                    count+=1
                    d[function.pop()] = [ans,count]
                    ans = 0
                    startcal = False
                    count=0
        return d

    def Readfile(self, srcfile):
        commentlist = [Comment.Single, Comment.Multiline, Token.Literal.String.Doc, Token.Text,Token.Comment.Preproc]
        inquotes = [Token.Literal.String.Double, Token.Literal.String.Single]
        totalcount=0
        srccount = 0
        with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
            countchars = 0
            for ttype, value in self.lexer.get_tokens(code.read()):
                if ttype in inquotes:continue
                if ( '\n' in value or ttype==Token.Comment.Single) and countchars>0:
                    srccount += 1
                    countchars = 0
                if ('\n' in value):totalcount+=1
                if (ttype not in commentlist):
                    countchars += 1
        return [srccount,totalcount]
                

def RunMain():
    usage = "usage: %prog [options] <directory name>"
    parser = OptionParser(usage)

    parser.add_option("-l", "--lang", dest="lang", default='cpp',
                      help="programming language to determine the line of code (cpp, java or c#)")
    parser.add_option("-I", "--includes", dest="includespath", default='.',
                      help="list of include paths (seperated by ;)")

    (options, args) = parser.parse_args()
    if(len(args) < 1):
        print ("Invalid number of arguments. Use depends.py --help to see the details.")
    else:
        dirname = args[0]
        pathlist = options.includespath.split(';')
        pathlist.append('.')  # append current directory to search path
        print ("Language : %s" %(options.lang))
        print ("Dependency search path : %s" %options.includespath)
        print ("Counting loc ...")
        app = Countlines(options.lang, dirname)
        return app.run(dirname)


if __name__ == "__main__":
    RunMain()