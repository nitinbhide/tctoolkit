Thinking Craftman Toolkit (TCToolkit)
=====================================

I am developing various small tools to do some quick code analysis. The project is combination of all such tools and common utilities.

These tools require [Pygments](http://pygments.org/) Python Syntax Highliger.

### Code Duplication Detector(CDD) ###
Code duplication detector is similar to [Copy Paste Detector (CPD)](http://pmd.sourceforge.net/cpd.html) 
or [Simian)(http://www.redhillconsulting.com.au/products/simian/). It uses Pygments Lexer to parse the 
source files and uses Rabin Karp algorithm to detect the duplicates. Hence it supports all languages supported 
by Pygments. 

*Check the CDD results for Apache httpd and Apache Tomcat [here](http://thinkingcraftsman.in/projects/index.htm#tctools).*

You can read more details on [my blog](http://nitinbhide.blogspot.com/2009/06/writing-code-duplication-detector.html) on why I wrote CDD. 

### Token Tag Cloud (TTC) ###
Sometime back I read the blog article ['See How Noisy Your Code Is'](http://fragmental.tw/2009/04/29/tag-clouds-see-how-noisy-your-code-is/). 
TTC is tool for creating various tag clouds based on token types (e.g. keywords, names, classnames etc).

### Treemap Visualization for Source Monitor Metrics data (SMTreemap) ### 

[Source Monitor](http://www.campwoodsw.com/sourcemonitor.html) is an excellent tool to generate various metrics from the source code 
_(e.g. maxium complexity, averge compelxity, line count, block depth etc)_. However, it is difficult to quickly analyse this data 
for large code bases. Treemaps are excellent tool to visualize the hierarchical data on two dimensions (as size and color). This 
tool uses Tkinter to display the SourceMonitor data as treemap. You have to export the source monitor data as CSV or XML. 
smtreemap.py can then use this CSV or XML file as input to display the treemap

