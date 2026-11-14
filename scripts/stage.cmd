@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

REM Stage alleen gewijzigde bronnen onder catalogus + koormappen
REM (geen afgeleiden). Help = Python argparse.

python scripts\stage_sources.py %*
exit /b %ERRORLEVEL%

:usage
python scripts\stage_sources.py -h
endlocal
exit /b %ERRORLEVEL%
