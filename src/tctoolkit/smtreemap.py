'''
Display the Source Monitor data as 'treemap'

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''

from __future__ import with_statement

import sys
import os
import string
from optparse import OptionParser
import tkinter
from idlelib.tree import TreeItem, TreeNode

from .tctoolkitutil.tktreemap import TreemapSquarified, TMColorMap, createScrollableCanvas
from .tctoolkitutil.tkcanvastooltip import TkCanvasToolTip
from sourcemon import *

SMFILEFORMATS = [
    ('Source Monitor XML', '*.xml'),
    ('Source Monitor CSV', '*.csv'),
]


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
        items = sorted(items, key=lambda child: child.node.name)
        return(items)

    def OnDoubleClick(self):
        self.tmcanvas.drawTreemap(self.node)


class App(object):

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Source Monitor Treemap")
        self.initMenu()
        self.initDropDown()
        self.pane = tkinter.PanedWindow(self.root, orient=tkinter.HORIZONTAL)
        self.pane.pack(fill=tkinter.BOTH, expand=1)
        self.initTreeCanvas()
        self.initTreemapCanvas()
        self.filetree = None

    def initTreemapCanvas(self):
        self.tmcanvas = TreemapSquarified(self.pane, width='13i', height='8i')
        self.tmcanvas.config(bg='white')
        self.pane.config(bg='blue')
        self.pane.add(self.tmcanvas.frame)
        self.pane.paneconfigure(
            self.tmcanvas.frame, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)
        self.tooltip = TkCanvasToolTip(self.tmcanvas, follow=True)

    def initTreeCanvas(self):
        frame = tkinter.Frame(self.pane)
        self.treecanvas = createScrollableCanvas(frame, width='2i')
        self.pane.add(frame)
        self.pane.paneconfigure(
            frame, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)

    def initMenu(self):
        menubar = tkinter.Menu(self.root)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openSMFile)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def initDropDown(self):
        self.dropdownframe = tkinter.Frame(self.root)
        self.sizeOption = tkinter.StringVar()
        self.sizeOption.set(SIZE_PROP)
        self.colorOption = tkinter.StringVar()
        self.colorOption.set(CLR_PROP)
        # get the list of options
        options = set(SMPROP_MAPPING.itervalues())
        # now convert the set to sorted list
        options = sorted(options)

        self.optionsSize = tkinter.OptionMenu(
            self.dropdownframe, self.sizeOption, command=self.optionchange, *options)
        self.optionsSize.grid(row=0, column=0)
        self.optionsClr = tkinter.OptionMenu(
            self.dropdownframe, self.colorOption, command=self.optionchange, *options)
        self.optionsClr.grid(row=0, column=1)
        self.dropdownframe.pack()

    def optionchange(self, param):
        sizepropname = self.sizeOption.get()
        clrpropname = self.colorOption.get()
        self.createtreemap(sizepropname=sizepropname, clrpropname=clrpropname)

    def createtreemap(self, tmrootnode=None, sizepropname=SIZE_PROP, clrpropname=CLR_PROP):
        del self.filetree
        if(tmrootnode != None):
            self.tmrootnode = tmrootnode
        ftreeroot = FileTreeItem(self.tmrootnode, self.tmcanvas)
        self.filetree = TreeNode(self.treecanvas, None, ftreeroot)
        self.filetree.update()
        self.filetree.expand()
        clrmap = self.getPropClrMap(self.tmrootnode, clrpropname)
        self.tmcanvas.set(tmcolormap=clrmap, sizeprop=sizepropname,
                          clrprop=clrpropname, upper=[1200, 700], tooltip=self.tooltip)
        self.tmcanvas.drawTreemap(self.tmrootnode)

    def getNeutralVal(self, clrpropname, minval, maxval):
        neutralval = COLOR_PROP_CONFIG.get(clrpropname)

        if(neutralval == None):
            neutralval = 0.5 * (minval + maxval)
        return(neutralval)

    def getPropClrMap(self, tmrootnode, clrpropname):
        clrmap = TMColorMap(minclr=(0, 255, 0), maxclr=(255, 0, 0))
        minval = tmrootnode.minclr(clrpropname)
        maxval = tmrootnode.maxclr(clrpropname)
        neutralval = self.getNeutralVal(clrpropname, minval, maxval)
        clrmap.setlimits(minval, maxval, neutralval=neutralval)
        return(clrmap)

    def openSMFile(self):
        filename = tkinter.filedialog.askopenfilename(
            title="Choose Source Monitor output file", filetypes=SMFILEFORMATS, defaultextension=".xml")
        smtree = SMTree(filename)
        self.createtreemap(smtree)

    def run(self):
        self.root.mainloop()
        # Now destroy the top level window. Otherwise it just sits there if you are running this application from inside interpreter like IDLE or PythonWin
        # You may get warning there.
        # self.root.destroy()


def RunMain():
    usage = "usage: %prog [options] <source monitor xml or csv filename>"
    description = '''SourceMonitor treemap display.
    (C) Nitin Bhide nitinbhide@thinkingcraftsman.in
    '''
    parser = OptionParser(usage, description=description)

    (options, args) = parser.parse_args()

    if(len(args) < 1):
        print("Invalid number of arguments. Use smtreemap.py --help to see the details.")
    else:
        app = App()
        smfile = args[0]
        tmroot = SMTree(smfile)
        app.createtreemap(tmroot)
        app.run()

if(__name__ == "__main__"):
    RunMain()
