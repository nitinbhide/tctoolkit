@echo off
REM Creating binrary and source distribution of SVNPlot
echo "Creating Thinking Craftsman Toolkit source distribution in zip format"
setup.py sdist --formats=zip
echo "Creating Windows installer for Thinking Craftsman Toolkit "
setup.py bdist_wininst

