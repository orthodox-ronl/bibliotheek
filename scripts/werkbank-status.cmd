@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

python scripts\werkbank_status.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\werkbank-status.cmd [--quiet]
echo.
echo   Toont open werkbank-cases (werkvoorraad niet-gepubliceerd, stubs
echo   zonder canonieke bron, lokale input\_werk-mappen).
echo   Schrijft data\werkbank-status.json (special page Werkbank).
echo   update-werkvoorraad / check / build / serve doen --quiet ook.
echo.
echo Handleiding: content-source\handleiding\start\werkbank.md
echo Man-page: content-source\handleiding\scripts\werkbank-status.md
echo.
endlocal
exit /b 2
