'''
setup.py
Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com)

This module is part of Thinking Craftsman Toolkit (TC Toolkit).
and is released under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
--------------------------------------------------------------------------------------
Setup file for installing Thinking Craftsman Toolkit
'''

from distutils.core import setup

setup(name='TCToolkit', version ='0.5.3',
      description='python module to analyze source code in various ways',
      author='Nitin Bhide',
      author_email='nitinbhide@gmail.com',
      license = 'http://www.opensource.org/licenses/bsd-license.php',
      url='http://code.google.com/p/tctoolkit',
      requires = ['pygments'],
      packages=['tctoolkit', 'tctoolkit.codedupdetect','tctoolkit.tctoolkitutil', 'tctoolkit.tokentagcloud'],
      package_dir = {'': '.'},
      package_data= {'tctoolkit':['README.htm']}
     )
