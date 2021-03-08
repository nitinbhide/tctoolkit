'''
Token Tag Cloud (TTC)
Create tag cloud of tokens used in source files. Tag size is based on the number of times token is used
and tag color is based on the type of token.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit

'''

import string
import sys
import json
import html
import pandas as pd
from pygments.lexers import get_lexer_by_name
from optparse import OptionParser
from .thirdparty.templet import unicodefunction
from .tokentagcloud.tokentagcloud import *
from .tctoolkitutil import readJsText, getJsDirPath, FileOrStdout
from .tctoolkitutil import TCApp
import sqlite3,os,codecs
from pathlib import Path

@unicodefunction
def OutputTagCloud(tagcld, d3js_text, d3cloud_text):
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
        <h2 align="center">Class Names Tag Cloud</h2>
        <div>
            <div class="colorscale"></div>
            <div id="classnames" class="tagcloud"></div>
        </div>
    </div>
    <hr/>
    <div>
        <h2 align="center">Function Name Tag Cloud</h2>
        <div>
            <div class="colorscale"></div>
            <div id="functionnames" class="tagcloud"></div>
        </div>
    </div>    
    <hr/>
    <div>
        <h2 align="center">Strings and Literals</h2>
        <div>
            <div class="colorscale"></div>
            <div id="literals" class="tagcloud"></div>
        </div>
    </div>    
    <hr/>
    <div id="colorscale">
    </div>
    <div class="tooltip" style=""visibility:hidden">
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
            var minFreq = d3.min(wordsAndFreq, function(d) { return d.count});
            var maxFreq = d3.max(wordsAndFreq, function(d) { return d.count});

            var fontSize = d3.scale.log();
            fontSize.domain([minFreq, maxFreq]);
            fontSize.range([5,100])
            // color is calculated based on how many files the word is found
            minColor = d3.min(wordsAndFreq, function(d) { return d.filecount});
            maxColor = d3.max(wordsAndFreq, function(d) { return d.filecount});
            var step = (Math.log(maxColor+1)-Math.log(minColor))/colors.length;            
            fill.domain(d3.range(Math.log(minColor), Math.log(maxColor+1), step));

            d3.layout.cloud().size([width, height])
                .words(wordsAndFreq)
                .padding(5)            
                .font("Impact")
                .rotate(function() { return 0})
                .fontSize(function(d) { return fontSize(+d.count); })
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
                  .style("font-size", function(d) { return fontSize(+d.count)+ "px"; })
                  .style("font-family", "Impact")
                  .style("fill", function(d, i) {
                    return fill(Math.log(d.filecount)); })
                  .attr("text-anchor", "middle")
                  .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                   })
                  .text(function(d) { return d.text;})
                  .on("mouseover", mouseover)
                  .on("mouseout", mouseout)                    
                  .on("mousemove", function(){return tooltip.style("top", (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");});
            }

            // Prepare the tooltip
            var tooltip = d3.select(".tooltip");
              function setTooltipText(d) {                    
                    var tooltiphtml = "<ul><li>"+d.count+" occurrences</li>"+
                        "<li>in "+ d.filecount +" files.</li></ul>";

                    tooltip.html(tooltiphtml);
                    tooltip.style("visibility", "visible");
              }

              function mouseover(p) {                
                setTooltipText(p);
              }

              function mouseout() {
                tooltip.style("visibility", "hidden");
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
        var keywordsAndFreq = ${ tagcld.getJSON(filterFunc=KeywordFilter)};        
        drawTagCloud(keywordsAndFreq, "#keyword",width, height);
        // Show the tag cloud for class names 
        var classnamesAndFreq = ${ tagcld.getJSON(filterFunc=ClassNameFilter) }    ;        
        drawTagCloud(classnamesAndFreq, "#classnames",width, height);
        // Show the tag cloud for function names only
        var funcNamesAndFreq = ${ tagcld.getJSON(filterFunc=FuncNameFilter) };        
        drawTagCloud(funcNamesAndFreq, "#functionnames",width, height);

        var literalsAndFreq = ${ tagcld.getJSON(filterFunc=LiteralFilter) };        
        drawTagCloud(literalsAndFreq, "#literals",width, height);

        var clrScaleDivs = d3.select('body').selectAll('.colorscale');
        drawColorScale(clrScaleDivs, fill);

      </script>

    </body>
    </html>
    '''


class D3SourceTagCloud(SourceCodeTagCloud):

    '''
    Generate source code tag cloud in HTML format
    '''

    def __init__(self, dirname, pattern='*.c', lang=None):
        self.conn = sqlite3.connect("ttc.db")
        self.c = self.conn.cursor()
        super(D3SourceTagCloud, self).__init__(dirname, pattern, lang)
    def javascript(self,name):
        if(self.dirname.endswith(os.sep) == False):
            self.dirname += os.sep
        filelister = DirFileLister(self.dirname)
        filelist = filelister.getFilesForLang(self.lang)
        nameset=set()
        for srcfile in filelist:
            prev=''
            with codecs.open(srcfile, "rb", encoding='utf-8', errors='ignore') as code:
                for ttype, value in get_lexer_by_name(self.lang).get_tokens(code.read()):
                    if name == 'class':
                        if ttype in Token.Name and prev.lower() in ['class', 'new']:
                            if value not in nameset: nameset.add(value)
                    elif name == 'func':
                        if ttype in Token.Name and prev.lower() == 'function':
                            if value not in nameset: nameset.add(value)
                    if ttype not in Token.Text: prev = value
        return nameset
    def inserttotable(self,taglist):
        self.c.execute(""" CREATE TABLE IF NOT EXISTS TagCloud(Text text,Count integer ,
        Filecount integer,UNIQUE(Text,Count,Filecount))""")
        self.conn.commit()
        for i in range(len(taglist)):
            try:
                self.c.execute('''INSERT INTO TagCloud VALUES(?,?,?)''',
                        (taglist[i]['text'], taglist[i]['count'], taglist[i]['filecount']))
            except:pass
        self.conn.commit()
        print(pd.read_sql_query("SELECT * FROM TagCloud", self.conn))

    def getJSON(self, numWords=100, filterFunc=None):
        tagJsonStr = ''
        classset = set()
        funcset=set()
        if self.lang in ['js', 'ts', 'typescript', 'javascript']:
            if filterFunc==ClassNameFilter:
                classset = self.javascript('class')
            elif filterFunc == FuncNameFilter:
                funcset = self.javascript('func')
        tagWordList = self.getTags(numWords, filterFunc,classset,funcset)
        # create list of dictionaries them dump list using json.dumps
        tagList = []

        if(len(tagWordList) > 0):
            # change the font size between "-2" to "+8" relative to current
            # font size
            tagList = [{'text': html.escape(w), 'count': freq, 'filecount': self.getFileCount(
                w)} for w, freq in tagWordList]
        tagJsonStr = json.dumps(tagList)
        if tagList:
            self.inserttotable(tagList)
        # print(tagJsonStr)
        return(tagJsonStr)


class TTCApp(TCApp):

    '''
    Token Tag Cloud application.
    Generate 'tag' cloud of tokens (function names, class names, language keywords etc) from
    various source code files.
    size of token : defines the number of times the token occurs.
    colour of token : defines the number of files the token occurs.
    '''

    def __init__(self, optparser):
        super(TTCApp, self).__init__(optparser, min_num_args=1)

    def _run(self):
        self.dirname = self.args[0]
        tagcld = D3SourceTagCloud(
            self.dirname, pattern=self.pattern, lang=self.lang)
        jsdir = getJsDirPath()
        with FileOrStdout(self.outfile) as outf:
            # read the text of d3js file
            d3jstext = readJsText(jsdir, ["d3js", "d3.min.js"])
            d3cloud_text = readJsText(jsdir, ["d3js", "d3.layout.cloud.js"])
            outf.write(OutputTagCloud(tagcld, d3jstext, d3cloud_text))
        


def RunMain():
    usage = "usage: %prog [options] <directory name>"
    description = '''Token Tag Cloud (C) Nitin Bhide
    Token Tag cloud parses the source code files and displays three tag clouds.
    (1) Tag cloud of keyword
    (2) Tag cloud of class names and variable names
    (3) Tag cloud of class names and function names    
    The size of word is based on total number of occurances of that 'token' in the various source code files
    The color of word is based on number of files that 'token' is found.
    '''
    parser = OptionParser(usage, description=description)

    app = TTCApp(parser)
    app.run()

if(__name__ == "__main__"):
    RunMain()
