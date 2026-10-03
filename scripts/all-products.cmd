@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage

REM Alias: alle product-kinds. Zelfde opties als products.cmd.
REM Voorkeur voor nieuwe docs: scripts\products.cmd --kinds all

call scripts\products.cmd --kinds all %*
exit /b %ERRORLEVEL%

:usage
echo.
echo Gebruik: scripts\all-products.cmd [opties]
echo.
echo   Alias voor: scripts\products.cmd --kinds all
echo   Zelfde opties als products ^(bijv. --dry-run, --force^).
echo.
echo Handleiding: content-source\handleiding\scripts\all-products.md
echo.
endlocal
exit /b 0