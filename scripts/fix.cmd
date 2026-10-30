@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

REM Afwerklijst uit check: tonen of uitvoeren.
REM Voorbeelden:
REM   scripts\fix.cmd --dry-run
REM   scripts\fix.cmd --check --dry-run
REM   scripts\fix.cmd --check
REM   scripts\fix.cmd -y

python scripts\fix.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\fix.cmd [--check] [--dry-run] [-y] [--verbose]
echo.
echo   Werkt data\check-fixlist.json af ^(elke regel = fix_cmd uit check^).
echo   --dry-run   toon de lijst, fix niets
echo   --check     eerst check --strict ^(lijst vernieuwen^), daarna tonen/fixen
echo.
echo Handleiding: content-source\handleiding\scripts\fix.md
echo.
python scripts\fix.py -h
endlocal
exit /b %ERRORLEVEL%
