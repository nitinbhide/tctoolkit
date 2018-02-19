@echo off
REM Creating binrary and source distribution of SVNPlot
del /s /q .\build\*
del manifest
echo "Creating Thinking Craftsman Toolkit source distribution in zip format"
py -2 setup.py sdist --formats=zip
echo "Creating Windows installer for Thinking Craftsman Toolkit "
py -2 setup.py bdist_wininst

