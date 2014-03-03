'''
Test code for creating the treemap view with Tkinter.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''

from __future__ import with_statement

from tctoolkitutil.treemapdata import TreemapNode
from tctoolkitutil.tktreemap import TreemapSquarified,TMColorMap,createScrollableCanvas
from tctoolkitutil.tkcanvastooltip import TkCanvasToolTip

import Tkinter,tkFileDialog
from idlelib.TreeWidget import TreeItem, TreeNode

import csv
import sys, os, string
import xml.etree.ElementTree as ET

CLR_PROP = 'Field 1'
SIZE_PROP = 'Field 0'


class ChildTreeItem(TreeItem):
    def __init__(self, smtreenode, tmcanvas):
        self.node = smtreenode
        self.tmcanvas = tmcanvas
        
    def GetText(self):
        return(self.node.name)
        
    def IsExpandable(self):
        node = self.node
        return len(node) > 0

    def GetSubList(self):        
        items = [ChildTreeItem(child, self.tmcanvas) for child in self.node]
        items = sorted(items, key=lambda child : child.node.name)
        return(items)
    
    def OnDoubleClick(self):
        self.tmcanvas.drawTreemap(self.node)

class TMTree(TreemapNode):
    def __init__(self, filename, **kwargs):
        TreemapNode.__init__(self,filename)
        self.childseperator = kwargs.get('childseperator', '.')
        self.fieldseperator = kwargs.get('fieldseperator', ',')
        self.createFromCSV(filename)
        self.MergeSingleChildNodes(self.childseperator)

    def createFromCSV(self, tmfile):
        '''
        treemap csv file. Last field defines children. remaining fields define various properties.
        '''
        assert(tmfile.endswith(".csv"))
            
        with open(tmfile, "rb") as f:
            reader = csv.reader(f, delimiter=self.fieldseperator,skipinitialspace=True)
            firstrow = reader.next() #ignore first line
            self.maxcolidx = 0
            
            for line in reader:
                colcount = len(line)
                self.maxcolidx = max(self.maxcolidx, colcount-2)
                if( colcount < 3):
                    continue
                fname = line[colcount-1]
                #split the filename into components.
                namelist = fname.split(self.childseperator)
                node = self.addChild(namelist)
                for colidx in range(0, colcount-1):
                    val = int(line[colidx])
                    prop = 'Field %d' % colidx
                    node.setProp(prop, val)
                        
        
class App:
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.title("Source Monitor Treemap")
        self.initMenu()
        self.initDropDown()
        self.pane = Tkinter.PanedWindow(self.root, orient=Tkinter.HORIZONTAL)
        self.pane.pack(fill=Tkinter.BOTH, expand=1)
        self.initTreeCanvas()
        self.initTreemapCanvas()
        self.childtree = None

    def initTreemapCanvas(self):
        self.tmcanvas = TreemapSquarified(self.pane,width='13i', height='8i')
        self.tmcanvas.config(bg='white')
        #self.tmcanvas.grid(column=1,row=1, sticky="nsew")
        self.tmcanvas.pack()
        self.pane.add(self.tmcanvas.frame)
        self.tooltip = TkCanvasToolTip(self.tmcanvas, follow=True)
        
    def initTreeCanvas(self):
        frame = Tkinter.Frame(self.pane)
        self.treecanvas = createScrollableCanvas(frame, width='2i')
        self.treecanvas.pack()
        self.pane.add(frame)

    def initMenu(self):
        menubar = Tkinter.Menu(self.root)
        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openTreemapFile)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def initDropDown(self):
        self.dropdownframe = Tkinter.Frame(self.root)
        self.sizeOption = Tkinter.StringVar()
        self.sizeOption.set(SIZE_PROP)
        self.colorOption = Tkinter.StringVar()
        self.colorOption.set(CLR_PROP)
        #get the list of options        
        options = ['Field 0', 'Field 1']
        
        self.optionsSize = Tkinter.OptionMenu(self.dropdownframe, self.sizeOption,command=self.optionchange, *options)
        self.optionsSize.grid(row=0, column=0)
        self.optionsClr = Tkinter.OptionMenu(self.dropdownframe,self.colorOption,command=self.optionchange, *options)
        self.optionsClr.grid(row=0, column=1)
        self.dropdownframe.pack()

    def optionchange(self, param):
        sizepropname = self.sizeOption.get()
        clrpropname = self.colorOption.get()
        self.createtreemap(sizepropname=sizepropname, clrpropname=clrpropname)
        
    def createtreemap(self, tmrootnode=None,sizepropname=SIZE_PROP, clrpropname=CLR_PROP):
        del self.childtree
        if( tmrootnode != None):
            self.tmrootnode = tmrootnode
        ftreeroot = ChildTreeItem(self.tmrootnode, self.tmcanvas)
        self.childtree = TreeNode(self.treecanvas, None, ftreeroot)
        self.childtree.update()
        self.childtree.expand()
        clrmap = self.getPropClrMap(self.tmrootnode, clrpropname)
        self.tmcanvas.set(tmcolormap=clrmap,sizeprop=sizepropname,clrprop=clrpropname,upper=[1200,700],tooltip=self.tooltip)
        self.tmcanvas.drawTreemap(self.tmrootnode)

    def getNeutralVal(self, clrpropname, minval, maxval):
        #neutralval = 0.5*(minval+maxval)
        neutralval = 15
        return(neutralval)
            
    def getPropClrMap(self,tmrootnode, clrpropname):
        clrmap = TMColorMap(minclr=(0,255,0),maxclr=(255,0,0))        
        minval = tmrootnode.minclr(clrpropname)
        maxval = tmrootnode.maxclr(clrpropname)
        neutralval = self.getNeutralVal(clrpropname, minval, maxval)
        clrmap.setlimits(minval,maxval, neutralval=neutralval)
        return(clrmap)

    def openTreemapFile(self):
        filename = tkFileDialog.askopenfilename(title="Choose Treemap CSV file", defaultextension=".csv")
        tmtree = TMTree(filename)
        self.createtreemap(tmtree)
            
    def run(self):
        self.root.mainloop()
        #Now destroy the top level window. Otherwise it just sits there if you are running this application from inside interpreter like IDLE or PythonWin
        # You may get warning there.
        #self.root.destroy()

def RunMain():
    app = App()
    tmfile = sys.argv[1]
    #tmfile = "E:\\users\\nitinb\\sources\\TCCAT\\test\\ccnet.xml"
    tmroot = TMTree(tmfile)
    app.createtreemap(tmroot)
    app.run()
    
if( __name__ == "__main__"):
    RunMain()