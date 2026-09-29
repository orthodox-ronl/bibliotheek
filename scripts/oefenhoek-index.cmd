@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\sync_oefenhoek_index.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\oefenhoek-index.cmd [--dry-run] [--svg] [--verbose]
echo.
echo   --svg   schrijf SVG uit bibliotheek-.vsa naar static\vsa\bladermap\
echo   Zonder flags: strip legacy widgets uit bladermap-index.md
echo.
echo Handleiding: content-source\handleiding\scripts\oefenhoek-index.md
echo.
endlocal
exit /b 0
