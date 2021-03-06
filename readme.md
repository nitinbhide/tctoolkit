Thinking Craftman Toolkit (TCToolkit)
=====================================

I am developing various small tools to do some quick code analysis. The project is combination of all such tools and common utilities.

These tools require [Pygments](http://pygments.org/) Python Syntax Highliger and use excellent [d3js](http://d3js.org) for visualizations.

### Code Duplication Detector(CDD)
Code duplication detector is similar to [Copy Paste Detector (CPD)](http://pmd.sourceforge.net/cpd.html) 
or [Simian](http://www.redhillconsulting.com.au/products/simian/). It uses Pygments Lexer to parse the 
source files and uses Rabin Karp algorithm to detect the duplicates. Hence it supports all languages supported 
by Pygments. 

*Check the CDD results for Apache httpd and Apache Tomcat [here](http://thinkingcraftsman.in/projects/index.htm#tctools).*

You can read more details on [my blog](http://nitinbhide.blogspot.com/2009/06/writing-code-duplication-detector.html) on why I wrote CDD. 

### Token Tag Cloud (TTC) 
Sometime back I read the blog article ['See How Noisy Your Code Is'](http://fragmental.tw/2009/04/29/tag-clouds-see-how-noisy-your-code-is/). 
TTC is tool for creating various tag clouds based on token types (e.g. keywords, names, classnames etc). Recently I rewrote this script
using d3js library for displaying the token tag cloud.

### Class Cooccurance matrix (CCOM)
This script analyzes the source code and finds class names which are used together. For example, class A has class B as member variable,
or member function of class A uses class B as parameter then class A and B are treated as occuring. If a function takes two parameters
objects class B and class C, then class B and C are treated as 'co-occuring'. If classes are co-occuring, then chances are there is some
dependency between their functionality and hence changes in one MAY impact other.

### Treemap Visualization for Source Monitor Metrics data (SMTreemap)

[Source Monitor](http://www.campwoodsw.com/sourcemonitor.html) is an excellent tool to generate various metrics from the source code 
_(e.g. maxium complexity, averge compelxity, line count, block depth etc)_. However, it is difficult to quickly analyse this data 
for large code bases. Treemaps are excellent tool to visualize the hierarchical data on two dimensions (as size and color). This 
tool uses Tkinter to display the SourceMonitor data as treemap. You have to export the source monitor data as CSV or XML. 
smtreemap.py can then use this CSV or XML file as input to display the treemap. However, smtreemap.py uses tkinter as 'gui' library
for displaying the treemap. If the tkinter is not available then, smtreemap.py will not use. Use smjstreemap in such cases.

smjstreemap.py : use excellent d3js javascript library to create javascript based treemap. smjstreemap.py doesnot require tkinter 
for displaying the treemaps

