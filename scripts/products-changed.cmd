@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

REM Alleen producten/pdf voor git-gewijzigde bronnen (missing+stale).
REM Voorbeelden:
REM   scripts\products-changed.cmd --dry-run
REM   scripts\products-changed.cmd
REM   scripts\products-changed.cmd --since-main --dry-run

call scripts\_ensure.cmd --vsa-tool
if errorlevel 1 exit /b 1

python scripts\products_changed.py %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\products-changed.cmd [--dry-run] [--since-main^|--since-development^|--base REF] [--force] [-y]
echo.
echo   Alleen catalogus-producten + koormap-index.md.pdf voor bestanden
echo   die in git gewijzigd zijn onder content-source ^(default: t.o.v. HEAD^).
echo   Condities: missing + stale ^(geen invalid^).
echo.
echo   Eerst kijken:  scripts\products-changed.cmd --dry-run
echo   t.o.v. development:  scripts\products-changed.cmd --since-development --dry-run
echo   t.o.v. main:         scripts\products-changed.cmd --since-main --dry-run
echo.
python scripts\products_changed.py -h
endlocal
exit /b %ERRORLEVEL%
