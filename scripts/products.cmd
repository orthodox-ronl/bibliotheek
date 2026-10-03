@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
REM Bibliotheek-producten genereren (recursief onder een map).
REM Voorbeelden:
REM   scripts\products.cmd
REM   scripts\products.cmd content-source\catalogus\trisagion --kinds mscz,audio
REM   scripts\products.cmd --kinds all --dry-run
REM   scripts\products.cmd --kinds mscz,mvsa,vsa
REM     (default: missing + stale + invalid)

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1

python scripts\products.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\products.cmd [args...]
echo.
echo   Korte hulp via Python ^(argparse^). Voorbeeldopties vaak: [pad] --dry-run --force
echo.
python scripts\products.py -h
endlocal
exit /b %ERRORLEVEL%
