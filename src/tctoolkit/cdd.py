'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

from __future__ import with_statement

from codedupdetect.codedupdetect import CodeDupDetect
from optparse import OptionParser
from tccatutil.common import *

from tccatutil.treemapdata import TreemapNode
from tccatutil.tktreemap import TreemapSquarified,TMColorMap
from tccatutil.tkcanvastooltip import TkCanvasToolTip

from Tkinter import Tk
import string, os, datetime

CLR_PROP = 'duplicate lines'
SIZE_PROP = 'filesize'

class CDDApp:
    def __init__(self, dirname, options):
        self.dirname=dirname
        self.options = options
        self.filelist = None

    def getFileList(self):
        if( self.filelist == None):
            if( self.options.pattern ==''):
                self.filelist = PreparePygmentsFileList(self.dirname)
            else:
                rawfilelist = GetDirFileList(self.dirname)
                self.filelist = fnmatch.filter(rawfilelist,self.options.pattern)
                
        return(self.filelist)

    def run(self):
        if( self.options.treemap == True):
            self.ShowDuplicatesTreemap()
            self.root.mainloop()
        else:
            self.PrintDuplicates()
            
    def PrintDuplicates(self):
        filelist = self.getFileList()
        tm1 = datetime.datetime.now()
        cdd = CodeDupDetect(100)
        exactmatch = cdd.printmatches(filelist)
        tm2 = datetime.datetime.now()
        print "time to find matches : ",(tm2-tm1)
        
    def ShowDuplicatesTreemap(self):
        self.initTk()
        self.createTreemap()
        
    def initTk(self):
        self.root = Tk("CDD")
        self.root.title("Code Duplication Treemap")
        self.tmcanvas = TreemapSquarified(self.root,width='13i', height='8i')
        self.tmcanvas.config(bg='white')
        self.tmcanvas.grid(sticky='nesw')
        self.tmcanvas.pack()
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

    def getMatchLcInfo(self):
        filelist = self.getFileList()
        cdd = CodeDupDetect(100)
        exactmatches = cdd.findcopies(filelist)
        #convert the matches to dictionary of filename against the number of copied lines
        matchinfodict = dict()
        for matchset in exactmatches:
            for match in matchset:
                fname = match.srcfile()
                lc = matchinfodict.get(fname, 0)
                matchinfodict[fname] = lc + match.getLineCount()
        return(matchinfodict)

    def getLcInfo(self):
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
        tmrootnode.MergeSingleChildNodes('/', SIZE_PROP, CLR_PROP)
        return(tmrootnode)
            
            
def RunMain():
    usage = "usage: %prog [options] <directory name>"
    parser = OptionParser(usage)

    parser.add_option("-p", "--pattern", dest="pattern", default='',
                      help="find duplications with files matching the pattern")
    parser.add_option("-t", "--treemap", action="store_true", dest="treemap", default=False,
                      help="display the duplication as treemap")
    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        print "Invalid number of arguments. Use cdd.py --help to see the details."
    else:        
        dirname = args[0]
        app = CDDApp(dirname, options)
        app.run()
            
if(__name__ == "__main__"):    
    RunMain()
    