'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

from __future__ import with_statement

import sys
import logging

from optparse import OptionParser

from tctoolkitutil.common import *
from codedupdetect.codedupdetect import CodeDupDetect

try:
    import Tkinter
    from idlelib.TreeWidget import TreeItem, TreeNode
    
    from tctoolkitutil.treemapdata import TreemapNode
    from tctoolkitutil.tktreemap import TreemapSquarified,TMColorMap,createScrollableCanvas
    from tctoolkitutil.tkcanvastooltip import TkCanvasToolTip
    
except:
    class TreeItem(object):
        pass
    
    print "Unable to import tkinter. Treemap will not be available."

import string, os, datetime

CLR_PROP = 'duplicate lines'
SIZE_PROP = 'filesize'
        
class CDDApp(object):
    def __init__(self, dirname, options):
        self.dirname=dirname
        self.options = options
        self.filelist = None
        self.matches = None
        self.dupsInFile = None

    def getFileList(self):
        if( self.filelist == None):
            if( self.options.pattern ==''):
                self.filelist = PreparePygmentsFileList(self.dirname)
            else:
                rawfilelist = GetDirFileList(self.dirname)
                self.filelist = fnmatch.filter(rawfilelist,self.options.pattern)
                
        return(self.filelist)

    def run(self):
        filelist = self.getFileList()        
        self.cdd = CodeDupDetect(filelist,self.options.minimum, fuzzy=self.options.fuzzy, min_lines=self.options.min_lines)
        
        if self.options.format.lower() == 'html':
            self.cdd.html_output(self.options.filename)
        else:
            #assume that format is 'txt'.
            self.printDuplicates(self.options.filename)
            
        if self.options.comments:
            self.cdd.insert_comments(self.dirname)        
        if( self.options.treemap == True and self.foundMatches()):
            self.ShowDuplicatesTreemap()
            self.root.mainloop()        
    
    def printDuplicates(self, filename):
        tm1 = datetime.datetime.now()
        with FileOrStdout(filename) as output:
            exactmatch = self.cdd.printmatches(output)
            tm2 = datetime.datetime.now()
            output.write("time to find matches - %s\n" %(tm2-tm1))

    def foundMatches(self):
        '''
        return true if there is atleast one match found.
        '''
        matches = self.getMatches()
        return( len(matches) > 0)
            
    def ShowDuplicatesTreemap(self):
        assert(self.foundMatches()==True)
        self.initTk()
        self.createTreemap()
        self.showDupListTree()
        
    def initTk(self):
        self.root = Tkinter.Tk()
        self.root.title("Code Duplication Treemap")
        self.pane = Tkinter.PanedWindow(self.root, orient=Tkinter.HORIZONTAL)
        self.pane.pack(fill=Tkinter.BOTH, expand=1)
        self.initDupListTree()
        self.initTreemap()
        
    def initDupListTree(self):
        frame = Tkinter.Frame(self.pane)
        self.duplisttree = createScrollableCanvas(frame, width='2i')
        self.pane.add(frame)
        self.pane.paneconfigure(frame, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)

    def initTreemap(self):
        self.tmcanvas = TreemapSquarified(self.pane,width='13i', height='8i',leafnodecb = self.tmLeafnodeCallback)
        self.tmcanvas.config(bg='white')
        self.pane.add(self.tmcanvas.frame)
        self.pane.paneconfigure(self.tmcanvas.frame, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
        self.tooltip = TkCanvasToolTip(self.tmcanvas, follow=True)

    def getColormap(self,tmrootnode):
        clrmap = TMColorMap(minclr=(0,255,0),maxclr=(255,0,0))        
        minval = tmrootnode.minclr(CLR_PROP)
        maxval = tmrootnode.maxclr(CLR_PROP)
        clrmap.setlimits(minval,maxval, neutralval=3)
        return(clrmap)
        
    def createTreemap(self):
        tmrootnode = self.makeTree()
        clrmap = self.getColormap(tmrootnode)
        self.tmcanvas.set(tmcolormap=clrmap,sizeprop=SIZE_PROP,clrprop=CLR_PROP,upper=[1200,700])
        self.tmcanvas.drawTreemap(tmrootnode)
        self.tooltip.updatebindings()

    def getMatches(self):
        if( self.matches == None):
            exactmatches = self.cdd.findcopies()
            self.matches = sorted(exactmatches,reverse=True,key=lambda x:x.matchedlines)
        return(self.matches)
    
    def getMatchLcInfo(self):
        #get the line count information of the duplicates
        matches = self.getMatches()
        #convert the matches to dictionary of filename against the number of copied lines
        matchinfodict = dict()
        for matchset in matches:
            for match in matchset:
                fname = match.srcfile()
                lc = matchinfodict.get(fname, 0)
                matchinfodict[fname] = lc + match.getLineCount()
        return(matchinfodict)

    def getLcInfo(self):
        #get the line count information about the files
        filelist = self.getFileList()
        lcinfodict = dict()
        for fname in filelist:
            with open(fname, "r") as f:
                lines = f.readlines()
                lcinfodict[fname] = len(lines)
        return(lcinfodict)
    
    def makeTree(self):
        matchlcinfo = self.getMatchLcInfo()
        lcinfo = self.getLcInfo()        
        tmrootnode = TreemapNode("Duplication Map - ")
        for fname, lc in lcinfo.iteritems():
            namelist = fname.split(os.sep)
            node = tmrootnode.addChild(namelist)
            node.setProp(SIZE_PROP, lc)
            node.setProp(CLR_PROP, matchlcinfo.get(fname, 0))
            node.setProp('filename', fname)
        tmrootnode.MergeSingleChildNodes('/')
        return(tmrootnode)

    def getDupsInFile(self,fname):
        if( self.dupsInFile == None):
            matches = self.getMatches()
            self.dupsInFile = dict()
            for matchset in matches:
                for match in matchset:
                    fname = match.srcfile()
                    duplist = self.dupsInFile.get(fname, [])
                    duplist.append((match.getStartLine(), match.getLineCount()))
                    self.dupsInFile[fname] = duplist
        return(self.dupsInFile.get(fname, None))
                
        
    def showDupListTree(self):
        mtreeroot = DupTreeItem("Duplicate List")
        #Add the tree items for various categories like (1-10 lines, 10-100 lines, 101-500 lines, More than 500 lines"
        dup500_ = mtreeroot.addChildName("More than 500 lines")
        dup101_500 = mtreeroot.addChildName("101-500 lines")
        dup11_100 = mtreeroot.addChildName("11-100 lines")
        dup1_10 = mtreeroot.addChildName("upto 10 lines")
        
        matchid = 0
        matches = self.getMatches()
        for matchset in matches:
            matchid = matchid+1
            matchnode = DupTreeItem("")
            lc = 0
            for match in matchset:
                fname = match.srcfile()
                lc = max(lc, match.getLineCount())
                start = match.getStartLine()
                matchnode.addChildName("%s (line %d - %d)" % (fname, start, start+lc))
            
            matchnode.name = "Match %d (Lines : %d)" % (matchid, lc)
            
            if( lc > 0 and lc <= 10):
                dup1_10.addChild(matchnode)
            elif( lc >10 and lc <= 100):
                dup11_100.addChild(matchnode)
            elif( lc >100 and lc < 500):
                dup101_500.addChild(matchnode)
            else:
                dup500_.addChild(matchnode)        
        
        for child in mtreeroot.children:
            child.name = "%s (count : %d)" % (child.name, len(child.children))
        
        #now create a 'tree display"
        self.filetree = TreeNode(self.duplisttree, None, mtreeroot)
        self.filetree.update()
        self.filetree.expand()
        
    def tmLeafnodeCallback(self, node, tmcanvas, canvasid,lower,upper):
        '''
        draw the approx positions for the duplicates in 'dark brown' color on the
        canvas rectangles of that file.
        '''        
        width = upper[0]-lower[0]
        height = float(upper[1]-lower[1])
            
        if( width > 4 and height > 2):            
            fname = node.getProp('filename')
            assert(fname != None)
            dupsinfile = self.getDupsInFile(fname)
            #if dupsinfile is None, then there are no duplicates in file
            if( dupsinfile != None):
                fsize = float(node.getSize(SIZE_PROP))
                x = lower[0]
                y = lower[1]
                #show small magenta coloured strip of 4 pixels (rectwd) to represent the location
                #of duplication.
                rectwd = 4
                    
                for startline, linecount in dupsinfile:
                    rectht = int(height*(float(linecount)/fsize)+0.5)
                    if( rectht > 1):
                        rectstart = int(height*(float(startline)/fsize)+0.5)
                        #draw rectangle with 'magenta' color fill and no border (border width=0)
                        tmcanvas.create_rectangle(x+2, y+rectstart, x+rectwd+2, y+rectstart+rectht,
                                                  fill='magenta',width=0)
            
class DupTreeItem(TreeItem):
    def __init__(self, name):
        self.name = name
        self.children = []
        
    def GetText(self):
        return(self.name)
        
    def IsExpandable(self):
        return len(self.children) > 0

    def addChild(self, child):
        self.children.append(child)

    def addChildName(self, name):
        child = DupTreeItem(name)
        self.addChild(child)
        return(child)
    
    def GetSubList(self):        
        return(self.children)
    
    def OnDoubleClick(self):
        pass
        
def RunMain():
    usage = "usage: %prog [options] <directory name>"
    description = """Code Duplication Detector. (C) Nitin Bhide nitinbhide@thinkingcraftsman.in
    Uses RabinKarp algorithm for finding exact duplicates. Fuzzy duplication detection support is
    experimental.
    """
    parser = OptionParser(usage,description=description)

    parser.add_option("-p", "--pattern", dest="pattern", default='',
                      help="find duplications with files matching the pattern")
    parser.add_option("-t", "--treemap", action="store_true", dest="treemap", default=False,
                      help="display the duplication as treemap")
    parser.add_option("-c", "--comments", action="store_true", dest="comments", default=False,
                      help="Mark duplicate patterns in-source with c-style comment.")
    parser.add_option("-r", "--report", dest="report", default=None,
                      help="Output html to given filename.This is essentially combination '-f html -o <filename>")
    parser.add_option("-o", "--out", dest="filename", default=None,
                      help="output file name. This is simple text file")
    parser.add_option("-f", "--fmt", dest="format", default="txt",
                      help="output file format. Supported : txt, html")
    parser.add_option("-m", "--minimum", dest="minimum", default=100, type="int",
                      help="Minimum token count for matched patterns.")
    parser.add_option("", "--lines", dest="min_lines", default=3, type="int",
                      help="Minimum line count for matched patterns.")
    parser.add_option("-z", "--fuzzy", dest="fuzzy", default=False, action="store_true",
                      help="Enable fuzzy matching (ignore variable names, function names etc).")
    parser.add_option("-g", "--log", dest="log", default=True, action="store_true",
                      help="Enable logging. Log file generated in the current directory as cdd.log")
    (options, args) = parser.parse_args()
    
    if options.report != None:
        options.format = 'html'
        options.filename = options.report
        
    if( len(args) < 1):
        print "Invalid number of arguments. Use cdd.py --help to see the details."
    else:
        if options.log == True:
            logging.basicConfig(filename='cdd.log',level=logging.DEBUG)
            
        dirname = args[0]
        app = CDDApp(dirname, options)
        app.run()
            
if(__name__ == "__main__"):    
    RunMain()
    