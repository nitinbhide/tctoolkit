@echo off
REM Run autopep8 on all .py files to fix PEP8 formatting errors
set SOURCEDIR=%~dp0
echo Running autopep8 on %SOURCEDIR%
autopep8 --in-place -r %SOURCEDIR%
