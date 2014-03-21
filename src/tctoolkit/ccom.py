'''
Class Co Ocurrence Matrix (CCOM)

Create a coocurrance matrix based on which class names a occurring in a file. The class names that occur in
one file are treated as 'co ocurring' classes.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''

import string
import sys
import itertools
import fnmatch

from optparse import OptionParser

from pygments.token import Token

from thirdparty.templet import stringfunction

from tctoolkitutil import readJsText,getJsDirPath
from tctoolkitutil import SourceCodeTokenizer
from tctoolkitutil import GetDirFileList,FileOrStdout

@stringfunction
def OutputCCOM(tagcld, d3js_text, d3cloud_text):
    '''<!DOCTYPE html>
    <html>        
    <head>
    <meta charset="utf-8">
    <script>
        // Embedd the text of d3.js
        $d3js_text
    </script>
    <script>
        // Embedd the text of d3.layout.cloudjs
        $d3cloud_text
    </script>
    <style type="text/css">    
    .tagcloud { display:inline-block;}
    .colorscale { display:inline-block;vertical-align:top;}
    </style>
    </head>
    <body>
    <div>
        <h2 align="center">Language Keyword Tag Cloud</h2>
        <div>
            <div class="colorscale"></div>
            <div id="keyword" class="tagcloud"></div>        
        </div>
    </div>
    <hr/>
    <div>
        <h2 align="center">Names (classname, variable names) Tag Cloud</h2>
        <div>
            <div class="colorscale"></div>
            <div id="names" class="tagcloud"></div>
        </div>
    </div>
    <hr/>
    <div>
        <h2 align="center">Class Name/Function Name Tag Cloud</h2>
        <div>
            <div class="colorscale"></div>
            <div id="classnames" class="tagcloud"></div>
        </div>
    </div>
    <hr/>
    <div id="colorscale">
    </div>    
    <script>
        var minColor = 0, maxColor=0;
        // color scale is reversed ColorBrewer RdYlBu
        var colors =  ["#a50026", "#d73027","#f46d43","#fdae61","#fee090","#ffffbf",
                        "#e0f3f8","#abd9e9","#74add1","#4575b4","#313695"];
        console.log(colors);
        colors.reverse();
        var fill =  d3.scale.linear();
        fill.range(colors);
        
        function drawTagCloud(wordsAndFreq, selector, width, height)
        {
            //console.log("selector is " + selector);
            // Font size is calculated based on word frequency
            var minFreq = d3.min(wordsAndFreq, function(d) { return d.size});
            var maxFreq = d3.max(wordsAndFreq, function(d) { return d.size});
            
            var fontSize = d3.scale.log();
            fontSize.domain([minFreq, maxFreq]);
            fontSize.range([10,100])
            // color is calculated based on how many files the word is found
            minColor = d3.min(wordsAndFreq, function(d) { return d.color});
            maxColor = d3.max(wordsAndFreq, function(d) { return d.color});
            var step = (Math.log(maxColor+1)-Math.log(minColor))/colors.length;            
            fill.domain(d3.range(Math.log(minColor), Math.log(maxColor+1), step));
          
            d3.layout.cloud().size([width, height])
                .words(wordsAndFreq)
                .padding(5)            
                .font("Impact")
                .rotate(function() { return 0})
                .fontSize(function(d) { return fontSize(+d.size); })
                .on("end", draw)
                .start();
          
            function draw(words) {
               // console.log("calling draw");
              d3.select('body').select(selector).append("svg")
                  .attr("width", width)
                  .attr("height", height)
                .append("g")
                  .attr("transform", "translate("+width/2+","+height/2+")")
                .selectAll("text")
                  .data(words)
                .enter().append("text")
                  .style("font-size", function(d) { return d.size + "px"; })
                  .style("font-family", "Impact")
                  .style("fill", function(d, i) {
                    return fill(Math.log(d.color)); })
                  .attr("text-anchor", "middle")
                  .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                   })
                  .text(function(d) { return d.text;});
            }
        }
        
        function drawColorScale(clrscaleDivs, fill)
        {            
            var clrScale = clrscaleDivs.append('div').append('ul').style("list-style-type","none").style("margin",0).style("padding",0)
            clrScale = clrScale.selectAll();
            var range = fill.range().slice(0); // deep copy returned array
            range.reverse(); // show blue at bottom to red at top.            
             var legend = clrScale.data(range)
                .enter().append("li")                    
                    .style("background-color", function(d, i){return range[i];} )
                    .html('&nbsp;&nbsp;&nbsp;');
        }
        
        var width=900;
        var height = width*3.0/4.0;
        // Show the tag cloud for keywords
        var keywordsAndFreq = ${ tagcld.getTagCloudJSON(filterFunc=KeywordFilter)};        
        drawTagCloud(keywordsAndFreq, "#keyword",width, height);
        // Show the tag cloud for names (class names, function names and variable names)
        var namesAndFreq = ${ tagcld.getTagCloudJSON(filterFunc=NameFilter) }    ;        
        drawTagCloud(namesAndFreq, "#names",width, height);
        // Show the tag cloud for class names and function names only
        var classNamesAndFreq = ${ tagcld.getTagCloudJSON(filterFunc=ClassFuncNameFilter) };        
        drawTagCloud(classNamesAndFreq, "#classnames",width, height);
        
        var clrScaleDivs = d3.select('body').selectAll('.colorscale');
        drawColorScale(clrScaleDivs, fill);
        
      </script>

    </body>
    </html>
    '''    

class NameTokenizer(SourceCodeTokenizer):
    '''
    tokenize to return only the class names from the source file
    '''
    def __init__(self, srcfile):
        super(NameTokenizer, self).__init__(srcfile)
        
    def ignore_type(self, ttype,value):
        ignore = False
        if(ttype in Token.Comment ):
            ignore=True
        if( ttype not in  Token.Name):
            ignore = True        
        return(ignore)


class ClassCoOccurMatrix(object):
    '''
    Generate Class Co-occurance matrix in HTML format
    '''    
    def __init__(self, dirname, pattern):
        self.dirname = dirname
        self.pattern = pattern
        self.ccom = dict()
        self.file_tokens = dict()
        self.class_tokens = set()
        self.create()

    def getCooccuranceData(self):
        '''
        create a co-occurance data in nodes and links list format. Something that can be
        dumped to json quickly
        '''
        groups = dict() #key = directory name, value = index
        nodes = dict() # key = classname, value = index
        links = dict() #key (classname1, classname2), value = number of ocurrances

        #add group (directory of the file) into the groups list
        def addGroup(filename):
            dir = os.path.dirname(filename)
            if dir not in groups:
                groups[dir] = len(groups)

        #add file into file list
        def addNode(classname):            
            addGroup(classname)
            if classname not in nodes:
                nodes[classname] = len(nodes)
        
        #add a link (co-occurance) between two classnames into links list.
        def addLink(cname1, cname2):
            if cname1 > cname2:
                cname1,cname2 = cname2, cname1
            addNode(cname1)
            addNode(cname2)
            links[(cname1,cname2)] = {'count': self.ccom[(cname1,cname2)]}
                           
        for co_pair, count in self.ccom.iteritems():
            addLink(co_pair[0], co_pair[1])

        #the child folders should be near to each other. Hence reindex of groups list again.
        groupslist = sorted(groups.keys())
        for i, grp in enumerate(groupslist):
            groups[grp] = i

        return groups, nodes, links
                                
    def create(self):
        flist = GetDirFileList(self.dirname)    
        #first add all names into the set
        for fname in flist:
            if fnmatch.fnmatch(fname,self.pattern):
                self.__addFile(fname)
        #now detect class names and create co occurance matrix
        for srcfile, names in self.file_tokens.iteritems():
            names = names & self.class_tokens

            for cname1, cname2 in itertools.permutations(names, 2):
                self.addPair(cname1, cname2)

    def addPair(self, classname1, classname2):
        '''
        add the co-occuring pair.
        '''
        if classname1 > classname2:
            classname1, classname2 = classname2, classname1
        name_tupple = (classname1, classname2)

        self.ccom[name_tupple] = self.ccom.get(name_tupple, 0)+1
        
    def __addFile(self, srcfile):        
        print "Adding class names information of file: %s" % srcfile

        #create a list of classnames and keep it in classnames set
        names = set()

        tokenizer = NameTokenizer(srcfile)
        
        for ttype, value in tokenizer:
            value =value.strip()
            names.add(value)
            if ttype in Token.Name.Class:
                self.class_tokens.add(value)
            
        self.file_tokens[srcfile] = names

def RunMain():
    usage = "usage: %prog [options] <directory name>"
    description = '''Class Co Ocurrence Matrix (CCOM) (C) Nitin Bhide
    Class Co Ocurrence Matrix the source code files and displays a co-occurance matrix of class names that occur in one
    file
    The color of matrix cell is based on number of times the classes occur together
    Only the statically typed languages are supported (C#, C++, C, etc)
    '''
    parser = OptionParser(usage,description=description)

    parser.add_option("-p", "--pattern", dest="pattern", default='*.c',
                      help="create tag cloud of files matching the pattern. Default is '*.c' ")
    parser.add_option("-o", "--outfile", dest="outfile", default=None,
                      help="outfile name. Output to stdout if not specified")
    
    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        parser.error( "Invalid number of arguments. Use ccom.py --help to see the details.")
    else:        
        dirname = args[0]
            
        ccom = ClassCoOccurMatrix(dirname, options.pattern)
        jsdir = getJsDirPath()
        
        with FileOrStdout(options.outfile) as outf:
            #read the text of d3js file
            d3jstext = readJsText(jsdir, ["d3js", "d3.min.js"]);
            #outf.write(OutputCCOM(ccom,d3jstext))
                
        
if(__name__ == "__main__"):
    RunMain()
    
    