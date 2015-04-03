'''
tktreemap.py
Utility to display a treemap using Tkiter.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''

import Tkinter
from itertools import imap
from treemapdata import TreemapNode, DEFAULT_COLOR_PROP, DEFAULT_SIZE_PROP

DEFAULT_MINCLR = (255, 0, 0)  # Red
DEFAULT_MAXCLR = (0, 255, 0)  # green
DEFAULT_NEUTRALCLR = (255, 255, 255)  # white
COLORDIFF_TOL = 0.001


def getwidth(lower, upper, axis):
    wid = upper[axis] - lower[axis]
    return(wid)


def getPreferedAxis(lower, upper):
    wid0 = getwidth(lower, upper, 0)
    wid1 = getwidth(lower, upper, 1)
    preferedaxis = 1
    if(wid0 > wid1):
        preferedaxis = 0
    return(preferedaxis)


def initScrollableCanvas(frame, canvas):
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    canvas.config(bg='white')
    # Create a scrollable canvas
    scrollX = Tkinter.Scrollbar(frame, orient=Tkinter.HORIZONTAL)
    scrollY = Tkinter.Scrollbar(frame, orient=Tkinter.VERTICAL)
    # now tie the three together. This is standard boilerplate text
    canvas['xscrollcommand'] = scrollX.set
    canvas['yscrollcommand'] = scrollY.set
    scrollX['command'] = canvas.xview
    scrollY['command'] = canvas.yview
    scrollX.grid(row=1, column=0, sticky=Tkinter.E + Tkinter.W)
    scrollY.grid(row=0, column=1, sticky=Tkinter.N + Tkinter.S)
    canvas.grid(
        row=0, column=0, sticky=Tkinter.N + Tkinter.S + Tkinter.E + Tkinter.W)
    # fill and expand if required.
    frame.pack(fill=Tkinter.BOTH, expand=True)


def createScrollableCanvas(parent, **kwargs):
    frame = Tkinter.Frame(parent)
    canvas = Tkinter.Canvas(frame, kwargs)
    initScrollableCanvas(frame, canvas)
    return(canvas)


class TMColorMap:

    def __init__(self, minclr=DEFAULT_MINCLR, maxclr=DEFAULT_MAXCLR, neutralclr=DEFAULT_NEUTRALCLR):
        self.minclr = minclr
        self.maxclr = maxclr
        self.neutralclr = neutralclr
        self.minclrval = -1.0
        self.maxclrval = 1.0
        self.neurtralclrval = 0.0

    def setclrs(self, **kwargs):
        minclr = kwargs.get('minclr', minclr)
        maxclr = kwargs.get('maxclr', maxclr)
        neutralclr = kwargs.get('neutralclr', neutralclr)

    def setlimits(self, minclrval, maxclrval, neutralval=None):
        self.minclrval = float(minclrval)
        self.maxclrval = float(maxclrval)
        if((self.maxclrval - self.minclrval) <= COLORDIFF_TOL):
            self.maxclrval = self.minclrval + COLORDIFF_TOL

        if(neutralval == None):
            neutralval = (self.minclrval + self.maxclrval) / 2.0

        self.neutralclrval = float(neutralval)
        # if neutral value is greater than max clr value, it will screw up the color computations
        # hence reset it if required.
        self.neutralclrval = min(self.neutralclrval, self.maxclrval)

        assert(
            self.minclrval <= self.neutralclrval and self.neutralclrval <= self.maxclrval)

    def mapclr(self, val):
        rgb = self.neutralclr
        if(val != None):
            # if check the val is in which interval (minclr, neutral) or
            # (neutral,maxclrval)
            val = float(val)
            val = min(val, self.maxclrval)
            val = max(val, self.minclrval)

            # Now get the value is fraction between the limits.
            try:
                if(val >= self.minclrval and val <= self.neutralclrval):
                    val = (val - self.minclrval) / \
                        (self.neutralclrval - self.minclrval)
                    minclr = self.minclr
                    maxclr = self.neutralclr
                else:
                    val = (val - self.neutralclrval) / \
                        (self.maxclrval - self.neutralclrval)
                    minclr = self.neutralclr
                    maxclr = self.maxclr
            except:
                # if you get any error set the color value to neutral color
                # minclrval and maxclrval are both 0 then set val to neural
                # color.
                minclr = self.minclr
                maxclr = self.maxclr
                val = neutralclr
            # now map the fraction to color.
            r = minclr[0] + val * (maxclr[0] - minclr[0])
            r = int(r + 0.5)
            g = minclr[1] + val * (maxclr[1] - minclr[1])
            g = int(g + 0.5)
            b = minclr[2] + val * (maxclr[2] - minclr[2])
            b = int(b + 0.5)
            rgb = (r, g, b)
        return(rgb)

    def mapclrstr(self, val):
        r, g, b = self.mapclr(val)
        rgbstr = "#%02X%02X%02X" % (r, g, b)
        return(rgbstr)


class TreemapCanvas(Tkinter.Canvas):

    def __init__(self, root, kwargs):
        # Set the default variable values for Treemaps
        self.tmroot = None
        self.nodemap = dict()
        # set the default values
        self.__setdefault(kwargs, 'tmmargin', 3)
        self.__setdefault(kwargs, 'titleheight', 12)
        self.__setdefault(kwargs, 'titlewidth', 50)
        self.__setdefault(kwargs, 'tmcolormap', TMColorMap())
        self.__setdefault(kwargs, 'lower', [0, 0])
        self.__setdefault(kwargs, 'upper', [600, 400])
        self.__setdefault(kwargs, 'sizeprop', DEFAULT_SIZE_PROP)
        self.__setdefault(kwargs, 'clrprop', DEFAULT_COLOR_PROP)
        self.__setdefault(kwargs, 'tooltip', None)
        self.__setdefault(kwargs, 'leafnodecb', None)
        # call the base class method to create the actual canvas
        self.__createCanvas(root, kwargs)

    def __setdefault(self, kwargs, var, defvalue):
        self.__dict__[var] = kwargs.get(var, defvalue)
        if(var in kwargs):
            del kwargs[var]

    def __createCanvas(self, root, kwargs):
        self.frame = Tkinter.Frame(root)
        Tkinter.Canvas.__init__(self, self.frame, kwargs)
        initScrollableCanvas(self.frame, self)

    def set(self, **kwargs):
        for key, value in kwargs.iteritems():
            assert(key in self.__dict__)
            self.__dict__[key] = value

    def drawTreemap(self, tmroot):
        self.delete(Tkinter.ALL)
        self.tmroot = tmroot
        axis = 0
        self['scrollregion'] = (
            self.lower[0], self.lower[0], self.upper[0], self.upper[1])
        self.createNode(self.tmroot, self.lower, self.upper, axis)
        if(self.tooltip != None):
            self.tooltip.updatebindings()

    def addMargins(self, lower, upper):
        """add margins to a node and return the locations of where to 
        draw children"""
        lower_with_margin = [0, 0]
        upper_with_margin = [0, 0]

        for dim in [0, 1]:
            lower_with_margin[dim] = lower[dim] + self.tmmargin
            upper_with_margin[dim] = upper[dim] - self.tmmargin
        # Add the space for title
        lower_with_margin, upper_with_margin = self.addTitleHeight(
            lower_with_margin, upper_with_margin)

        return (lower_with_margin, upper_with_margin)

    def addTitleHeight(self, lower, upper):
        # copy the lists to avoid modifying the original ones
        lower = list(lower)
        upper = list(upper)
        if(self.canDrawTitle(lower, upper)):
            lower[1] = lower[1] + self.titleheight
        return(lower, upper)

    def canDrawTitle(self, lower, upper):
        return((upper[1] - lower[1]) > self.titleheight and (upper[0] - lower[0]) > self.titlewidth)

    def drawTitle(self, node, lower, upper):
        if(self.canDrawTitle(lower, upper)):
            # draw title horizontally centered in the rectangle and attached to
            # top
            x = int((lower[0] + upper[0]) / 2)
            y = lower[1]
            maxwid = upper[0] - lower[0]
            objid = self.create_text(
                x, y, text=node.name, anchor='n', width=maxwid)
            self.addTooltipTag(objid, node)

    def getTooltipText(self, node):
        sizeval = node.getSize(self.sizeprop)
        tiptext = "%s\n%s : %.2f" % (node.name, self.sizeprop, sizeval)
        clrval = node.getClr(self.clrprop)
        if(clrval != None):
            tiptext = tiptext + "\n%s : %.2f" % (self.clrprop, clrval)
        return(tiptext)

    def addTooltipTag(self, objid, node):
        tiptext = self.getTooltipText(node)
        tiptag = "tooltip:" + tiptext
        self.addtag_withtag(tiptag, objid)


class TreemapSD(TreemapCanvas):

    def __init__(self, root, **kwargs):
        TreemapCanvas.__init__(self, root, kwargs)

    def createNode(self, node, lower=[0.0, 0.0], upper=[500.0, 500.0], axis=0):
        self.createNodeSliceDice(node, lower, upper, axis)

    def createNodeSliceDice(self, node, lower=[0.0, 0.0], upper=[500.0, 500.0], axis=0):
        """add a node of the tree to the treemap"""
        # Copy lists to avoid modifying the original lists
        lower = list(lower)
        upper = list(upper)
        axis = axis % 2
        clr = self.tmcolormap.mapclrstr(node.getClr(self.clrprop))
        id = self.create_rectangle(
            lower[0], lower[1], upper[0], upper[1], fill=clr)
        # add tooltip
        self.addTooltipTag(id, node)
        self.drawTitle(node, lower, upper)

        (lm, um) = self.addMargins(lower, upper)
        width = um[axis] - lm[axis]
        try:
            nodesize = float(node.getSize(self.sizeprop))
            for child in node.getValidChildren(self.sizeprop, self.clrprop):
                um[axis] = lm[axis] + (width * float(child.getSize(self.sizeprop))
                                       / nodesize)

                self.createNodeSliceDice(child, list(lm), list(um), axis + 1)
                lm[axis] = um[axis]
            if(self.leafnodecb != None and len(node) == 0):
                self.leafnodecb(node, self, id)

        except TypeError:
            pass


class TreemapSquarified(TreemapCanvas):

    def __init__(self, root, **kwargs):
        TreemapCanvas.__init__(self, root, kwargs)

    def createNode(self, node, lower, upper, axis):
        '''create the root node'''
        self.createNodeSquarified(node, lower, upper)

    def createNodeSquarified(self, node, lower, upper):
        assert(node != None)
        clr = self.tmcolormap.mapclrstr(node.getClr(self.clrprop))
        id = self.create_rectangle(
            lower[0], lower[1], upper[0], upper[1], fill=clr)
        # add tooltip
        self.addTooltipTag(id, node)
        # draw title
        self.drawTitle(node, lower, upper)

        nodelist = list(node.getValidChildren(self.sizeprop, self.clrprop))
        if(len(nodelist) > 0):
            # BUGBUG : if there is a size given to node. It will be missed.
            (lm, um) = self.addMargins(lower, upper)
            # now sort the nodelist in the reverse order of sizes
            nodelist = sorted(
                nodelist, key=lambda node: node.getSize(self.sizeprop), reverse=True)
            self.createNodelistSquarified(nodelist, lm, um)
        elif(self.leafnodecb != None):
            assert(len(nodelist) == 0)
            self.leafnodecb(node, self, id, lower, upper)

    def createNodelistSquarified(self, nodelist, lower, upper, axis=0):
        # Copy the lists to avoid modifying the passed values
        lower = list(lower)
        upper = list(upper)
        axis = getPreferedAxis(lower, upper)
        otheraxis = (axis + 1) % 2
        width = getwidth(lower, upper, axis)
        ht = getwidth(lower, upper, otheraxis)

        if(width > 0.0 and ht > 0.0):
            sqrowsizes = []
            rowchildlist = []
            worstratio = 50000
            nodesize = sum(
                imap(lambda node: node.getSize(self.sizeprop), nodelist))
            if(nodesize > 0.0):
                rowsize = 0.0
                idx = 0
                rowwid = 0.0
                for child in nodelist:
                    childsize = float(child.getSize(self.sizeprop))
                    #assert(childsize > 0.0)
                    sqrowsizes.append(childsize)
                    rowsize = rowsize + childsize
                    wid1 = width * rowsize / nodesize
                    aspectratio = self.worstratio(sqrowsizes, ht, wid1)
                    if (worstratio > aspectratio):
                        rowchildlist.append(child)
                        rowwid = wid1
                        worstratio = aspectratio
                        assert(len(sqrowsizes) == len(rowchildlist))
                    else:
                        # best aspect ratio found. Now layout the row.
                        break
                if(len(rowchildlist) > 0):
                    # Make sure that lists are copied.
                    rowlower = list(lower)
                    rowupper = list(upper)
                    rowupper[axis] = rowlower[axis] + rowwid
                    self.drawrow(rowchildlist, rowlower, rowupper, axis)
                # update the rectangle size
                lower[axis] = lower[axis] + rowwid
                # calculate the new
                nodelist = nodelist[len(rowchildlist):]
                if(len(nodelist) > 0):
                    self.createNodelistSquarified(nodelist, lower, upper)

    def drawrow(self, nodelist, lower, upper, axis):
        assert(axis == 0 or axis == 1)
        # Copy the lists to avoid modifying the passed values
        lower = list(lower)
        upper = list(upper)
        otheraxis = (axis + 1) % 2
        width = getwidth(lower, upper, axis)
        ht = getwidth(lower, upper, otheraxis)
        nodesize = sum(
            imap(lambda node: node.getSize(self.sizeprop), nodelist))
        assert(nodesize > 0.0)
        assert(ht > 0.0)
        for child in nodelist:
            upper[otheraxis] = lower[otheraxis] + \
                (ht * child.getSize(self.sizeprop) / nodesize)
            self.createNodeSquarified(child, lower, upper)
            lower[otheraxis] = upper[otheraxis]

    def worstratio(self, sqrowsizes, ht, rowwid):
        assert(ht > 0.0)
        assert(rowwid > 0.0)
        rowsize = sum(sqrowsizes)
        worstaspect = 0.0
        if rowsize == 0 or rowwid == 0:
            return 0.0
        for rectsize in sqrowsizes:
            rectht = ht * (rectsize / rowsize)
            if rectht == 0.0:
                return 0.0
            aspect = max(rowwid / rectht, rectht / rowwid)
            if(worstaspect < aspect):
                worstaspect = aspect
        return(worstaspect)

'''
Example Code on how ot use the TkTreemap
'''


class App:

    def __init__(self):
        self.root = Tkinter.Tk()
        self.tmcanvas = TreemapSquarified(self.root, width='8i', height='6i')
        self.tmcanvas.config(bg='white')
        self.tmcanvas.pack()

    def createtreemap(self, tmnode, tmcolormap=None):
        self.tmcanvas.set(tmcolormap=tmcolormap)
        self.tmcanvas.drawTreemap(tmnode)

    def run(self):
        self.root.mainloop()


def RunMain():
    app = App()
    tmroot = TreemapNode("root")
    node1 = tmroot.addChildNameValue("node1", 6, 5)
    #node11 = node1.addChildNameValue("node11", 10, 10)
    #node12 = node1.addChildNameValue("node12", 5, 100)
    tmroot.addChildNameValue("node2", 6, -5)
    tmroot.addChildNameValue("node3", 4, -10)
    tmroot.addChildNameValue("node4", 3, 50)
    tmroot.addChildNameValue("node5", 2, 50)
    tmroot.addChildNameValue("node6", 2, 50)
    tmroot.addChildNameValue("node7", 1, 50)
    tmroot.addChildNameValue("node7", 0, 50)

    clrmap = TMColorMap()
    minval = tmroot.minclr()
    maxval = tmroot.maxclr()
    clrmap.setlimits(minval, maxval)

    app.createtreemap(tmroot, tmcolormap=clrmap)
    app.run()

if(__name__ == "__main__"):
    RunMain()
