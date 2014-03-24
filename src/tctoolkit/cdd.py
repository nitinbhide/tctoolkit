'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import sys
import logging

import string, os, datetime
import json
from optparse import OptionParser

from pygments import highlight
from pygments.formatters import HtmlFormatter

from tctoolkitutil import *
from thirdparty.templet import *
from codedupdetect import CodeDupDetect

class HtmlWriter(object):
    '''
    class to output the duplication information in html format
    '''
    def __init__(self, cddapp):
        self.cddapp = cddapp
        self.formatter = HtmlFormatter(encoding='utf-8')

    def getCssStyle(self):
        return self.formatter.get_style_defs('.highlight')

    def getMatches(self):
        return self.cddapp.getMatches()

    def write(self, fname):
        with open(fname, "w") as outf:
            outf.write(self.output())

    def getCooccuranceData(self):
        '''
        create a co-occurance data in JSON format.
        '''
        groups, nodes, links = self.cddapp.getCooccuranceData()
        nodelist = [None]* len(nodes)
        linklist = list()
        #create a list of node dictionaries
        assert(len(nodelist) == len(nodes))
        grouplist = [None]*len(groups)

        for group, index in groups.iteritems():
            grouplist[index] = group
            
        for node, index in nodes.iteritems():
            groupname = os.path.dirname(node)
            nodelist[index] = {'name':os.path.basename(node), 'group':groups[groupname], 'fullpath':node}
        #create a list of link dictionaries
        for link, value in links.iteritems():
            source = link[0]
            target = link[1]
            linklist.append({ 'source':nodes[source], 'target':nodes[target], 'value':value})

        return json.dumps({ 'groups': grouplist, 'nodes':nodelist, 'links' : linklist})

    @stringfunction
    def outputCooccurenceMatrix(self):
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
              var groups = cooc_mat.groups;

              // Compute index per node.
              nodes.forEach(function(node, i) {
                node.index = i;
                node.count = 0;
                matrix[i] = d3.range(n).map(function(j) { return {x: j, y: i, z: 0}; });
              });

              // Convert links to matrix; count character occurrences.
              var maxLinkValue = 0;
              cooc_mat.links.forEach(function(link) {
                var lines = link.value.lines;
                matrix[link.source][link.target].z = lines;                
                matrix[link.target][link.source].z = lines;                
                nodes[link.source].count += lines;
                nodes[link.target].count += lines;
                maxLinkValue = d3.max([maxLinkValue, lines]);
              });

              // update the color scale domain.
              var step = (Math.log(maxLinkValue+1) - 0)/(1.0*colors.length);
              z.domain(d3.range(0, Math.log(maxLinkValue+1),step));

              // Precompute the orders.
              var orders = {
                name: d3.range(n).sort(function(a, b) { return d3.ascending(nodes[a].name, nodes[b].name); }),
                count: d3.range(n).sort(function(a, b) { return nodes[b].count - nodes[a].count; }),
                group: d3.range(n).sort(function(a, b) { return nodes[b].group - nodes[a].group; })
              };

              // The default sort order.
              x.domain(orders.group);

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
                    var tooltiphtml = "<ul><li>Column : "+groups[node1.group]+'/'+node1.name+"</li>"+
                        "<li>Row : "+groups[node2.group]+'/'+node2.name + "</li>"+
                        "<li>Lines:"+d.z+"</li></ul>";

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

                rowtitles.transition().duration(2500)
                    .attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
                columntitles.transition().duration(2500)
                    .attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-45)"; });
              }
              
              order("group");
            };

            //duplication co-occurance data
            var dupData = ${self.getCooccuranceData()};
            drawCooccurrence(dupData);            
        '''
        #duplication co-occurance matrix data.
        # similar to http://bost.ocks.org/mike/miserables/

    @stringfunction
    def output(self):
        '''<!DOCTYPE html>
        <html>
            <head>
                <meta http-equiv="content-type" content="text/html;charset=utf-8">
                <style type="text/css">${self.getCssStyle()}</style>
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
                <script >
                    ${self.getD3JS()}
                </script>
            </head>
            <body>
                <div>
                 ${[self.getMatchLink(i, match) for i, match in enumerate(self.getMatches())]}
                </div>
                <div style="margin-top:10px">Goto <a href="#dup_co_ocm">Duplication Cooccurance Matrix</a></div>
                <div style="margin-top:10px">
                    ${[self.getMatchHtml(i, match) for i, match in enumerate(self.getMatches())]}
                </div>
                <div id="dup_co_ocm">
                    <h1>Duplication Cooccurance Matrix</h1>
                    <div id="co_ocm">                    
                    </div>
                </div>                
            </body>
            <script>
            ${self.outputCooccurenceMatrix()}
            </script>
        </html>
        '''
    
    @stringfunction
    def getMatchLink(self, i, matchset):
        '''<a href="#match_$i">Match ${i+1}&nbsp;</a>'''

    @stringfunction
    def getMatchHtml(self, i, matchset):
        '''<div id="match_$i">
                <h1>MATCH ${i+1}</h1>
               <ul>
               ${[self.getMatchInfo(m) for m in matchset]}
               </ul>
               <div class="highlight">               
                    ${self.getSyntaxHighlightedSource(matchset)}
                    <a href="#">Up</a>
               </div>
           </div>
        '''

    @stringfunction
    def getMatchInfo(self, match):
        '''<li>${match.srcfile()}:${match.getStartLine()}-${match.getStartLine()+match.getLineCount()}</li>'''

    def getSyntaxHighlightedSource(self, matchset):                
        return  highlight(''.join(matchset.getMatchSource()),matchset.getSourceLexer(), self.formatter, outfile=None)
    
    def getD3JS(self):
        jsdir = getJsDirPath()
        return readJsText(jsdir, ["d3js", "d3.min.js"]);

class CDDApp(object):
    def __init__(self, dirname, options):
        self.dirname=dirname
        self.options = options
        self.filelist = None
        self.matches = None
        self.dupsInFile = None

    def getFileList(self):
        if( self.filelist == None):
            filelister = DirFileLister(self.dirname)
            if( self.options.lang != None):
                self.filelist = filelister.getFilesForLang(self.options.lang)
            if( self.options.pattern ==''):
                self.filelist = filelister.getPygmentsFiles()
            else:
                self.filelist = filelister.getMatchingFiles(self.options.pattern)                
                
        return(self.filelist)

    def run(self):
        filelist = self.getFileList()        
        self.cdd = CodeDupDetect(filelist,self.options.minimum, fuzzy=self.options.fuzzy, min_lines=self.options.min_lines)
        
        if self.options.format.lower() == 'html':
            #self.cdd.html_output(self.options.filename)
            htmlwriter = HtmlWriter(self)            
            htmlwriter.write(self.options.filename)

        else:
            #assume that format is 'txt'.
            self.printDuplicates(self.options.filename)
            
        if self.options.comments:
            self.cdd.insert_comments(self.dirname)        
        
    def printDuplicates(self, filename):
        with FileOrStdout(filename) as output:
            exactmatch = self.cdd.printmatches(output)
            tm2 = datetime.datetime.now()            

    def foundMatches(self):
        '''
        return true if there is atleast one match found.
        '''
        matches = self.getMatches()
        return( len(matches) > 0)        
            
    def getMatches(self):
        if( self.matches == None):
            exactmatches = self.cdd.findcopies()
            self.matches = sorted(exactmatches,reverse=True,key=lambda x:x.matchedlines)
        return(self.matches)
    
    def getCooccuranceData(self):
        return self.cdd.getCooccuranceData(self.dirname)

                                  
def RunMain():
    usage = "usage: %prog [options] <directory name>"
    description = """Code Duplication Detector. (C) Nitin Bhide nitinbhide@thinkingcraftsman.in
    Uses RabinKarp algorithm for finding exact duplicates. Fuzzy duplication detection support is
    experimental.
    """
    parser = OptionParser(usage,description=description)

    parser.add_option("-p", "--pattern", dest="pattern", default='',
                      help="find duplications with files matching the pattern")
    parser.add_option("-c", "--comments", action="store_true", dest="comments", default=False,
                      help="Mark duplicate patterns in-source with c-style comment.")
    parser.add_option("-r", "--report", dest="report", default=None,
                      help="Output html to given filename.This is essentially combination '-f html -o <filename>")
    parser.add_option("-o", "--out", dest="filename", default=None,
                      help="output file name. This is simple text file")
    parser.add_option("-f", "--fmt", dest="format", default=None,
                      help="output file format. If not specified, determined from outputfile extension. Supported : txt, html")
    parser.add_option("-m", "--minimum", dest="minimum", default=100, type="int",
                      help="Minimum token count for matched patterns.")
    parser.add_option("", "--lines", dest="min_lines", default=3, type="int",
                      help="Minimum line count for matched patterns.")
    parser.add_option("-z", "--fuzzy", dest="fuzzy", default=False, action="store_true",
                      help="Enable fuzzy matching (ignore variable names, function names etc).")
    parser.add_option("-g", "--log", dest="log", default=False, action="store_true",
                      help="Enable logging. Log file generated in the current directory as cdd.log")
    parser.add_option("-l", "--lang", dest="lang", default=None,
                      help="programming language. Pattern will be ignored if language is defined")
    
    (options, args) = parser.parse_args()

    
    if options.report != None:
        options.format = 'html'
        options.filename = options.report

    if options.format == None:
        #auto detect the format based on the out file extension.
        options.format = 'txt'
        if options.filename:
            name, ext = os.path.splitext(options.filename)
            if ext in set(['.html', '.htm', '.xhtml']):
                options.format = 'html'

    if( len(args) < 1):
        print "Invalid number of arguments. Use cdd.py --help to see the details."
    else:
        if options.log == True:
            logging.basicConfig(filename='cdd.log',level=logging.INFO)
            
        dirname = args[0]
        app = CDDApp(dirname, options)
        with TimeIt(sys.stdout, "Time to calculate the duplicates") as timer:
            app.run()
            
if(__name__ == "__main__"):    
    RunMain()
    