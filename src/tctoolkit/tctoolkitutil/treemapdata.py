'''
class to store the treemap data as hierarchy of nodes

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''

from itertools import imap

_NODEID = 0

DEFAULT_COLOR_PROP = 'color'
DEFAULT_SIZE_PROP = 'size'

class TreemapNode(object):
    def __init__(self, name,accumulateSizes=True):
        self.children = dict()
        self.name = name
        global _NODEID
        self.id = _NODEID
        _NODEID = _NODEID+1
        self.properties = dict()
        self.accumulateSizes = accumulateSizes

    def __iter__(self):
        return(self.children.itervalues())

    def __len__(self):
        return(len(self.children))

    def __str__(self):
        return(self.name)
        
    def getValidChildren(self, sizeprop, clrprop):
        '''
        return a list of children with non zero size value and
        where getClr() return a valid floating point value.
        '''
        for child in self.children.itervalues():            
            if child.isValidNode(sizeprop, clrprop):
                yield child
        
    def isValidNode(self, sizeprop, clrprop):
        '''
        check if this node is valid for given size property and color property
        i.e. it can be displayed.
        A valid node is
         (a) must have size > 0
         (b) must have color that is not None.
         (c) However, a node which has children will not have a color assigned (i.e.
              getClr will return None)
        '''
        return self.getSize(sizeprop) > 0 \
            and (len(self.children) > 0 or self.getClr(clrprop) != None)
            
    def addChildNode(self, node):
        assert(self.children.has_key(node.name) == False)
        assert(isinstance(node, TreemapNode)==True)
        self.children[node.name] = node
        return(node)

    def addChildName(self, name):
        if(self.children.has_key(name) == False):
            node = TreemapNode(name)
            self.children[name] = node
                
        return(self.children[name])

    def addChildNameValue(self, name, size, clr):
        node = self.addChildName(name)
        node.setProp('size', size)
        node.setProp('color', clr)
        return(node)
        
    def addChild(self, nodeNameList):
        parent = self
        curchild = None
        for nodename in nodeNameList[0:-1]:
            if( parent.children.has_key(nodename) == False):
                parent.addChildName(nodename)
            parent = parent.children[nodename]
        childnode = parent.addChildName(nodeNameList[-1])
        return(childnode)

    def getNode(self, nodeNameList):
        node = self
        for nodename in nodeNameList:
            if( node.children.has_key(nodename) == True):
                node = node.children[nodename]                                
            else:
                node = None
                break                
            
        return(node)    

    def MergeSingleChildNodes(self, seperator='/'):
        for child in self.children.itervalues():
            child.MergeSingleChildNodes(seperator)
            
        if( len(self.children) == 1 and len(self.properties)==0):
            child = self.children.values()[0]
            self.name = self.name + seperator + child.name
            self.properties = child.properties
            self.children = child.children
        
    def setProp(self, key, val):
        self.properties[key] = val

    def getProp(self, key):
        return(self.properties.get(key, None))
    
    def getClr(self, key=DEFAULT_COLOR_PROP):
        clr = self.properties.get(key, None)
        if( clr != None):
            clr = float(clr)
        return(clr)

    def mysize(self, key=DEFAULT_SIZE_PROP):
        size = float(self.properties.get(key, 0.0))
        return(size)
        
    def getSize(self, key=DEFAULT_SIZE_PROP):
        cmbsize = float(self.properties.get(key, 0.0))
        #add it as sum of properties of its children
        if( self.accumulateSizes == True):
            cmbsize = reduce(lambda totalsize,node : totalsize + node.getSize(key), self.children.itervalues(), cmbsize)
        
        return(cmbsize)

    def minclr(self, clrprop=DEFAULT_COLOR_PROP):
        minclr = self.getClr(clrprop)
        if( self.children != None and len(self.children) > 0):
            minclr = min(imap(lambda child:child.minclr(clrprop), self.children.itervalues()))
                    
        assert( (self.children != None and len(self.children) > 0) or minclr != None)
        return(minclr)
    
    def maxclr(self, clrprop=DEFAULT_COLOR_PROP):
        maxclr = self.getClr(clrprop)
        if( self.children != None and len(self.children) > 0):
            maxclr = max(imap(lambda child:child.maxclr(clrprop), self.children.itervalues()))
        assert( (self.children != None and len(self.children) > 0) or maxclr != None)
        return(maxclr)
    
    def writejson(self,outfile, sizekey=DEFAULT_SIZE_PROP, clrkey=None):
        #outfile.write('alert("hello json")\n')
        outfile.write("var jsondata =\n")
        self.writejsonnode(outfile, sizekey,clrkey)
        outfile.write(";\n")        

    def writejsonnodechildren(self, outfile,sizekey, clrkey=None):
        isfirst = True
        for node in self.children.values():
            if( isfirst == False):
                outfile.write(',\n')
            node.writejsonnode(outfile, sizekey,clrkey)
            isfirst = False            
        
    def writejsonnode(self, outfile,sizekey, clrkey=None):        
        outfile.write('{\t"id": "%s","name": "%s","data": %s,\n' %
                      (self.id, self.name, self.jsondata(sizekey, clrkey)))
        outfile.write('"children":[')
        self.writejsonnodechildren(outfile,sizekey, clrkey)
        outfile.write(']}\n')
        
    def jsondata(self, sizekey, clrkey=None):
        jsondata = "["
        jsondata = jsondata + '{"key": "%s", "value": "%f"}' % (sizekey, self.getSize(sizekey))
        if( clrkey != None):
            jsondata = jsondata + ',{"key": "%s", "value": "%f"}' % (clrkey, self.getClr(clrkey))
        jsondata = jsondata + "]"
        return(jsondata)
    