@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Bibliotheek-id in basispartituur-.mscz colofon zetten of controleren.

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1
python scripts\ensure_bibliotheek_id.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\ensure-bibliotheek-id.cmd [root] [--check-only] [--fail]
echo.
echo   Zet of herstelt Bibliotheek-id in basispartituur-.mscz onder bibliotheek/.
echo   Zonder root: content-source\bibliotheek.
echo   Daarna mscz-products voor verse PDF's.
echo.
echo Handleiding: content-source\handleiding\scripts\ensure-bibliotheek-id.md
echo.
endlocal
exit /b 2
