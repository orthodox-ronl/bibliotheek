@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM Alias: alle product-kinds. Zelfde opties als products.cmd.
REM Voorkeur voor nieuwe docs: scripts\products.cmd --kinds all …

call scripts\products.cmd --kinds all %*
exit /b %ERRORLEVEL%
