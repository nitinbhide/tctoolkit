import sys,os,io
import string, sqlite3
import pandas as pd
from optparse import OptionParser
from datetime import datetime
from pygments.token import Comment,Token
from pygments.lexers import get_lexer_by_name
import codecs,traceback
sys.path.append("..")
from tctoolkitutil import DirFileLister
class Hierarchy():
    def __init__(self,parent=None):
        self.parent = parent
        self.cchild = 0
        self.stack = []
        self.depth = 0
        self.count = 0
        self.ccount=0
        
class Countlines():
    
    def __init__(self, language, dependspath=[]):
        dependencypath = dependspath
        self.language = language
        self.srcdir = None
        self.lexer = get_lexer_by_name(language)
        self.openlist = ["for","while","if","else","loop","until"]
        self.closelist = ['}', "end"]
        self.conn = sqlite3.connect("analysis.db")
        self.c = self.conn.cursor()

    def StripAtStart(self,src, strtostrip):
        if(src.startswith(strtostrip)):
            src = src[len(strtostrip):]
        return (src)
        
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
        
        self.c.execute(""" CREATE TABLE IF NOT EXISTS Files (FILENAME text PRIMARY KEY,DATE text,src_loc integer,total_loc integer)""")
        self.c.execute('''CREATE TABLE IF NOT EXISTS Blockdepth (FILENAME text ,Function text,Max_depth integer,loc integer, FOREIGN KEY (FILENAME)
         REFERENCES Files (FILENAME),UNIQUE(Filename,Function))''' )
        self.conn.commit()
        self.c.execute('DELETE FROM Blockdepth')
        for srcfile in filelist:
            a = self.Readfile(srcfile)
            try:
                c.execute('''INSERT INTO Files VALUES(?,?,?,?)''',(self.StripAtStart(srcfile,self.srcdir),datetime.now(),a[0],a[1]))
                conn.commit()
            except:
                pass
            self.Blockdept(srcfile)
            # break
        print (pd.read_sql_query("SELECT * FROM Blockdepth", self.conn))
        
    def Blockdept(self, srcfile):
        type1 = ['c', 'cpp', 'java', 'js','cs']
        type2 = ['rb', 'py']
        if self.StripAtStart(srcfile,self.srcdir).split('.')[1] in type1:
            return self.Type1(srcfile)
        else:
            return self.Type2(srcfile)

    def Type1(self, srcfile):
        function = []
        a = []
        startcal = 0
        gotfunc = False
        with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
            for ttype, value in self.lexer.get_tokens(code.read()):
                if gotfunc:
                    if value == '{':
                        startcal += 1
                        gotfunc = False
                    elif value == ';':
                        gotfunc = False
                        function.pop()
                        a[-1].count = 0
                        a.pop()
                    else:continue
                if ttype == Token.Name.Function :
                    gotfunc = True
                    if startcal:    
                        obj = Hierarchy(function[-1])
                    else:
                        obj = Hierarchy()
                    a.append(obj)
                    function.append(value)
                    a[-1].count += 1
                    continue
                if '{' == value and startcal:
                    a[-1].stack.append(1)
                    a[-1].depth = max(a[-1].depth, len(a[-1].stack))
                if '}'==value and startcal:
                    a[-1].stack.pop()
                if startcal and '\n' in value:
                    a[-1].count += 1

                if a and len(a[-1].stack) == 0 and a[-1].depth > 0:
                    if a[-1].parent:
                        a[-2].cchild = a[-1].depth
                        a[-2].ccount = a[-1].count
                    self.c.execute('''INSERT INTO Blockdepth VALUES(?,?,?,?)''',
                    (self.StripAtStart(srcfile,self.srcdir),function.pop(),a[-1].cchild+a[-1].depth,a[-1].count+a[-1].ccount))
                    self.conn.commit()
                    startcal -= 1
                    a.pop()

    def Type2(self, srcfile):
        function = []
        a = []
        d=dict()
        ans,count = 0,0
        countl,counts = 0,0
        countspace = False
        startcal = False
        with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
            for line in code.readlines():
                if len(line.strip()) == 0: continue
                # print(line)
                # print(len(line) - len(line.lstrip()))
                
                # for ttype, value in self.lexer.get_tokens(line):
                #     print(ttype,value)
                #     if countspace or ( len(line)-len(line.lstrip()) > counts):
                #         a.append(counts)
                #         counts = len(line)-len(line.lstrip())
                #         count += 1
                #         print(len(line)-len(line.lstrip()))
                #         ans = max(ans, count)
                    # if ttype == Token.Name.Function :
                    #     startcal = True
                    #     countspace=True
                    #     function.append(value)
                    #     count+=1
                    #     a.append(count)
                    #     countl+=1
                        
                    # if value in self.openlist:
                    #     countspace=True
                    # if (ttype == Token.Text):
                    #      print(len(value))
                    # elif value in self.closelist or (len(line)-len(line.lstrip())<counts):
                    #     countspace=False
                    #     counts = a.pop()
                    #     count-=1
                    
                    # if startcal and '\n' in value:countl+=1
                    # if not a and ans > 0:
                    #     countl+=1
                    #     d[function.pop()] = [ans,countl]
                    #     ans = 0
                    #     startcal = False
                    #     counts = 0
                    # if ans > 0 and not d:
                    #     d['-'] = [ans, countl]
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


# if value == 'GetName': print(ttype, value)
#                 if gotfunc:
#                     if value == '{':
#                         startcal = True
#                         gotfunc = False
#                     elif value == ';':
#                         gotfunc = False
#                         function.pop()
#                         count = 0
#                     else:continue
#                 if ttype == Token.Name.Function :
#                     gotfunc = True
#                     function.append(value)
#                     count += 1
#                     continue
#                 if '{' == value and startcal:
#                     a.append(1)
#                     ans = max(ans,len(a))
#                 if '}'==value and startcal:
#                     a.pop()
                
#                 if startcal and '\n' in value: count += 1
#                 if len(a) == 0 and ans > 0:
#                     if count>0:
#                         d[function.pop()] = [ans, count]
#                     else:function.pop()
#                     ans = 0
#                     startcal = False
#                     count = 0