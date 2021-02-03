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
        c.execute(""" CREATE TABLE IF NOT EXISTS Files (FILENAME text,DATE text,LOC integer)""")
        c.execute("DELETE FROM Files")
        conn.commit()
        os.chdir('../metrics/test/')
        for srcfile in filelist:
            # self.Blockdept(srcfile)
            # break
            c.execute('''INSERT INTO Files VALUES(?,?,?)''',(self.StripAtStart(srcfile,self.srcdir),(datetime.now()),self.Readfile(srcfile)))
            conn.commit()
        print (pd.read_sql_query("SELECT * FROM Files", conn))
        
    def Blockdept(self, srcfile):
        d = dict()
        function = []
        a = []
        open = ['{',':']
        close = ['}']
        ans=0
        with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
            
            for ttype, value in self.lexer.get_tokens(code.read()):
                # print(ttype, value)
                if ttype == Token.Name.Function:
                    function.append(value)
                    
                if value in open:
                    a.append('{')
                    ans = max(ans, len(a))
                elif value in close:
                    a.pop()
                if not a and ans>0:
                    d[function.pop()] = ans
                    ans=0
        print(d)

    def Readfile(self, srcfile):
        commentlist = [Comment.Single, Comment.Multiline, Token.Literal.String.Doc, Token.Text,Token.Comment.Preproc]
        inquotes = [Token.Literal.String.Double, Token.Literal.String.Single]
        count = 0
        test=os.listdir("./")
        for item in test:
            if item.startswith("sample"):
                os.remove(item)
        extension=self.StripAtStart(srcfile,self.srcdir).split('.')[1]
        with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
            # ioread = io.StringIO(code.read())
            # print(ioread.read())
            with codecs.open("sample."+extension, "w+", encoding='utf-8', errors='ignore') as f:
                for r in code.readlines():
                    r = r.strip()
                    f.write(r+'\n')
            with codecs.open("sample."+extension, "rb", encoding='utf-8', errors='ignore') as f:
                countchars = 0
                for ttype, value in self.lexer.get_tokens(f.read()):
                    if ttype in inquotes:continue
                    if ( value == '\n' or ttype==Token.Comment.Single) and countchars>0:
                        count += 1
                        countchars=0
                    if (ttype not in commentlist):
                        countchars+=1
        return count
                

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