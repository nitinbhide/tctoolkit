'''
sourcemon/__init__.py

Contains file parsers and utility functions to parse and convert the source monitor XML and CSV files

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''
import logging
import csv
import sys
import os
import string
import xml.etree.ElementTree as ET
from tctoolkitutil.treemapdata import TreemapNode


def tonum(str):
    str = str.replace(',', '')
    num = 0.0
    if(str.endswith('+')):
        str = str[0:-1]
        num = 1.0
    num = num + float(str)
    return(num)


# define the mapping between the Source Monitor column names and Treemap properties.
# This table is required as for same metric, Source Monitor column names
# are different for different languages.

CLR_PROP = 'MaxComplexity'
SIZE_PROP = 'Lines'

SMPROP_MAPPING = {"Lines": "Lines",
                  "Maximum Complexity": "MaxComplexity",
                  "Complexity of Most Complex Function": "MaxComplexity",
                  "Statements": "Statements",
                  "Percent Comment Lines": "Percent Comment Lines",
                  "Percent Lines with Comments": "Percent Comment Lines",
                  "Functions": "Functions",
                  "Percent Branch Statements": "Percent Branch Statements",
                  "Percent Documentation Lines": "Percent Documentation Lines",
                  "Classes, Interfaces, Structs": "Classes, Interfaces, Structs",
                  "Classes and Interfaces": "Classes, Interfaces, Structs",
                  "Methods per Class": "Methods per Class",
                  "Calls per Method": "Calls per Method",
                  "Statements per Method": "Statements per Method",
                  "Average Statements per Function": "Statements per Method",
                  "Average Statements per Method": "Statements per Method",
                  "Maximum Block Depth": "Maximum Block Depth",
                  "Average Block Depth": "Average Block Depth",
                  "Average Complexity": "Average Complexity",
                  }


# color properties configuration. Neural color values for each property.
# if it is defined as none or not there in the table, Then neutral color
# is just midpoint of min/max values

COLOR_PROP_CONFIG = {
    "MaxComplexity": 15,
    "Maximum Block Depth": 5,
    "Statements per Method": 25,
    "Percent Branch Statements": 30
}


class SMTree(TreemapNode):

    '''
    extract the data from SourceMonitor XML or CSV file and convert it into
    hierarchical tree data structure
    '''

    def __init__(self, filename):
        super(SMTree, self).__init__(filename)
        if(filename.endswith('.csv')):
            self.createFromCSV(filename)
        elif(filename.endswith('.xml')):
            self.createFromXML(filename)
        self.MergeSingleChildNodes('/')

    def getColNumPropMap(self, firstrow):
        col2Prop = dict()
        for col in firstrow:
            col = col.strip()
            propname = SMPROP_MAPPING.get(col)
            if(propname != None):
                col2prop[colid] = propname

        return(col2prop)

    def getMetricId2PropMap(self, xmtree):
        assert(xmtree != None)
        metricnodes = xmtree.findall('project/metric_names/metric_name')
        metricid2prop = dict()

        for metricnode in metricnodes:
            propname = SMPROP_MAPPING.get(metricnode.text)
            if(propname != None):
                metricid = metricnode.attrib.get('id')
                metricid2prop[metricid] = propname

        return(metricid2prop)

    def createFromCSV(self, smfile):
        '''
        smfile - source monitor csv file
        '''
        assert(smfile.endswith(".csv"))

        with open(smfile, "r") as f:
            reader = csv.reader(f)
            firstrow = reader.next()  # ignore first line
            col2prop = self.getColNumPropMap(firstrow)

            for line in reader:
                fname = line[3]
                # split the filename into components.
                namelist = fname.split(os.sep)
                node = self.addChild(namelist)
                for colidx, prop in col2prop:
                    val = tonum(line[colidx])
                    node.setprop(prop, val)

    def createFromXML(self, smfile):
        assert(smfile.endswith('.xml'))
        logging.debug("extracting xml %s" % smfile)
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
                if(propname != None):
                    tmnode.setProp(propname, tonum(metricnode.text))
