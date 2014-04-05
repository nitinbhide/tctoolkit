'''
Class Co Ocurrence Matrix (CCOM)

Create a coocurrance matrix based on which class names a occurring in a file. The class names that occur in
one file are treated as 'co ocurring' classes.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''
import logging
import string
import sys
import itertools
import operator
import fnmatch
import json
import math

from optparse import OptionParser

from pygments.token import Token

from thirdparty.templet import stringfunction

from tctoolkitutil import readJsText,getJsDirPath
from tctoolkitutil import SourceCodeTokenizer
from tctoolkitutil import DirFileLister,FileOrStdout

try:
    #check if the NetworkX is available
    import networkx as nx
except:
    nx = None

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
              var minLinkValue = 999999999;
              cooc_mat.links.forEach(function(link) {
                var count = link.value.count;
                matrix[link.source][link.target].z = count;                
                matrix[link.target][link.source].z = count;                
                nodes[link.source].count += count;
                nodes[link.target].count += count;
                maxLinkValue = Math.max(maxLinkValue, count);
                minLinkValue = Math.min(minLinkValue, count);
              });
              minLinkValue = Math.max(minLinkValue, 1)

              // update the color scale domain.
              var step = (Math.log(maxLinkValue+1) - Math.log(minLinkValue))/(1.0*colors.length);
              z.domain(d3.range(Math.log(minLinkValue), Math.log(maxLinkValue+1),step));

              // Precompute the orders.
              var orders = {
                name: d3.range(n).sort(function(a, b) { return d3.ascending(nodes[a].name, nodes[b].name); }),
                count: d3.range(n).sort(function(a, b) { return nodes[a].count - nodes[b].count; }),
                group:d3.range(n).sort(function(a, b) { 
                    var cmp = nodes[a].group - nodes[b].group; 
                    if (cmp == 0) {
                        cmp = nodes[b].count - nodes[a].count
                    }
                    return cmp;
                }),
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
                    var tooltiphtml = "<ul><li>Column : "+node1.name+"</li>"+
                        "<li>Row : "+node2.name + "</li>"+
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
                
                t = rowtitles.transition().duration(2500);
                t.attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; });

                t = columntitles.transition().duration(2500);                
                t.attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-45)"; });
              }
              
              order("group");
            };

            function updateEdgesToRemoveList(edgesToRemove) {
                // append the list of edges to remove
                var edgeList = d3.select('#edgesToRemove').append('ol');

                    edgeList.selectAll('li')
                        .data(edgesToRemove)
                        .enter().append("li")
                            .text(function(d, i) { return d[0] + " : " + d[1]; });
            }

            //class co-occurance data
            var ccomData = ${self.getCoocurrenceData()};
            drawCooccurrence(ccomData);            
            updateEdgesToRemoveList(ccomData.edgesToRemove);

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
                #edgesToRemove ol {
                    margin-left: 2em;
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
            <div><h1>Suggestions for Dependency Removal</h1></div>
            <div id="edgesToRemove"></div>
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
    def __init__(self, srcfile, lang):
        super(NameTokenizer, self).__init__(srcfile,lang=lang)
        
    def ignore_type(self, srctoken):
        ignore = False
        if(srctoken.is_type(Token.Comment) ):
            ignore=True
        elif( not srctoken.is_type(Token.Name)):
            ignore = True       
        return(ignore)
    
    def update_type(self, srctoken, prevtoken):
        '''
        class name detection only for classes which are declared in the module project.
        For example 'class A: B' -- detect only A as class name and not B. This will ensure
        that system classes (e.g. .Net framework classes) are ignored (most of the time)
        '''
        if srctoken.ttype == Token.Name.Class:
            if not (prevtoken and prevtoken.ttype in Token.Keyword and prevtoken.value == 'class'):
                logging.debug("%s : type reset to name" % srctoken.value)
                srctoken.ttype = Token.Name
            

class ClassCoOccurMatrix(object):
    '''
    Generate Class Co-occurance matrix in HTML format
    '''    
    def __init__(self, dirname, mincoocurrance, lang=None, pattern = '*.c'):
        '''
        mincoocurrance : minimum number of co-cocurrances to consider this in display
        '''
        self.dirname = dirname
        self.pattern = pattern
        self.lang = lang
        self.mincoocurrance = int(mincoocurrance)
        self.ccom = dict()
        self.file_tokens = dict()
        self.class_tokens = set()
        self.edgesToRemove = list()
        self.create()
        self.detectGroups = self.detectGroupsSimple
        if nx:
            #NetworkX is available, use it for detecting groups
            self.detectGroups = self.detectGroupsNX            
            
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
                nodes[classname] = { 'count': 0, 'index' : len(nodes)}
        
        #add a link (co-occurance) between two classnames into links list.
        def addLink(cname1, cname2):
            if cname1 > cname2:
                cname1,cname2 = cname2, cname1
            linkcount = self.ccom[(cname1,cname2)]
            if linkcount > self.mincoocurrance:
                addNode(cname1)
                addNode(cname2)
                links[(cname1,cname2)] = {'count': linkcount}
                nodes[cname1]['count'] = nodes[cname1]['count']+linkcount
                nodes[cname2]['count'] = nodes[cname2]['count']+linkcount
                           
        for co_pair, count in self.ccom.iteritems():
            addLink(co_pair[0], co_pair[1])

        groups = self.detectGroups(nodes, links)
        self._updateGroupIndexInNode(nodes, groups)

        return nodes, links
    
    def detectGroupsNX(self, nodes, links):
        '''
        detect groups using the NetworkX library. It uses a simple algorithm of
        remove "highest between_ness centrality nodes" and then detecting the graph
        split.
        '''
        def make_nx_graph(nodes, links):
            G=nx.Graph()
            G.add_nodes_from(nodes)
            link_tupples = [(node_tupple[0], node_tupple[1], val['count']) for node_tupple, val in links.iteritems()]
            G.add_weighted_edges_from(link_tupples)
            return G

        def calc_betweenness(graph):
            centrality = nx.edge_betweenness_centrality(graph, False)
            centrality = sorted(centrality.iteritems(), key = operator.itemgetter(1), reverse=True)
            return centrality
            
        def calc_average(iter):
            averge = sum(iter) * 1.0 / len(centrality)
            return averge 

        def centrality_stddev(centrality):
            #find the standard deviation of centrality
            count = len(centrality)
            average = 0.0
            std_dev = 0.0
            if count > 0:
                total = sum(itertools.imap(operator.itemgetter(1), centrality)) * 1.0;
                average = total/count
                variance_sum = sum(map(lambda x: (x - average)**2, itertools.imap(operator.itemgetter(1), centrality)))
                std_dev = math.sqrt(variance_sum/count)
            return average, std_dev


        graph = make_nx_graph(nodes, links)
        groups = nx.connected_components(graph)
        
        print "number of groups detected %d" % len(groups)
        centrality = calc_betweenness(graph)
        average, censtddev = centrality_stddev(centrality)
        #remove all the edges with centrality > (average+stddev)
        centrality_maxval = average+(censtddev*1.96)
        edges = [edge_info[0] for edge_info in centrality if edge_info[1] >= centrality_maxval]
        self.edgesToRemove = edges # Store the information about suggested edges to remove
        graph.remove_edges_from(edges)
        print "edges removed %d" % len(edges)
        
        #now extract the groups (or connected components) from the graph.
        groups = nx.connected_components(graph)
        groups = sorted(groups, key=lambda g:len(g), reverse=True)
        print "number of groups detected %d" % len(groups)
        return groups

    def detectGroupsSimple(self, nodes, links):
        '''
        simple group/cluster detection algorithm.
        1. start with node with highest number of links
        2. find all the nodes linked to this node.
        3. these form one group.
        4. Repeat this process
        '''
        #first create a node set for search
        nodeset = set(nodes.iterkeys())
                
        def findMaxCountNode(nodeset):
            maxnode = max(nodeset, key= lambda n: nodes[n]['count'])
            return maxnode

        def findConnectedNode(nodeset, node):
            #find the node connected to 'node', return it.
            for link in links.iterkeys():
                if(link[0] == node and link[1] in nodeset):
                    return link[1]
                if link[1] == node and link[0] in nodeset:
                    return link[0]
            return None

        groups = list()
        
        while len(nodeset) > 0:
            maxnode = findMaxCountNode(nodeset)
            #remove maxnode from nodeset
            nodeset.remove(maxnode)
            #now trace all the nodes connected to this node.
            curgroup = list()
            groups.append(curgroup)
            curgroup.append(maxnode)
            connode = findConnectedNode(nodeset, maxnode)
            while connode != None:
                nodeset.remove(connode)
                curgroup.append(connode)
                connode = findConnectedNode(nodeset, maxnode)
        return groups
        
    def _updateGroupIndexInNode(self, nodes, groups):
        #update the group index in the nodes dictionary
        groupkey = 'group'
        for grpidx, group in enumerate(groups):
            for node in group:
                nodes[node][groupkey] = grpidx
    
    def create(self):
        filelister = DirFileLister(self.dirname)

        #first add all names into the set               
        for fname in filelister.getFilesForPatternOrLang(pattern= self.pattern, lang=self.lang):
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

        tokenizer = NameTokenizer(srcfile, self.lang)
        
        for srctoken in tokenizer:
            value =srctoken.value.strip()
            names.add(value)
            if srctoken.is_type(Token.Name.Class):
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
            
        for node, nodedata in nodes.iteritems():
            nodelist[nodedata['index']] = {'name':node, 'count':nodedata['count'], 'group':nodedata['group']}
        #create a list of link dictionaries
        for link, value in links.iteritems():
            source = link[0]
            target = link[1]
            linklist.append({ 'source':nodes[source]['index'], 'target':nodes[target]['index'], 'value':value})

        return json.dumps({'nodes':nodelist, 'links' : linklist, 'edgesToRemove': self.edgesToRemove})

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
    parser.add_option("-m", "--minimum", dest="mincoocurrance", default=2,type = 'int',
                      help="minimum coocurrance count required")
    parser.add_option("-l", "--lang", dest="lang", default=None,
                      help="programming language. Pattern will be ignored if language is defined")
    
    (options, args) = parser.parse_args()
    
    if( len(args) < 1):
        parser.error( "Invalid number of arguments. Use ccom.py --help to see the details.")
    else:        
        dirname = args[0]
            
        ccom = ClassCoOccurMatrix(dirname, options.mincoocurrance, pattern =options.pattern, lang= options.lang)
        writer = HtmlCCOMWriter(ccom)
        writer.write(options.outfile)
        
if(__name__ == "__main__"):
    RunMain()
    
    