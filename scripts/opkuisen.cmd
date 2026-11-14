@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Generieke opkuiser (herkomstanalyse + inhoud; optioneel layout).
REM Niet in check/build/serve. Help = Python argparse (één bron van waarheid).

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
if "%~1"=="" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\opkuisen.py %*
exit /b %ERRORLEVEL%

:usage
python scripts\opkuisen.py -h
if /I "%~1"=="-h" exit /b 0
if /I "%~1"=="--help" exit /b 0
endlocal
exit /b 2
