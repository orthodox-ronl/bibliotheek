@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
REM Compat-shim: doorsturen naar bieb accepteer
call scripts\bieb.cmd accepteer %*
exit /b %ERRORLEVEL%
