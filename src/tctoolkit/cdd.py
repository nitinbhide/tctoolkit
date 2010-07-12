'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

from __future__ import with_statement

from contextlib import contextmanager
import sys

from codedupdetect.codedupdetect import CodeDupDetect
from optparse import OptionParser

from tctoolkitutil.common import *
from tctoolkitutil.treemapdata import TreemapNode
from tctoolkitutil.tktreemap import TreemapSquarified,TMColorMap,createScrollableCanvas
from tctoolkitutil.tkcanvastooltip import TkCanvasToolTip

import Tkinter
from idlelib.TreeWidget import TreeItem, TreeNode

import string, os, datetime

CLR_PROP = 'duplicate lines'
SIZE_PROP = 'filesize'

@contextmanager
def FileOrStdout(filename):
    output = sys.stdout
    if( filename != None):        
        try:
            output = open(filename, "w")
        except:
            pass
    yield(output)
    if( output != sys.stdout):
        output.close()
    
        
class CDDApp:
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
        self.cdd = CodeDupDetect(filelist,100)            
        self.PrintDuplicates()
        
        if( self.options.treemap == True):
            self.ShowDuplicatesTreemap()
            self.root.mainloop()        
    
    def PrintDuplicates(self):
        tm1 = datetime.datetime.now()
        with FileOrStdout(self.options.filename) as output:
            exactmatch = self.cdd.printmatches(output)
            tm2 = datetime.datetime.now()
            output.write("time to find matches - %s\n" %(tm2-tm1))

            
    def ShowDuplicatesTreemap(self):
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
        self.duplisttree.pack()
        self.pane.add(frame)
        self.pane.paneconfigure(frame, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)

    def initTreemap(self):
        self.tmcanvas = TreemapSquarified(self.pane,width='13i', height='8i',leafnodecb = self.tmLeafnodeCallback)
        self.tmcanvas.config(bg='white')
        self.tmcanvas.grid(sticky='nesw')
        self.tmcanvas.pack()
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
    parser = OptionParser(usage)

    parser.add_option("-p", "--pattern", dest="pattern", default='',
                      help="find duplications with files matching the pattern")
    parser.add_option("-t", "--treemap", action="store_true", dest="treemap", default=False,
                      help="display the duplication as treemap")
    parser.add_option("-f", "--file", dest="filename", default=None,
                      help="output file name. This is simple text file")
    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        print "Invalid number of arguments. Use cdd.py --help to see the details."
    else:        
        dirname = args[0]
        app = CDDApp(dirname, options)
        app.run()
            
if(__name__ == "__main__"):    
    RunMain()
    