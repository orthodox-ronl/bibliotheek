@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\lifecycle_grenzen.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\lifecycle-grenzen.cmd [--fail]
echo.
echo   Controleert of catalogus-mappen geen werkbank-rommel bevatten
echo   (spaties in namen, .cap/.capx, kale .mxl).
echo   Default: meldt en exit 0. Met --fail: exit 1 bij problemen.
echo.
echo Handleiding: content-source\handleiding\start\levenscyclus.md
echo Man-page: content-source\handleiding\scripts\lifecycle-grenzen.md
echo.
endlocal
exit /b 2
