@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Basispartituur-standaard (layoutprofiel partituur) op .mscz of .mxl.
REM Dunne wrapper om VSA-tooling; zie scripts\apply_mscz_layout.py
REM Help = Python argparse (één bron van waarheid).

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
if "%~1"=="" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\apply_mscz_layout.py %*
exit /b %ERRORLEVEL%

:usage
python scripts\apply_mscz_layout.py -h
if /I "%~1"=="-h" exit /b 0
if /I "%~1"=="--help" exit /b 0
endlocal
exit /b 2
