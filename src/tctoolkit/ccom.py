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
import json

from optparse import OptionParser

from pygments.token import Token

from thirdparty.templet import stringfunction

from tctoolkitutil import readJsText,getJsDirPath
from tctoolkitutil import SourceCodeTokenizer
from tctoolkitutil import GetDirFileList,FileOrStdout

class HtmlCCOMWriter(object):
    '''
    Output html of Co-occurance matrix data.
    '''
    def __init__(self, ccom):
        self.ccom = ccom

    def write(self, fname):
        '''
        write the Cooccurence matrix to html file <fname>
        '''
        with FileOrStdout(fname) as outf:
            jsdir = getJsDirPath()
            #read the text of d3js file
            d3jstext = readJsText(jsdir, ["d3js", "d3.min.js"]);
            outf.write(self.outputHtml(d3jstext))

    @stringfunction
    def outputCComScript(self):
        '''
        // Co-occurance matrix
        function drawCooccurrence(cooc_mat) {
            var margin = {top: 100, right: 100, bottom: 10, left: 80};                
            var width = cooc_mat.nodes.length*15;
            var height = width;

            var colors =  ["#a50026", "#d73027","#f46d43","#fdae61","#fee090","#ffffbf",
                        "#e0f3f8","#abd9e9","#74add1","#4575b4","#313695"];
            //console.log(colors);
            colors.reverse();

            var x = d3.scale.ordinal().rangeBands([0, width]),
                z = d3.scale.linear().range(colors),
                c = d3.scale.category10().domain(d3.range(10));
            
            var tooltip = d3.select("body")
                    .append("div")
                    .classed("tooltip", true)
                    .style("visibility", "hidden");
        
            var svg = d3.select("#co_ocm").append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)                
              
              var matrix = [],
                  nodes = cooc_mat.nodes,
                  n = nodes.length;
              
              // Compute index per node.
              nodes.forEach(function(node, i) {
                node.index = i;
                node.count = 0;
                matrix[i] = d3.range(n).map(function(j) { return {x: j, y: i, z: 0}; });
              });

              // Convert links to matrix; count character occurrences.
              var maxLinkValue = 0;
              cooc_mat.links.forEach(function(link) {
                var count = link.value.count;
                matrix[link.source][link.target].z = count;                
                matrix[link.target][link.source].z = count;                
                nodes[link.source].count += count;
                nodes[link.target].count += count;
                maxLinkValue = d3.max([maxLinkValue, count]);
              });

              // update the color scale domain.
              var step = (Math.log(maxLinkValue+1) - 0)/(1.0*colors.length);
              z.domain(d3.range(0, Math.log(maxLinkValue+1),step));

              // Precompute the orders.
              var orders = {
                name: d3.range(n).sort(function(a, b) { return d3.ascending(nodes[a].name, nodes[b].name); }),
                count: d3.range(n).sort(function(a, b) { return nodes[b].count - nodes[a].count; }),
              };

              // The default sort order.
              x.domain(orders.name);

              var rowtitles = svg.append('g')
                .attr("transform", "translate(" + margin.left + ","+margin.top+")")
                .selectAll('.rowtitle')
                    .data(nodes)
                    .enter().append("text")
                      .attr("class", "rowtitle")
                      .attr("x", 6)
                      .attr("y", x.rangeBand() / 2)
                      .attr("text-anchor", "end")
                      .attr("width", margin.left)
                      .text(function(d, i) { return d.name; })
                      .attr("transform", function(d, i) { return "translate(0, "+x(i) + ")"; });

              var columntitles = svg.append('g')
                .attr("transform", "translate(" + margin.left + ","+margin.top+")")                
                .selectAll('.columntitle')
                .data(nodes)
                .enter().append("text")
                  .attr("class", "columntitle")
                  .attr("x", 6)
                  .attr("y", x.rangeBand() / 2)
                  .attr("text-anchor", "start")
                  .text(function(d, i) { return d.name; })
                  .attr("transform", function(d, i) { return "translate(" + x(i) + ",0)rotate(-45)"; });              

              
              svg = svg.append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
                          
              svg.append("rect")
                  .attr("class", "background")
                  .attr("width", width)
                  .attr("height", height);                  

              var row = svg.selectAll(".row")
                  .data(matrix)
                .enter().append("g")
                  .attr("class", "row")
                  .attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
                  .each(row);

              row.append("line")
                  .attr("x2", width);
              
              var column = svg.selectAll(".column")
                  .data(matrix)
                .enter().append("g")
                  .attr("class", "column")
                  .attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });

              column.append("line")
                  .attr("x1", -width);
              
              function row(row) {
                var cell = d3.select(this).selectAll(".cell")
                    .data(row.filter(function(d) { return d.z; }))
                  .enter().append("rect")
                    .attr("class", "cell")
                    .attr("x", function(d) { return x(d.x); })
                    .attr("width", x.rangeBand())
                    .attr("height", x.rangeBand())
                    /*.style("fill-opacity", function(d) { return z(d.z); })*/
                    .style("fill", function(d) { return z(Math.log(d.z));})
                    .on("mouseover", mouseover)
                    .on("mouseout", mouseout)                    
                    .on("mousemove", function(){return tooltip.style("top", (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");});
              }

              // Prepare the tooltip
              function setTooltipText(d) {                    
                    var node1 = nodes[d.x];
                    var node2 = nodes[d.y];
                    var tooltiphtml = "<ul><li>Class 1: "+node1.name+"</li>"+
                        "<li>Class 2: "+node2.name + "</li>"+
                        "<li>Count:"+d.z+"</li></ul>";

                    tooltip.html(tooltiphtml);
                    tooltip.style("visibility", "visible");
              }
                              
              function mouseover(p) {
                d3.selectAll("text.rowtitle").classed("active", function(d, i) {
                 return i == p.y; 
                });
                d3.selectAll("text.columntitle").classed("active", function(d, i) { return i == p.x; });
                setTooltipText(p);
              }

              function mouseout() {
                d3.selectAll("text").classed("active", false);
                tooltip.style("visibility", "hidden");
              }

              d3.select("#order").on("change", function() {
                clearTimeout(timeout);
                order(this.value);
              });

              function order(value) {
                x.domain(orders[value]);

                var t = svg.transition().duration(2500);

                t.selectAll(".row")
                    .delay(function(d, i) { return x(i) * 4; })
                    .attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
                  .selectAll(".cell")
                    .delay(function(d) { return x(d.x) * 4; })
                    .attr("x", function(d) { return x(d.x); });

                t.selectAll(".column")
                    .delay(function(d, i) { return x(i) * 4; })
                    .attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });

                t.selectAll(".rowtitle")
                    .attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
                t.selectAll(".columntitle")
                    .attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-45)"; });
              }
              
              order("name");
            };

            //duplication co-occurance data
            var ccomData = ${self.getCoocurrenceData()};
            drawCooccurrence(ccomData);            
        '''
        #duplication co-occurance matrix data.
        # similar to http://bost.ocks.org/mike/miserables/

    @stringfunction
    def outputHtml(self, d3js_text):
        '''<!DOCTYPE html>
        <html>        
        <head>
        <meta charset="utf-8">
        <style type="text/css">
                #co_ocm {
                    margin-top:20px;
                }
                #co_ocm .background {
                    fill: #eee;
                }

                #co_ocm line {
                    stroke: #fff;
                }

                #co_ocm text.active {
                    fill: red;
                }
                 .tooltip {
                    position:absolute;
                    z-index: 10;
                    background-color:#FFFFF0;
                    padding:3px;
                    border:2px solid #808080;
                }
                .tooltip ul {
                    list-style-type:none;
                    padding:3px;
                    margin:0px;
                }
        </style>
        <script>
            // Embedd the text of d3.js
            $d3js_text
        </script>
        </head>
        <body>
            <div><h1>Class Co occurance Matrix</h1></div>
            <div id="co_ocm"></div>
        </body>
        <script>
            ${self.outputCComScript()}
        </script>
        </html>
        '''

    def getCoocurrenceData(self):
        '''
        return co-occurance data in JSON format.
        '''
        return self.ccom.getJSON()

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
        nodes = dict() # key = classname, value = index
        links = dict() #key (classname1, classname2), value = number of ocurrances

        #add file into file list
        def addNode(classname):            
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

        return nodes, links
                                
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
        '''
        extracted all tokens from a source file and then add it to co-occurence matrix
        '''
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

    def getJSON(self):
        '''
        create a co-occurance data in JSON format.
        '''
        nodes, links = self.getCooccuranceData()
        nodelist = [None]* len(nodes)
        linklist = list()
        #create a list of node dictionaries
        assert(len(nodelist) == len(nodes))
            
        for node, index in nodes.iteritems():
            nodelist[index] = {'name':node}
        #create a list of link dictionaries
        for link, value in links.iteritems():
            source = link[0]
            target = link[1]
            linklist.append({ 'source':nodes[source], 'target':nodes[target], 'value':value})

        return json.dumps({'nodes':nodelist, 'links' : linklist})

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
        writer = HtmlCCOMWriter(ccom)
        writer.write(options.outfile)
        
if(__name__ == "__main__"):
    RunMain()
    
    