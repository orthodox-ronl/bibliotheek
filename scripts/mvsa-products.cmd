@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\sync_mvsa_products.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\mvsa-products.cmd [args...]
echo.
echo   Korte hulp via Python ^(argparse^). Voorbeeldopties vaak: [pad] --dry-run --force
echo.
python scripts\sync_mvsa_products.py -h
endlocal
exit /b %ERRORLEVEL%
