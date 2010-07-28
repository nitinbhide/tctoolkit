@echo off
REM Creating binrary and source distribution of SVNPlot
del manifest
echo "Creating Thinking Craftsman Toolkit source distribution in zip format"
python setup.py sdist --formats=zip
echo "Creating Windows installer for Thinking Craftsman Toolkit "
python setup.py bdist_wininst

