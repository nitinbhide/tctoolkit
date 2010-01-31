'''
Display the Source Monitor data as 'treemap'

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
from optparse import OptionParser
import xml.etree.ElementTree as ET

CLR_PROP = 'MaxComplexity'
SIZE_PROP = 'Lines'

#define the mapping between the Source Monitor column names and Treemap properties.
#This table is required as for same metric, Source Monitor column names are different for different languages.

SMPROP_MAPPING = { "Lines":"Lines",
                   "Maximum Complexity":"MaxComplexity",
                   "Complexity of Most Complex Function":"MaxComplexity",
                   "Statements":"Statements",
                   "Percent Comment Lines":"Percent Comment Lines",
                   "Percent Lines with Comments":"Percent Comment Lines",
                   "Functions":"Functions",
                   "Percent Branch Statements":"Percent Branch Statements",
                   "Percent Documentation Lines":"Percent Documentation Lines",
                   "Classes, Interfaces, Structs":"Classes, Interfaces, Structs",
                   "Classes and Interfaces":"Classes, Interfaces, Structs",
                   "Methods per Class":"Methods per Class",
                   "Calls per Method":"Calls per Method",
                   "Statements per Method":"Statements per Method",
                   "Average Statements per Function":"Statements per Method",
                   "Average Statements per Method":"Statements per Method",
                   "Maximum Block Depth":"Maximum Block Depth",
                   "Average Block Depth":"Average Block Depth",
                   "Average Complexity":"Average Complexity",
    }

SMFILEFORMATS =[
    ('Source Monitor XML','*.xml'),
    ('Source Monitor CSV','*.csv'),
    ]


#color properties configuration. Neural color values for each property.
#if it is defined as none or not there in the table, Then neutral color is just midpoint of min/max values

COLOR_PROP_CONFIG= {
        "MaxComplexity": 15,
        "Maximum Block Depth":5,
        "Statements per Method":25,
        "Percent Branch Statements":30
    }

class FileTreeItem(TreeItem):
    def __init__(self, smtreenode, tmcanvas):
        self.node = smtreenode
        self.tmcanvas = tmcanvas
        
    def GetText(self):
        return(self.node.name)
        
    def IsExpandable(self):
        node = self.node
        return len(node) > 0

    def GetSubList(self):
        items = [FileTreeItem(child, self.tmcanvas) for child in self.node]
        items = sorted(items, key=lambda child : child.node.name)
        return(items)
    
    def OnDoubleClick(self):
        self.tmcanvas.drawTreemap(self.node)

class SMTree(TreemapNode):
    def __init__(self, filename):
        TreemapNode.__init__(self,filename)
        if( filename.endswith('.csv')):
            self.createFromCSV(filename)
        elif( filename.endswith('.xml')):
            self.createFromXML(filename)
        self.MergeSingleChildNodes('/')

    def getColNumPropMap(self, firstrow):
        col2Prop = dict()
        for col in firstrow:
            col = col.strip()
            propname =SMPROP_MAPPING.get(col)
            if(  propname != None):
                col2prop[colid] = propname
            
        return(col2prop)
            
    def createFromCSV(self, smfile):
        '''
        smfile - source monitor csv file
        '''
        assert(smfile.endswith(".csv"))
            
        with open(smfile, "r") as f:
            reader = csv.reader(f)
            firstrow = reader.next() #ignore first line
            col2prop = self.getColNumPropMap(firstrow)
            
            for line in reader:
                fname = line[3]
                #split the filename into components.
                namelist = fname.split(os.sep)
                node = self.addChild(namelist)
                for colidx, prop in col2prop:
                    val = tonum(line[colidx])
                    node.setprop(prop, val)
                
    def getMetricId2PropMap(self, xmtree):
        assert(xmtree != None)
        metricnodes = xmtree.findall('project/metric_names/metric_name')
        metricid2prop = dict()
        
        for metricnode in metricnodes:
            propname = SMPROP_MAPPING.get(metricnode.text)
            if( propname != None):
                metricid = metricnode.attrib.get('id')
                metricid2prop[metricid] = propname
                
        return(metricid2prop)
            
    def createFromXML(self, smfile):
        assert(smfile.endswith('.xml'))
        print "extracting xml ",smfile
        xmtree = ET.parse(smfile)
        metricid2prop = self.getMetricId2PropMap(xmtree)
        
        filenodes = xmtree.findall("project/checkpoints/checkpoint/files/file")
        for fnode in filenodes:
            fname = fnode.attrib.get("file_name")
            namelist = fname.split(os.sep)
            tmnode = self.addChild(namelist)

            for metricnode in fnode.findall('metrics/metric'):
                metricid = metricnode.attrib.get('id')
                propname = metricid2prop.get(metricid)
                if( propname != None):
                    tmnode.setProp(propname, tonum(metricnode.text))
        
            
def tonum(str):
    str = str.replace(',','')
    num = 0.0
    if( str.endswith('+')):
        str = str[0:-1]
        num = 1.0
    num = num+float(str)
    return(num)

        
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
        self.filetree = None

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
        filemenu.add_command(label="Open", command=self.openSMFile)
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
        options = set(SMPROP_MAPPING.itervalues())
        #now convert the set to sorted list
        options = sorted(options)
        
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
        del self.filetree
        if( tmrootnode != None):
            self.tmrootnode = tmrootnode
        ftreeroot = FileTreeItem(self.tmrootnode, self.tmcanvas)
        self.filetree = TreeNode(self.treecanvas, None, ftreeroot)
        self.filetree.update()
        self.filetree.expand()
        clrmap = self.getPropClrMap(self.tmrootnode, clrpropname)
        self.tmcanvas.set(tmcolormap=clrmap,sizeprop=sizepropname,clrprop=clrpropname,upper=[1200,700],tooltip=self.tooltip)
        self.tmcanvas.drawTreemap(self.tmrootnode)

    def getNeutralVal(self, clrpropname, minval, maxval):
        neutralval = COLOR_PROP_CONFIG.get(clrpropname)
        
        if(  neutralval== None):
            neutralval = 0.5*(minval+maxval)
        return(neutralval)
            
    def getPropClrMap(self,tmrootnode, clrpropname):
        clrmap = TMColorMap(minclr=(0,255,0),maxclr=(255,0,0))        
        minval = tmrootnode.minclr(clrpropname)
        maxval = tmrootnode.maxclr(clrpropname)
        neutralval = self.getNeutralVal(clrpropname, minval, maxval)
        clrmap.setlimits(minval,maxval, neutralval=neutralval)
        return(clrmap)

    def openSMFile(self):
        filename = tkFileDialog.askopenfilename(title="Choose Source Monitor output file", filetypes=SMFILEFORMATS,defaultextension=".xml")
        smtree = SMTree(filename)
        self.createtreemap(smtree)
            
    def run(self):
        self.root.mainloop()
        #Now destroy the top level window. Otherwise it just sits there if you are running this application from inside interpreter like IDLE or PythonWin
        # You may get warning there.
        #self.root.destroy()

def RunMain():
    usage = "usage: %prog [options] <source monitor xml or csv filename>"
    parser = OptionParser(usage)

    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        print "Invalid number of arguments. Use smtreemap.py --help to see the details."
    else:            
        app = App()
        smfile = args[0]
        #smfile = "E:\\users\\nitinb\\sources\\TCCAT\\test\\ccnet.xml"
        tmroot = SMTree(smfile)
        app.createtreemap(tmroot)
        app.run()
    
if( __name__ == "__main__"):
    RunMain()